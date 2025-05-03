import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from utils.session_manager import save_session, update_progress
from config import API_BASE_URL

def render():
    st.title("Content Planning")
    
    # Check if setup is completed
    if not st.session_state.setup_completed or not st.session_state.setup_id:
        st.error("Please complete the setup first.")
        col1, col2 = st.columns([1, 1])
        with col2:
            if st.button("⬅️ Go to Setup"):
                st.session_state.page = "Setup"
                save_session()
                st.rerun()
        return
    
    # Display existing content schedule if available
    if st.session_state.content_schedule:
        st.success("✅ Content schedule generated!")
        display_content_schedule(st.session_state.content_schedule)
        
        # Option to regenerate
        if st.button("🔄 Regenerate Content Schedule"):
            st.session_state.content_schedule = None
            st.session_state.schedule_id = None
            save_session()
            st.rerun()
            
        # Navigation button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col3:
            if st.button("➡️ Continue to Platform Credentials", key="navigate_button"):
                st.session_state.page = "Credentials"
                save_session()
                st.rerun()
        return
    
    # Initialize progress tracking
    update_progress("content_generation", 0.1)
    
    # Content planning form
    with st.form(key="content_planning_form"):
        st.subheader("Content Schedule Generation")
        st.write("Let's create a content schedule based on your brand strategy.")
        
        # Display the content strategy
        if st.session_state.raw_content:
            st.subheader("Your Content Strategy")
            st.write(st.session_state.raw_content)
        
        # Time period selection
        st.subheader("Schedule Parameters")
        col1, col2 = st.columns(2)
        
        with col1:
            time_period = st.selectbox(
                "Time Period",
                options=["1 Week", "2 Weeks", "1 Month"],
                index=1
            )
            
        with col2:
            post_frequency = st.selectbox(
                "Post Frequency",
                options=["Daily", "Every other day", "3 times per week", "Weekly"],
                index=2
            )
        
        update_progress("content_generation", 0.3)
        
        # Additional instructions
        special_instructions = st.text_area(
            "Special Instructions (Optional)",
            placeholder="e.g., Focus on product launches, Include seasonal content, etc.",
            height=100
        )
        
        update_progress("content_generation", 0.5)
        
        # Submit button
        submit_button = st.form_submit_button("Generate Content Schedule")
    
    # Handle form submission
    if submit_button:
        try:
            # Show spinner during API call
            with st.spinner("🤖 AI is creating your content schedule..."):
                update_progress("content_generation", 0.7)
                
                # Prepare data for API
                content_data = {
                    "email": st.session_state.email,
                    "strategy": st.session_state.raw_content,
                    "time_period": time_period,
                    "post_frequency": post_frequency,
                    "special_instructions": special_instructions
                }

                # Make API request
                response = requests.post(
                    f"{API_BASE_URL}/content_planner",
                    json=content_data,
                    timeout=180  # Longer timeout for content generation
                )
                
                if response.status_code == 200:
                    content_schedule = response.json()
                    st.session_state.content_schedule = content_schedule
                    st.session_state.schedule_id = content_schedule.get("schedule_id")
                    
                    update_progress("content_generation", 1.0)
                    save_session()
                    
                    st.success("✨ Content schedule generated successfully!")
                    display_content_schedule(content_schedule)
                    
                    # Navigation button
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col3:
                        if st.button("➡️ Continue to Platform Credentials", key="navigate_button"):
                            st.session_state.page = "Credentials"
                            save_session()
                            st.rerun()
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

def display_content_schedule(content_schedule):
    """Display the content schedule in a user-friendly format."""
    if isinstance(content_schedule, list):
        posts = content_schedule
    elif isinstance(content_schedule, dict) and "posts" in content_schedule:
        posts = content_schedule["posts"]
    else:
        st.error("Invalid content schedule format")
        return
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Calendar View", "List View"])
    
    with tab1:
        # Calendar view
        st.subheader("Calendar View")
        
        # Convert posts to DataFrame
        df = pd.DataFrame(posts)
        
        # Ensure date column exists and is in datetime format
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")
            
            # Group by date
            dates = df["date"].dt.date.unique()
            
            for date in dates:
                date_str = date.strftime("%A, %B %d, %Y")
                st.write(f"### {date_str}")
                
                # Get posts for this date
                day_posts = df[df["date"].dt.date == date]
                
                for _, post in day_posts.iterrows():
                    # Use dictionary-style access for DataFrame rows
                    platform = post.get("platform", "All") if isinstance(post, dict) else post["platform"] if "platform" in post else "All"
                    title = post.get("title", "Post") if isinstance(post, dict) else post["title"] if "title" in post else "Post"
                    
                    with st.expander(f"{platform} - {title}"):
                        # Safely access values using conditional logic
                        if isinstance(post, dict):
                            st.write(f"**Platform:** {post.get('platform', 'Not specified')}")
                            st.write(f"**Time:** {post.get('time', 'Not specified')}")
                            st.write(f"**Content:** {post.get('content', '')}")
                            
                            if "image_description" in post and post["image_description"]:
                                st.write(f"**Image Description:** {post['image_description']}")
                                
                            if "hashtags" in post and post["hashtags"]:
                                st.write(f"**Hashtags:** {post['hashtags']}")
                        else:
                            # For pandas Series objects
                            st.write(f"**Platform:** {post['platform'] if 'platform' in post else 'Not specified'}")
                            st.write(f"**Time:** {post['time'] if 'time' in post else 'Not specified'}")
                            st.write(f"**Content:** {post['content'] if 'content' in post else ''}")
                            
                            if "image_description" in post and post["image_description"]:
                                st.write(f"**Image Description:** {post['image_description']}")
                                
                            if "hashtags" in post and post["hashtags"]:
                                st.write(f"**Hashtags:** {post['hashtags']}")
                
                st.divider()
        else:
            st.error("Date information missing in content schedule")
    
    with tab2:
        # List view
        st.subheader("List View")
        
        # Create a more compact table view
        if posts:
            # Extract relevant columns
            table_data = []
            for post in posts:
                # Handle both dict and non-dict post objects
                if isinstance(post, dict):
                    content = post.get("content", "")
                    table_data.append({
                        "Date": post.get("date", ""),
                        "Platform": post.get("platform", ""),
                        "Title": post.get("title", ""),
                        "Content": content[:100] + "..." if len(content) > 100 else content
                    })
                else:
                    # For other types (like pandas Series)
                    content = post["content"] if "content" in post else ""
                    table_data.append({
                        "Date": post["date"] if "date" in post else "",
                        "Platform": post["platform"] if "platform" in post else "",
                        "Title": post["title"] if "title" in post else "",
                        "Content": content[:100] + "..." if len(content) > 100 else content
                    })
            
            # Display as table
            st.dataframe(pd.DataFrame(table_data), use_container_width=True)
        else:
            st.write("No posts in schedule")
    
    # Download option
    st.download_button(
        label="📥 Download Content Schedule",
        data=json.dumps(posts, indent=2),
        file_name="content_schedule.json",
        mime="application/json"
    )
