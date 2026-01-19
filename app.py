import streamlit as st
import requests
import pandas as pd

# Reverb API base URL
BASE_URL = "https://api.reverb.com/api"

# Function to get listings
def get_listings(api_token, state=None):
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept-Version": "3.0"  # Required for Reverb API v3
    }
    params = {"per_page": 100}  # Adjust as needed
    if state:
        params["state"] = state
    response = requests.get(f"{BASE_URL}/my/listings", headers=headers, params=params)  # Fetch user's own listings
    if response.status_code == 200:
        return response.json()["listings"]
    else:
        st.error(f"Error fetching listings: {response.status_code} - {response.text}")
        return []

# Function to publish a draft listing
def publish_listing(api_token, listing_id):
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept-Version": "3.0"  # Required for Reverb API v3
    }
    url = f"{BASE_URL}/my/listings/{listing_id}/publish"  # Using /my/listings for actions on own listings
    st.write(f"Attempting to publish listing ID {listing_id} at URL: {url}")  # Debug info
    response = requests.put(url, headers=headers)
    if response.status_code == 200:
        st.success("Listing published successfully!")
    else:
        st.error(f"Error publishing listing: {response.status_code} - {response.text}")
        # Additional debug: Show response details
        st.write("Response details:", response.json() if response.headers.get('content-type') == 'application/json' else response.text)

# Function to end a published listing
def end_listing(api_token, listing_id):
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept-Version": "3.0"  # Required for Reverb API v3
    }
    url = f"{BASE_URL}/my/listings/{listing_id}/end"  # Using /my/listings for actions on own listings
    st.write(f"Attempting to end listing ID {listing_id} at URL: {url}")  # Debug info
    response = requests.put(url, headers=headers)
    if response.status_code == 200:
        st.success("Listing ended successfully!")
    else:
        st.error(f"Error ending listing: {response.status_code} - {response.text}")
        # Additional debug: Show response details
        st.write("Response details:", response.json() if response.headers.get('content-type') == 'application/json' else response.text)

# Streamlit UI
st.title("Reverb Listings Manager")

# Input API token
api_token = st.text_input("Enter your Reverb API Token", type="password")

if api_token:
    # Fetch all listings (drafts and published)
    st.header("Your Listings")
    drafts = get_listings(api_token, state="draft")
    published = get_listings(api_token, state="published")
    all_listings = drafts + published
    
    if all_listings:
        # Convert to DataFrame for display
        df = pd.DataFrame([
            {
                "ID": listing["id"],
                "Title": listing["title"],
                "State": listing["state"],
                "Price": listing.get("price", {}).get("amount", "N/A"),
                "Condition": listing.get("condition", {}).get("display_name", "N/A")
            }
            for listing in all_listings
        ])
        st.dataframe(df)
        
        # Action sections
        st.header("Actions")
        
        # Publish a draft
        st.subheader("Publish a Draft Listing")
        draft_options = [f"{listing['id']}: {listing['title']}" for listing in drafts]
        if draft_options:
            selected_draft = st.selectbox("Select a draft to publish", draft_options)
            if st.button("Publish Selected Draft"):
                listing_id = selected_draft.split(":")[0]
                publish_listing(api_token, listing_id)
        else:
            st.info("No draft listings found.")
        
        # End a published listing
        st.subheader("End a Published Listing")
        published_options = [f"{listing['id']}: {listing['title']}" for listing in published]
        if published_options:
            selected_published = st.selectbox("Select a published listing to end", published_options)
            if st.button("End Selected Listing"):
                listing_id = selected_published.split(":")[0]
                end_listing(api_token, listing_id)
        else:
            st.info("No published listings found.")
    else:
        st.info("No listings found.")
else:
    st.info("Please enter your API token to proceed.")
