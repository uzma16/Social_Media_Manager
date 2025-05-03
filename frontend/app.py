import streamlit as st
import importlib
from utils.session_manager import initialize_session, load_session, save_session, clear_session

# Set page configuration as the first Streamlit command
st.set_page_config(
    page_title="Social Media Manager",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
initialize_session()

# Function to validate email
def validate_email(email: str) -> bool:
    # For demo purposes, accept any valid-looking email
    import re
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))

# Authentication form
def render_authentication():
    st.title("Welcome to Social Media Manager")
    st.write("Please enter your email to access the platform.")
    
    with st.form(key="auth_form"):
        email = st.text_input("Email Address", placeholder="Enter your email", key="email_input")
        remember_me = st.checkbox("Remember me", value=True)
        submit_button = st.form_submit_button("Authenticate")
        
        if submit_button:
            if not email:
                st.error("Please enter an email address.")
            elif validate_email(email):
                # Try to load existing session
                if load_session(email):
                    st.success("Welcome back! Loading your previous session...")
                else:
                    # Create new session
                    st.session_state.authenticated = True
                    st.session_state.email = email
                    if remember_me:
                        save_session(email)
                    st.success("Authentication successful! Loading the platform...")
                st.rerun()
            else:
                st.error("Invalid email format. Please enter a valid email address.")

# Function to dynamically import a module
def import_page(module_name):
    try:
        module = importlib.import_module(f"pages.modules.{module_name}")
        return module
    except ImportError as e:
        st.error(f"Failed to import {module_name}: {str(e)}")
        return None

# Progress indicator component
def render_progress_indicator():
    if st.session_state.current_operation:
        operation = st.session_state.current_operation
        if operation == "setup":
            progress = st.session_state.setup_progress
            st.progress(progress, f"Setup Progress: {int(progress*100)}%")
        elif operation == "content_generation":
            progress = st.session_state.content_generation_progress
            st.progress(progress, f"Content Generation: {int(progress*100)}%")

# Main app rendering
def render_main_app():
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        st.write(f"Logged in as: {st.session_state.email}")
        
        # Show setup completion status
        if st.session_state.setup_completed:
            st.success("✅ Setup Completed")
        else:
            st.warning("⚠️ Setup Incomplete")
        
        # Navigation buttons
        setup_clicked = st.button("📝 Setup", key="setup_button")
        planner_clicked = st.button("📅 Content Planner", key="planner_button")
        credentials_clicked = st.button("🔑 Platform Credentials", key="credentials_button")
        
        # Handle navigation button clicks
        if setup_clicked:
            st.session_state.previous_page = st.session_state.page
            st.session_state.page = "Setup"
            save_session()
            st.rerun()
            
        if planner_clicked:
            if not st.session_state.setup_completed:
                st.error("Please complete setup first")
            else:
                st.session_state.previous_page = st.session_state.page
                st.session_state.page = "Content Planner"
                save_session()
                st.rerun()
                
        if credentials_clicked:
            if not st.session_state.setup_completed:
                st.error("Please complete setup first")
            elif not st.session_state.content_schedule:
                st.error("Please generate content schedule first")
            else:
                st.session_state.previous_page = st.session_state.page
                st.session_state.page = "Credentials"
                save_session()
                st.rerun()
        
        st.divider()
        
        # Session management
        save_clicked = st.button("💾 Save Session", key="save_session_button")
        logout_clicked = st.button("🚪 Logout", key="logout_button")
        
        if save_clicked:
            if save_session():
                st.success("Session saved successfully!")
            else:
                st.error("Failed to save session")
                
        if logout_clicked:
            clear_session()
            st.session_state.authenticated = False
            st.rerun()

    # Render progress indicator if an operation is in progress
    render_progress_indicator()
    
    # Page routing
    if st.session_state.page == "Setup":
        setup_module = import_page("1_setup")
        if setup_module:
            setup_module.render()
    elif st.session_state.page == "Content Planner":
        planner_module = import_page("2_content_planning")
        if planner_module:
            planner_module.render()
    elif st.session_state.page == "Credentials":
        credentials_module = import_page("3_last_page")
        if credentials_module:
            credentials_module.render()
    else:
        st.error("Unknown page selected")
        # Fallback to setup page
        st.session_state.page = "Setup"
        st.rerun()

# Conditional rendering based on authentication
if not st.session_state.authenticated:
    render_authentication()
else:
    render_main_app()
