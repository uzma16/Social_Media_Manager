import streamlit as st
import requests
import json
from utils.session_manager import save_session, update_progress
from config import API_BASE_URL

def render():
    st.title("Brand Setup")
    st.write("Let's set up your brand profile to generate tailored content.")
    
    # Check if setup is already completed
    if st.session_state.setup_completed and st.session_state.setup_id:
        st.success("✅ Setup already completed!")
        
        # Display the existing strategy
        if st.session_state.raw_content:
            st.subheader("Your Content Strategy")
            st.write(st.session_state.raw_content)
        
        # Option to redo setup
        if st.button("Redo Setup"):
            # Reset setup-related session state
            st.session_state.setup_completed = False
            st.session_state.setup_id = None
            st.session_state.brand_guidelines = {}
            st.session_state.goals = ""
            st.session_state.target_audience = {}
            st.session_state.platforms = []
            st.session_state.api_response = None
            st.session_state.raw_content = ""
            save_session()
            st.rerun()
            
        # Navigation button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col3:
            if st.button("➡️ Continue to Content Planning", key="navigate_button"):
                st.session_state.page = "Content Planner"
                save_session()
                st.rerun()
        
        return
    
    # Initialize progress tracking
    update_progress("setup", 0.1)
    
    # Setup form
    with st.form(key="setup_form"):
        st.subheader("Brand Guidelines")
        col1, col2 = st.columns(2)
        
        with col1:
            brand_name = st.text_input("Brand Name", 
                                      value=st.session_state.brand_guidelines.get("brand_name", ""),
                                      placeholder="e.g., Acme Inc.")
            brand_voice = st.text_input("Brand Voice", 
                                       value=st.session_state.brand_guidelines.get("brand_voice", ""),
                                       placeholder="e.g., Professional, Friendly, Innovative")
        
        with col2:
            industry = st.text_input("Industry", 
                                    value=st.session_state.brand_guidelines.get("industry", ""),
                                    placeholder="e.g., Technology, Fashion, Healthcare")
            key_values = st.text_input("Key Values", 
                                      value=st.session_state.brand_guidelines.get("key_values", ""),
                                      placeholder="e.g., Sustainability, Innovation, Quality")
        
        update_progress("setup", 0.3)
        
        st.subheader("Goals")
        goals = st.text_area("What are your social media goals?", 
                            value=st.session_state.goals,
                            placeholder="e.g., Increase brand awareness, Generate leads, Build community",
                            height=100)
        
        update_progress("setup", 0.5)
        
        st.subheader("Target Audience")
        col1, col2 = st.columns(2)
        
        with col1:
            age_range = st.text_input("Age Range", 
                                     value=st.session_state.target_audience.get("age_range", ""),
                                     placeholder="e.g., 25-34")
            interests = st.text_input("Interests", 
                                     value=st.session_state.target_audience.get("interests", ""),
                                     placeholder="e.g., Technology, Travel, Fitness")
        
        with col2:
            location = st.text_input("Location", 
                                    value=st.session_state.target_audience.get("location", ""),
                                    placeholder="e.g., United States, Global")
            pain_points = st.text_input("Pain Points", 
                                       value=st.session_state.target_audience.get("pain_points", ""),
                                       placeholder="e.g., Lack of time, Budget constraints")
        
        update_progress("setup", 0.7)
        
        st.subheader("Platforms")
        col1, col2, col3, col4 = st.columns(4)
        
        platforms = st.session_state.platforms or []
        
        with col1:
            if st.checkbox("Instagram", value="Instagram" in platforms):
                if "Instagram" not in platforms:
                    platforms.append("Instagram")
            else:
                if "Instagram" in platforms:
                    platforms.remove("Instagram")
                    
            if st.checkbox("LinkedIn", value="LinkedIn" in platforms):
                if "LinkedIn" not in platforms:
                    platforms.append("LinkedIn")
            else:
                if "LinkedIn" in platforms:
                    platforms.remove("LinkedIn")
        
        with col2:
            if st.checkbox("Twitter/X", value="Twitter" in platforms):
                if "Twitter" not in platforms:
                    platforms.append("Twitter")
            else:
                if "Twitter" in platforms:
                    platforms.remove("Twitter")
                    
            if st.checkbox("Facebook", value="Facebook" in platforms):
                if "Facebook" not in platforms:
                    platforms.append("Facebook")
            else:
                if "Facebook" in platforms:
                    platforms.remove("Facebook")
        
        with col3:
            if st.checkbox("TikTok", value="TikTok" in platforms):
                if "TikTok" not in platforms:
                    platforms.append("TikTok")
            else:
                if "TikTok" in platforms:
                    platforms.remove("TikTok")
                    
            if st.checkbox("YouTube", value="YouTube" in platforms):
                if "YouTube" not in platforms:
                    platforms.append("YouTube")
            else:
                if "YouTube" in platforms:
                    platforms.remove("YouTube")
        
        with col4:
            if st.checkbox("Pinterest", value="Pinterest" in platforms):
                if "Pinterest" not in platforms:
                    platforms.append("Pinterest")
            else:
                if "Pinterest" in platforms:
                    platforms.remove("Pinterest")
                    
            if st.checkbox("Other", value="Other" in platforms):
                if "Other" not in platforms:
                    platforms.append("Other")
            else:
                if "Other" in platforms:
                    platforms.remove("Other")
        
        update_progress("setup", 0.9)
        
        # Save form data to session state
        st.session_state.brand_guidelines = {
            "brand_name": brand_name,
            "brand_voice": brand_voice,
            "industry": industry,
            "key_values": key_values
        }
        st.session_state.goals = goals
        st.session_state.target_audience = {
            "age_range": age_range,
            "interests": interests,
            "location": location,
            "pain_points": pain_points
        }
        st.session_state.platforms = platforms
        
        # Submit button
        submit_button = st.form_submit_button("Generate Content Strategy")
    
    # Handle form submission
    if submit_button:
        # Validate inputs - improved validation logic
        missing_fields = []
        
        if not brand_name.strip():
            missing_fields.append("Brand Name")
        
        if not industry.strip():
            missing_fields.append("Industry")
        
        if not goals.strip():
            missing_fields.append("Goals")
        
        if not platforms:
            missing_fields.append("at least one Platform")
        
        if missing_fields:
            st.error(f"Please fill in all required fields: {', '.join(missing_fields)}.")
            return
        
        # Prepare data for API
        setup_data = {
            "email": st.session_state.email,
            "brand_guidelines": st.session_state.brand_guidelines,
            "goals": st.session_state.goals,
            "target_audience": st.session_state.target_audience,
            "platforms": st.session_state.platforms
        }
        
        try:
            # Show spinner during API call
            with st.spinner("🤖 AI is analyzing your brand and creating your strategy..."):
                update_progress("setup", 0.95)
                
                # Make API request
                response = requests.post(
                    f"{API_BASE_URL}/setup",  # Changed from /process_setup to /setup
                    json=setup_data,
                    timeout=120  # Longer timeout for AI processing
                )
                
                if response.status_code == 200:
                    response_json = response.json()
                    st.session_state.api_response = response_json
                    
                    # Store setup_id correctly - check different possible locations
                    if "result" in response_json and "setup_id" in response_json["result"]:
                        st.session_state.setup_id = response_json["result"]["setup_id"]
                    elif "setup_id" in response_json:
                        st.session_state.setup_id = response_json["setup_id"]
                    else:
                        # If setup_id is not in the expected location, search for it
                        import json
                        response_str = json.dumps(response_json)
                        if "setup_id" in response_str:
                            st.write("Debug: setup_id found in response but not in expected location")
                            st.write(f"Debug: Full response: {response_json}")
                    
                    # Debug output
                    st.write(f"Debug: Stored setup_id: {st.session_state.setup_id}")
                    
                    st.session_state.raw_content = response_json.get("result", {}).get("raw", "")
                    
                    # Mark setup as completed
                    st.session_state.setup_completed = True
                    update_progress("setup", 1.0)
                    
                    # Save session
                    save_session()
                    
                    st.success("✨ Setup completed successfully! Here's your personalized strategy:")
                    st.write(st.session_state.raw_content)
                    
                    # Navigation button
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col3:
                        if st.button("➡️ Continue to Content Planning", key="navigate_button"):
                            st.session_state.page = "Content Planner"
                            save_session()
                            st.rerun()
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
