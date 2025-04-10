import streamlit as st
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'components')))
from components.utils import make_api_call

st.set_page_config(page_title="Step 1: Setup", layout="wide")

st.title("Step 1: User Input & Setup")
st.write("Provide your brand details to set up the social media manager.")

# Form for user inputs
with st.form(key="setup_form"):
    # Brand Guidelines
    st.subheader("Brand Guidelines")
    voice = st.text_input("Brand Voice (e.g., professional, witty)", "")
    tone = st.text_input("Tone (e.g., formal, casual)", "")
    visual_style = st.text_area("Visual Style (e.g., minimalist, bold)", "")
    dos_donts = st.text_area("Dos and Don'ts (e.g., avoid politics)", "")

    # Goals
    st.subheader("Goals")
    goals = st.text_area("Specific Goals (e.g., increase engagement by 20%)", "")
    
    # Brand Assets
    st.subheader("Brand Assets")
    logos = st.file_uploader("Upload Logos", type=["png", "jpg", "svg"], accept_multiple_files=True)
    fonts = st.file_uploader("Upload Fonts", type=["ttf", "otf"], accept_multiple_files=True)
    colors = st.text_input("Brand Colors (e.g., #FF5733, #C70039)", "")
    templates = st.file_uploader("Upload Templates", type=["pdf", "psd"], accept_multiple_files=True)

    # Target Audience
    st.subheader("Target Audience")
    demographics = st.text_area("Demographics (e.g., age 25-34, female)", "")
    psychographics = st.text_area("Psychographics (e.g., tech-savvy, eco-conscious)", "")
    behaviors = st.text_area("Behaviors (e.g., active mornings)", "")

    # Platforms
    st.subheader("Social Media Platforms")
    platforms = st.multiselect("Select Platforms", ["Instagram", "Twitter", "LinkedIn", "TikTok", "Facebook"])
    priorities = st.text_area("Platform Priorities (e.g., Instagram 70%)", "")

    # Existing Data
    st.subheader("Existing Data")
    past_data = st.file_uploader("Upload Past Data (e.g., analytics CSV)", type=["csv", "xlsx"])

    submit_button = st.form_submit_button(label="Submit Setup")

# Handle form submission
if submit_button:
    # Prepare data for API
    setup_data = {
        "brand_guidelines": {"voice": voice, "tone": tone, "visual_style": visual_style, "dos_donts": dos_donts},
        "goals": goals,
        "target_audience": {"demographics": demographics, "psychographics": psychographics, "behaviors": behaviors},
        "platforms": {"names": platforms, "priorities": priorities},
    }

    # Handle file uploads
    files = []
    for logo in logos or []:
        files.append(("logos", (logo.name, logo, logo.type)))
    for font in fonts or []:
        files.append(("fonts", (font.name, font, font.type)))
    for template in templates or []:
        files.append(("templates", (template.name, template, template.type)))
    if past_data:
        files.append(("past_data", (past_data.name, past_data, past_data.type)))

    # Send to backend
    response = make_api_call("POST", "/setup", data={"json": json.dumps(setup_data)}, files=files)
    
    if response.status_code == 200:
        result = response.json()
        st.success("Setup completed successfully!")
        st.json(result["brand_voice_profile"])
        st.write("Initial Content Strategy:")
        st.write(result["content_strategy"])
        st.write("Assets stored successfully.")
    else:
        st.error(f"Error: {response.text}")

# Sidebar for instructions
st.sidebar.write("Enter all required fields. Upload assets as needed.")