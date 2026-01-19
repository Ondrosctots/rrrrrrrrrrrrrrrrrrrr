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
    "Accept": "application/hal+json",
    "Accept-Version": "3.0",
    "User-Agent": "Reverb-Streamlit-Manager/1.0"
}

# -------------------------
# Fetch LIVE listings
# -------------------------
def fetch_live_listings():
    r = requests.get(
        f"{BASE_URL}/my/listings",
        headers=HEADERS
    )
    if not r.ok:
        raise Exception(f"Live listings error: {r.text}")
    return r.json().get("_embedded", {}).get("listings", [])

# -------------------------
# Fetch DRAFT listings
# -------------------------
def fetch_draft_listings():
    r = requests.get(
        f"{BASE_URL}/my/listings/drafts",
        headers=HEADERS
    )
    if not r.ok:
        raise Exception(f"Draft listings error: {r.text}")
    return r.json().get("_embedded", {}).get("listings", [])

# -------------------------
# Cached loader (token-scoped)
# -------------------------
@st.cache_data(ttl=60)
def load_all_listings(token):
    live = fetch_live_listings()
    drafts = fetch_draft_listings()
    return live + drafts

# -------------------------
# Load listings
# -------------------------
try:
    listings = load_all_listings(token)
except Exception as e:
    st.error(f"Failed to fetch listings:\n{e}")
    st.stop()

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
            st.markdown(f"**{listing.get('title', 'Untitled draft')}**")
            st.caption(f"ID: {listing['id']}")

        with col2:
            st.write(f"State: **{listing['state']}**")

        with col3:
            price = listing.get("price")
            if price:
                st.write(f"{price['amount']} {price['currency']}")
            else:
                st.write("—")

        with col4:
            # Draft → Publish
            if listing["state"] == "draft":
                if st.button("🚀 Publish", key=f"publish_{listing['id']}"):
                    r = requests.post(
                        f"{BASE_URL}/listings/{listing['id']}/publish",
                        headers=HEADERS
                    )
                    if r.ok:
                        st.success("Listing published.")
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
                    if r.ok:
                        st.success("Listing ended.")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(r.text)
