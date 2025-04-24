import streamlit as st

def render():
    st.title("Platform Credentials & Posting Options")
    st.write("Provide credentials for auto-posting or opt to receive posts via email.")

    # Layout: Three columns
    col_left, col_center, col_right = st.columns([2, 1, 2])

    # Left column: Credentials input
    with col_left:
        st.header("Social Media Credentials")
        st.markdown("Enter your platform credentials for auto-posting (stored securely).")
        
        with st.form("credentials_form"):
            instagram_user = st.text_input("Instagram Username", key="instagram_user")
            instagram_pass = st.text_input("Instagram Password", type="password", key="instagram_pass")
            
            linkedin_user = st.text_input("LinkedIn Username/Email", key="linkedin_user")
            linkedin_pass = st.text_input("LinkedIn Password", type="password", key="linkedin_pass")
            
            twitter_user = st.text_input("Twitter Username", key="twitter_user")
            twitter_pass = st.text_input("Twitter Password", type="password", key="twitter_pass")
            
            facebook_user = st.text_input("Facebook Username/Email", key="facebook_user")
            facebook_pass = st.text_input("Facebook Password", type="password", key="facebook_pass")
            
            tiktok_user = st.text_input("TikTok Username", key="tiktok_user")
            tiktok_pass = st.text_input("TikTok Password", type="password", key="tiktok_pass")
            
            submit_credentials = st.form_submit_button("Submit Credentials")
            
            if submit_credentials:
                if any([instagram_user, linkedin_user, twitter_user, facebook_user, tiktok_user]):
                    st.session_state.credentials = {
                        "instagram": {"user": instagram_user, "pass": instagram_pass},
                        "linkedin": {"user": linkedin_user, "pass": linkedin_pass},
                        "twitter": {"user": twitter_user, "pass": twitter_pass},
                        "facebook": {"user": facebook_user, "pass": facebook_pass},
                        "tiktok": {"user": tiktok_user, "pass": tiktok_pass}
                    }
                    st.success("Credentials submitted! (Stored in session state)")
                else:
                    st.error("Please provide at least one platform's credentials.")

    # Center column: OR divider
    with col_center:
        st.markdown("<h1 style='text-align: center; margin-top: 200px;'>OR</h1>", unsafe_allow_html=True)

    # Right column: Email option
    with col_right:
        st.header("Receive Posts via Email")
        st.markdown("If you prefer not to share credentials, we can send generated posts to your email for manual posting.")
        
        with st.form("email_form"):
            email = st.text_input("Email Address", key="email_input")
            submit_email = st.form_submit_button("Submit Email")
            
            if submit_email:
                if email and "@" in email:
                    st.session_state.email = email
                    st.success(f"Email submitted: {email}. Posts will be sent for review. (Placeholder)")
                else:
                    st.error("Please enter a valid email address.")

    # Navigation buttons in same row
    st.markdown("---")
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("⬅️ Back to Content Planning", key="back_button"):
            st.session_state.page = "Content Planner"
            st.rerun()
    with col_nav2:
        if st.button("✅ Finish", key="finish_button"):
            if "credentials" in st.session_state or "email" in st.session_state:
                st.success("Setup complete! Credentials or email saved. (Placeholder: Ready for posting)")
            else:
                st.error("Please submit credentials or an email before finishing.")

    # Instructions
    st.sidebar.header("Instructions")
    st.sidebar.markdown("""
    1. **Credentials (Left):** Enter usernames and passwords for platforms to enable auto-posting.
    2. **Email (Right):** Provide an email to receive posts for manual verification and posting.
    3. Click **Submit** in either form to save.
    4. Use **Back to Content Planning** to return or **Finish** to complete the setup.
    """)