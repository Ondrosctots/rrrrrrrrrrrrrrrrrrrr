import streamlit as st
import requests

# -------------------------
# Streamlit config
# -------------------------
st.set_page_config(
    page_title="Reverb Listing Manager",
    layout="wide"
)

st.title("🎸 Reverb Listing Manager")
st.caption("🔒 Your API token is used only for this session and is never stored.")

# -------------------------
# Token input (ALWAYS REQUIRED)
# -------------------------
token = st.text_input(
    "Reverb API Token",
    type="password",
    placeholder="rbv_XXXXXXXXXXXXXXXX"
)

if not token:
    st.warning("Please enter your Reverb API token to continue.")
    st.stop()

BASE_URL = "https://api.reverb.com/api"

HEADERS = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
    "X-Api-Version": "3"
}

# -------------------------
# Fetch ALL listings (NO PARAMS, TRAILING SLASH)
# -------------------------
@st.cache_data(ttl=60)
def get_all_listings(token):
    response = requests.get(
        f"{BASE_URL}/my/listings/",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "X-Api-Version": "3"
        }
    )

    response.raise_for_status()
    return response.json().get("listings", [])

# -------------------------
# Load listings
# -------------------------
try:
    all_listings = get_all_listings(token)
except Exception as e:
    st.error(f"Failed to fetch listings: {e}")
    st.stop()

# Filter locally
listings = [
    l for l in all_listings
    if l.get("state") in ("draft", "live")
]

st.subheader(f"📦 Your Listings ({len(listings)})")

if not listings:
    st.info("No draft or live listings found.")
    st.stop()

# -------------------------
# Display listings
# -------------------------
for listing in listings:
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([4, 2, 2, 2])

        with col1:
            st.markdown(f"**{listing['title']}**")
            st.caption(f"ID: {listing['id']}")

        with col2:
            st.write(f"State: **{listing['state']}**")

        with col3:
            price = listing.get("price")
            if price:
                st.write(f"{price['amount']} {price['currency']}")

        with col4:
            # Draft → Publish
            if listing["state"] == "draft":
                if st.button("🚀 Publish", key=f"publish_{listing['id']}"):
                    r = requests.post(
                        f"{BASE_URL}/listings/{listing['id']}/publish",
                        headers=HEADERS
                    )
                    if r.status_code == 200:
                        st.success("Listing published successfully.")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(r.text)

            # Live → End
            elif listing["state"] == "live":
                if st.button("⛔ End Listing", key=f"end_{listing['id']}"):
                    r = requests.post(
                        f"{BASE_URL}/listings/{listing['id']}/end",
                        headers=HEADERS
                    )
                    if r.status_code == 200:
                        st.success("Listing ended successfully.")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(r.text)
