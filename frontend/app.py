# import streamlit as st
# import importlib


# # Set page configuration as the first Streamlit command
# st.set_page_config(
#     page_title="Social Media Manager",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # No custom navigation needed; Streamlit handles it via pages/
# st.write("Select a page from the sidebar to begin.")

# # Initialize session state
# if 'page' not in st.session_state:
#     st.session_state.page = "Setup"

# if 'raw_content' not in st.session_state:
#     st.session_state.raw_content = ""

# # Function to dynamically import a module
# def import_page(module_name):
#     try:
#         module = importlib.import_module(f"pages.modules.{module_name}")
#         return module
#     except ImportError as e:
#         st.error(f"Failed to import {module_name}: {str(e)}")
#         return None

# # Sidebar navigation
# with st.sidebar:
#     st.header("Navigation")
#     if st.button("📝 Setup", key="setup_button"):
#         st.session_state.page = "Setup"
#         st.rerun()
#     if st.button("📅 Content Planner", key="planner_button"):
#         st.session_state.page = "Content Planner"
#         st.rerun()

# # Page routing
# if st.session_state.page == "Setup":
#     setup_module = import_page("1_setup")
#     if setup_module:
#         setup_module.render()
# elif st.session_state.page == "Content Planner":
#     planner_module = import_page("2_content_planning")
#     if planner_module:
#         planner_module.render()
# else:
#     st.error("Unknown page selected")

import streamlit as st
import importlib

# Set page configuration as the first Streamlit command
st.set_page_config(
    page_title="Social Media Manager",
    layout="wide",
    initial_sidebar_state="expanded"
)

# No custom navigation needed; Streamlit handles it via pages/
st.write("Select a page from the sidebar to begin.")

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "Setup"

if 'raw_content' not in st.session_state:
    st.session_state.raw_content = ""

# Function to dynamically import a module
def import_page(module_name):
    try:
        module = importlib.import_module(f"pages.modules.{module_name}")
        return module
    except ImportError as e:
        st.error(f"Failed to import {module_name}: {str(e)}")
        return None

# Sidebar navigation
with st.sidebar:
    st.header("Navigation")
    if st.button("📝 Setup", key="setup_button"):
        st.session_state.page = "Setup"
        st.rerun()
    if st.button("📅 Content Planner", key="planner_button"):
        st.session_state.page = "Content Planner"
        st.rerun()
    if st.button("🔑 Platform Credentials", key="credentials_button"):
        st.session_state.page = "Last Page"
        st.rerun()

# Page routing
if st.session_state.page == "Setup":
    setup_module = import_page("1_setup")
    if setup_module:
        setup_module.render()
elif st.session_state.page == "Content Planner":
    planner_module = import_page("2_content_planning")
    if planner_module:
        planner_module.render()
elif st.session_state.page == "Last Page":
    last_page_module = import_page("3_last_page")
    if last_page_module:
        last_page_module.render()
else:
    st.error("Unknown page selected")