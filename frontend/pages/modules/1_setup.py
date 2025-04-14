import streamlit as st
import json
import requests
from typing import Dict, Any
from streamlit_extras.switch_page_button import switch_page


# Page configuration
# st.set_page_config(page_title="Step 1: Setup", layout="wide")

def display_api_response(response_data):
    try:
        st.subheader("🎯 Generated Strategy")
        # Create an expandable section for the strategy
        with st.expander("View Strategy", expanded=True):
            # Extract the raw content from the response
            raw_content = response_data.get("result", {}).get("raw", "")
            st.write("Raw response data:", raw_content)

        # Add a download button for the complete report
        st.download_button(
            label="📥 Download Complete Report",
            data=json.dumps(response_data, indent=2),
            file_name="social_media_strategy.json",
            mime="application/json",
        )
    
    except Exception as e:
        st.error(f"Error displaying response: {str(e)}")
        st.write("Raw response data:", response_data)

    # return raw_content

def submit_setup(setup_data: Dict[str, Any]) -> requests.Response:
    API_URL = "http://localhost:8000"
    try:
        response = requests.post(
            f"{API_URL}/process_setup",  # Note the underscore here
            json=setup_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        raise


def render():
    # Initialize session state for storing API response
    if 'api_response' not in st.session_state:
        st.session_state.api_response = None

    st.title("Step 1: User Input & Setup")
    st.write("Provide your brand details to set up the social media manager.")


    # Form for user inputs
    with st.form(key="setup_form"):
        # Brand Guidelines
        st.subheader("Brand Guidelines")
        voice = st.text_input(
            "Brand Voice (e.g., professional, witty)", 
            placeholder="Enter your brand's voice characteristics"
        )
        tone = st.text_input(
            "Tone (e.g., formal, casual)", 
            placeholder="Enter your brand's tone"
        )
        visual_style = st.text_area(
            "Visual Style (e.g., minimalist, bold)", 
            placeholder="Describe your brand's visual style"
        )
        dos_donts = st.text_area(
            "Dos and Don'ts (e.g., avoid politics)", 
            placeholder="List your brand's dos and don'ts"
        )

        # Goals
        st.subheader("Goals")
        goals = st.text_area(
            "Specific Goals (e.g., increase engagement by 20%)", 
            placeholder="Enter your social media goals"
        )
        
        # Brand Assets
        st.subheader("Brand Assets")
        colors = st.text_input(
            "Brand Colors (e.g., #FF5733, #C70039)", 
            placeholder="Enter your brand colors (hex codes preferred)"
        )

        # Target Audience
        st.subheader("Target Audience")
        demographics = st.text_area(
            "Demographics (e.g., age 25-34, female)", 
            placeholder="Describe your target audience demographics"
        )
        psychographics = st.text_area(
            "Psychographics (e.g., tech-savvy, eco-conscious)", 
            placeholder="Describe your audience's interests and values"
        )
        behaviors = st.text_area(
            "Behaviors (e.g., active mornings)", 
            placeholder="Describe your audience's typical behaviors"
        )

        # Platforms
        st.subheader("Social Media Platforms")
        platforms = st.multiselect(
            "Select Platforms",
            options=["Instagram", "Twitter", "LinkedIn", "TikTok", "Facebook"],
            help="Choose the platforms you want to focus on"
        )
        priorities = st.text_area(
            "Platform Priorities (e.g., Instagram 70%)", 
            placeholder="Specify the priority level for each platform"
        )

        # Submit button
        submit_button = st.form_submit_button(
            label="Submit Setup",
            help="Click to submit your setup information"
        )

    # Handle form submission
    if submit_button:
        # Validate required fields
        if not voice or not tone or not goals or not platforms:
            st.error("Please fill in all required fields: Brand Voice, Tone, Goals, and at least one Platform.")
        else:
            # Prepare data for API
            setup_data = {
                "brand_guidelines": {
                    "voice": voice,
                    "tone": tone,
                    "visual_style": visual_style or "",
                    "dos_donts": dos_donts or ""
                },
                "goals": goals,
                "target_audience": {
                    "demographics": demographics or "",
                    "psychographics": psychographics or "",
                    "behaviors": behaviors or ""
                },
                "platforms": platforms
            }

            try:
                # Show loading spinner with custom message
                with st.spinner("🤖 AI is analyzing your brand and creating your strategy..."):
                    response = submit_setup(setup_data)
                    # Debug: Print raw response
                    # st.write("Debug - Raw Response:", response.text)
                    st.session_state.api_response = response.json()
                
                # Display success message
                st.success("✨ Setup completed successfully! Here's your personalized strategy:")
                
                # Display the API response
                display_api_response(st.session_state.api_response)
            except Exception as e:
                st.error("⚠️ Error during setup")
                with st.expander("View Error Details"):
                    st.write(f"Error: {str(e)}")
                    if hasattr(e, 'response'):
                        st.code(e.response.content.decode())
                if st.button("🔄 Try Again"):
                    st.session_state.api_response = None
                    st.rerun()
                
                # Add navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("📝 Edit Setup"):
            st.session_state.api_response = None
            st.rerun()
    with col2:
        if st.button("💾 Save Strategy"):
            # Add functionality to save the strategy
            st.toast("Strategy saved successfully!")
    with col3:
        # Navigation button to switch to Content Planner with data
        if st.button("➡️ Continue to Content Planning", key="navigate_button"):
            # Store raw_content in session state
            raw_content = st.session_state.api_response.get("result", {}).get("raw", "") if st.session_state.api_response else ""
            st.session_state.raw_content = raw_content
            st.session_state.page = "Content Planner"
            st.rerun()
        
    
    # Sidebar with instructions and tips
    with st.sidebar:
        st.header("Setup Instructions")
        st.markdown("""
        1. Fill in all required fields (marked with *)
        2. Be as specific as possible in your descriptions
        3. Choose your target platforms carefully
        4. Review your inputs before submitting
        """)
        
        st.header("Tips")
        st.info("""
        💡 Your brand voice should align with your target audience's preferences.
        
        💡 Be specific with your goals - make them measurable when possible.
        
        💡 Consider your resources when selecting platforms to focus on.
        """)

        # Add help contact
        st.divider()
        st.markdown("Need help? [Contact Support](mailto:support@example.com)")
