import streamlit as st
import json
import os
from datetime import datetime
import pickle

# Directory for storing session data
SESSION_DIR = "sessions"

def initialize_session():
    """Initialize session state with default values if they don't exist"""
    defaults = {
        "authenticated": False,
        "email": "",
        "page": "Setup",
        "previous_page": None,
        "setup_completed": False,
        "content_schedule": None,
        "setup_id": None,
        "schedule_id": None,
        "raw_content": None,
        "current_operation": None,
        "setup_progress": 0.0,
        "content_generation_progress": 0.0,
        "brand_guidelines": {},
        "goals": "",
        "target_audience": {},
        "platforms": [],
        "api_response": None
    }
    
    # Initialize session state variables
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def save_session(email=None):
    """Save current session state to a file"""
    try:
        # Create sessions directory if it doesn't exist
        if not os.path.exists(SESSION_DIR):
            os.makedirs(SESSION_DIR)
        
        # Use email from parameter or session state
        user_email = email if email else st.session_state.email
        if not user_email:
            return False
        
        # Create a copy of session state without button states
        session_data = {}
        for key, value in st.session_state.items():
            # Skip button widget keys and other non-serializable items
            if not key.endswith('_button') and key != 'FormSubmitter:auth_form-Authenticate':
                try:
                    # Test if value is serializable
                    json.dumps(value)
                    session_data[key] = value
                except (TypeError, OverflowError):
                    # Skip non-serializable values
                    pass
        
        # Save to file
        filename = os.path.join(SESSION_DIR, f"{user_email.replace('@', '_at_')}.json")
        with open(filename, 'w') as f:
            json.dump(session_data, f)
        
        return True
    except Exception as e:
        st.error(f"Error saving session: {str(e)}")
        return False

def load_session(email):
    """Load session state from a file"""
    try:
        filename = os.path.join(SESSION_DIR, f"{email.replace('@', '_at_')}.json")
        if not os.path.exists(filename):
            return False
        
        with open(filename, 'r') as f:
            session_data = json.load(f)
        
        # Update session state with loaded data
        for key, value in session_data.items():
            # Skip button widget keys
            if not key.endswith('_button'):
                st.session_state[key] = value
        
        # Set authenticated flag
        st.session_state.authenticated = True
        
        return True
    except Exception as e:
        st.error(f"Error loading session: {str(e)}")
        return False

def clear_session():
    """Clear the current session state"""
    for key in list(st.session_state.keys()):
        # Skip button widget keys
        if not key.endswith('_button'):
            del st.session_state[key]
    
    # Reinitialize with defaults
    initialize_session()

def update_progress(operation_type, progress_value):
    """Update progress for a specific operation type
    
    Args:
        operation_type (str): Type of operation ('setup' or 'content_generation')
        progress_value (float): Progress value between 0.0 and 1.0
    """
    # Validate progress value
    progress_value = max(0.0, min(1.0, float(progress_value)))
    
    # Set current operation if not already set
    if not st.session_state.current_operation and progress_value > 0:
        st.session_state.current_operation = operation_type
    
    # Update progress based on operation type
    if operation_type == "setup":
        st.session_state.setup_progress = progress_value
        # Clear current operation if complete
        if progress_value >= 1.0:
            st.session_state.current_operation = None
    elif operation_type == "content_generation":
        st.session_state.content_generation_progress = progress_value
        # Clear current operation if complete
        if progress_value >= 1.0:
            st.session_state.current_operation = None
    
    # Save session after progress update
    save_session()


