import streamlit as st
import requests
import json
from typing import List
from pymongo import MongoClient
from utils.session_manager import save_session
from config import API_BASE_URL, MONGO_URI

def render():
    st.title("Platform Credentials & Posting Options")
    st.write("Provide credentials for auto-posting or opt to receive posts via email.")

    # Debug information
    st.write("Debug: Session state keys:", list(st.session_state.keys()))
    st.write(f"Debug: setup_id = {st.session_state.get('setup_id')}")
    st.write(f"Debug: setup_completed = {st.session_state.get('setup_completed')}")
    
    # Validate setup_id and content schedule
    setup_id = st.session_state.get("setup_id")
    if not setup_id:
        st.error("Setup ID not found. Please complete the setup first.")
        # Add a button to return to setup
        if st.button("⬅️ Return to Setup"):
            st.session_state.page = "Setup"
            save_session()
            st.rerun()
        return
    
    if not st.session_state.get("content_schedule"):
        st.error("Content schedule not found. Please generate a content schedule first.")
        # Add a button to return to content planning
        if st.button("⬅️ Return to Content Planning"):
            st.session_state.page = "Content Planner"
            save_session()
            st.rerun()
        return
    
    # Fetch platforms from setup
    platforms = fetch_platforms(setup_id)
    
    if not platforms:
        st.warning("No platforms found in your setup. Please update your setup with at least one platform.")
        if st.button("⬅️ Return to Setup"):
            st.session_state.page = "Setup"
            save_session()
            st.rerun()
        return
    
    # Create tabs for each platform
    tabs = st.tabs(platforms + ["Email Delivery"])
    
    # Initialize credentials dictionary if not exists
    if "credentials" not in st.session_state:
        st.session_state.credentials = {}
    
    # Platform credential forms
    for i, platform in enumerate(platforms):
        with tabs[i]:
            st.subheader(f"{platform} Credentials")
            
            # Different fields based on platform
            with st.form(key=f"{platform}_form"):
                if platform == "Instagram" or platform == "Facebook":
                    api_key = st.text_input(
                        "API Key/Access Token", 
                        value=st.session_state.credentials.get(platform, {}).get("api_key", ""),
                        type="password"
                    )
                    account_id = st.text_input(
                        "Account ID/Page ID", 
                        value=st.session_state.credentials.get(platform, {}).get("account_id", "")
                    )
                    
                    if st.form_submit_button("Save Credentials"):
                        st.session_state.credentials[platform] = {
                            "api_key": api_key,
                            "account_id": account_id
                        }
                        st.success(f"{platform} credentials saved!")
                        save_session()
                
                elif platform == "Twitter" or platform == "LinkedIn":
                    api_key = st.text_input(
                        "API Key", 
                        value=st.session_state.credentials.get(platform, {}).get("api_key", ""),
                        type="password"
                    )
                    api_secret = st.text_input(
                        "API Secret", 
                        value=st.session_state.credentials.get(platform, {}).get("api_secret", ""),
                        type="password"
                    )
                    access_token = st.text_input(
                        "Access Token", 
                        value=st.session_state.credentials.get(platform, {}).get("access_token", ""),
                        type="password"
                    )
                    access_secret = st.text_input(
                        "Access Secret", 
                        value=st.session_state.credentials.get(platform, {}).get("access_secret", ""),
                        type="password"
                    )
                    
                    if st.form_submit_button("Save Credentials"):
                        st.session_state.credentials[platform] = {
                            "api_key": api_key,
                            "api_secret": api_secret,
                            "access_token": access_token,
                            "access_secret": access_secret
                        }
                        st.success(f"{platform} credentials saved!")
                        save_session()
                
                else:  # Generic form for other platforms
                    api_key = st.text_input(
                        "API Key/Access Token", 
                        value=st.session_state.credentials.get(platform, {}).get("api_key", ""),
                        type="password"
                    )
                    additional_info = st.text_area(
                        "Additional Information", 
                        value=st.session_state.credentials.get(platform, {}).get("additional_info", "")
                    )
                    
                    if st.form_submit_button("Save Credentials"):
                        st.session_state.credentials[platform] = {
                            "api_key": api_key,
                            "additional_info": additional_info
                        }
                        st.success(f"{platform} credentials saved!")
                        save_session()
    
    # Email delivery option
    with tabs[-1]:
        st.subheader("Email Delivery")
        st.write("Receive your content schedule and posts via email.")
        
        with st.form(key="email_form"):
            # Get the email value safely
            current_email = ""
            if "posting_email" in st.session_state:
                current_email = st.session_state.posting_email
            elif "email" in st.session_state:
                current_email = st.session_state.email
            
            posting_email = st.text_input(
                "Email Address", 
                value=current_email,
                placeholder="Enter email to receive content"
            )
            
            delivery_frequency = st.selectbox(
                "Delivery Frequency",
                options=["Send all at once", "Daily digest", "Weekly digest"]
            )
            
            if st.form_submit_button("Save Email Preferences"):
                st.session_state.posting_email = posting_email
                st.success("Email preferences saved!")
                save_session()
    
    # Final submission
    st.divider()
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write("When you're ready, click 'Submit All Credentials' to save your preferences and complete the setup.")
    
    with col2:
        if st.button("Submit All Credentials", type="primary"):
            try:
                # Prepare data for API
                credentials_data = {
                    "email": st.session_state.email,
                    "credentials": st.session_state.credentials,
                    "posting_email": st.session_state.get("posting_email", st.session_state.email)
                }
                
                # Make API request
                with st.spinner("Saving credentials..."):
                    response = requests.post(
                        f"{API_BASE_URL}/store_credentials",
                        json=credentials_data
                    )
                    
                    if response.status_code == 200:
                        st.success("✅ All credentials saved successfully!")
                        st.balloons()
                        
                        # Show completion message
                        st.write("### 🎉 Setup Complete!")
                        st.write("""
                        Your social media content will be posted according to the schedule.
                        You can always come back to update your credentials or content strategy.
                        """)
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

def fetch_platforms(setup_id: str) -> List[str]:
    """Fetch selected platforms directly from MongoDB."""
    try:
        # Debug output to help diagnose the issue
        st.write(f"Debug: Looking for setup with ID: {setup_id}")
        
        client = MongoClient(MONGO_URI)
        db = client["social_media_manager"]
        
        # Try both user_uuid and _id fields
        setup = db.setups.find_one({"user_uuid": setup_id})
        if not setup:
            setup = db.setups.find_one({"_id": setup_id})
        
        # If still not found, try string conversion for ObjectId
        if not setup and len(setup_id) == 24:  # ObjectId is 24 hex chars
            from bson.objectid import ObjectId
            try:
                obj_id = ObjectId(setup_id)
                setup = db.setups.find_one({"_id": obj_id})
            except:
                pass
        
        client.close()
        
        if not setup:
            st.error(f"Setup not found in database with ID: {setup_id}")
            return []
        
        platforms = setup.get("platforms", [])
        st.write(f"Debug: Found platforms: {platforms}")
        return platforms
    except Exception as e:
        st.error(f"Failed to fetch platforms from MongoDB: {str(e)}")
        return []  # Add a return statement here
