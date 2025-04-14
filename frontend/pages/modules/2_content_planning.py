import streamlit as st
import json
import pandas as pd
import requests
import logging
from typing import Dict, Any,List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API submission function
def submit_schedule(strategy_text: str) -> requests.Response:
    """
    Submit content strategy to the backend API to generate a posting schedule.
    """
    API_URL = "http://localhost:8000"
    try:
        response = requests.post(
            f"{API_URL}/content_planner",
            json={"strategy": strategy_text},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        raise

# Parse API response to extract posts
# Parse API response to extract posts
def parse_schedule_response(response_json: Any) -> List[Dict]:
    """
    Extract the posts list from the API response, handling various JSON structures.
    """
    logger.info("Raw API response: %s", json.dumps(response_json, indent=2))
    try:
        # If response is a list, return it directly
        if isinstance(response_json, list):
            logger.info("Found %d posts in response list", len(response_json))
            return response_json
        # Handle dictionary response
        if not isinstance(response_json, dict):
            raise ValueError("Expected a dictionary or list, but got a different type")
        
        # Check for "raw" key with embedded JSON
        if "raw" in response_json:
            raw_content = response_json["raw"]
            # Strip markdown-like ```json markers if present
            raw_content = raw_content.replace("```json\n", "").replace("\n```", "").strip()
            parsed_raw = json.loads(raw_content)
            # Handle case where parsed_raw is a list or a dict with "posts"
            if isinstance(parsed_raw, list):
                logger.info("Found %d posts in 'raw' list", len(parsed_raw))
                return parsed_raw
            elif isinstance(parsed_raw, dict) and "posts" in parsed_raw:
                posts = parsed_raw["posts"]
                logger.info("Found %d posts in 'raw.posts'", len(posts))
                return posts
            else:
                logger.warning("No valid posts found in 'raw' content")
                return []
        # Check for "schedule" key
        elif "schedule" in response_json:
            schedule = response_json["schedule"]
            if isinstance(schedule, dict) and "posts" in schedule:
                posts = schedule["posts"]
                logger.info("Found %d posts in 'schedule.posts'", len(posts))
                return posts
            elif isinstance(schedule, list):
                logger.info("Found %d posts in 'schedule' list", len(schedule))
                return schedule
        # Check for direct "posts" key
        elif "posts" in response_json:
            posts = response_json["posts"]
            logger.info("Found %d posts in 'posts'", len(posts))
            return posts
        logger.warning("No posts found in response")
        return []
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        logger.error("Error parsing API response: %s", str(e))
        st.error(f"Failed to parse API response: {str(e)}")
        return []

def render():
    # Access raw_content from session state
    raw_content = st.session_state.get("raw_content", "No data received from Setup.")
    st.subheader("Received Strategy Data")
    st.write("Raw Content:", raw_content)
    DEFAULT_CONTENT_STRATEGY = raw_content
    # Streamlit app configuration
    # st.set_page_config(page_title="Social Media Scheduler", layout="wide")
    st.title("Social Media Content Scheduler")
    st.write("Generate and explore a 2-month posting schedule interactively.")

    # Input section
    st.header("Content Strategy Input")
    strategy_text = st.text_area(
        "Enter or edit your social media content strategy:",
        value=DEFAULT_CONTENT_STRATEGY,
        height=400,
        key="strategy_input"
    )

    # Platform and week filters
    st.header("Filters")
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        platform_filter = st.multiselect(
            "Filter by Platform",
            options=["All", "Instagram", "LinkedIn"],
            default=["All"],
            key="platform_filter"
        )
    with col2:
        week_filter = st.multiselect(
            "Filter by Week",
            options=["All"] + [str(i) for i in range(1, 9)],
            default=["All"],
            key="week_filter"
        )
    with col3:
        search_query = st.text_input("Search by Pillar or Description", "", key="search_query")

    # Generate schedule button
    if st.button("Generate Schedule", key="generate_button"):
        with st.spinner("Generating posting schedule..."):
            try:
                # Call the API
                response = submit_schedule(strategy_text)
                schedule_posts = parse_schedule_response(response.json())
                
                if not schedule_posts:
                    st.warning("No schedule data found in the response")
                    logger.warning("Empty posts list returned from parse_schedule_response")
                
                # Store the posts in session state for filtering
                st.session_state.schedule_posts = schedule_posts
                
                if schedule_posts:
                    st.success("Schedule generated successfully!")
                else:
                    st.info("Using sample data for display due to empty response")
                    # Sample data for UI testing
                    st.session_state.schedule_posts = [
                        {
                            "platform": "Instagram",
                            "content_type": "Image",
                            "pillar_or_campaign": "Industry Insights",
                            "description": "Share a key industry statistic with a minimalist visual.",
                            "week": 1,
                            "day": "Monday",
                            "time": "11:00 AM EST"
                        },
                        {
                            "platform": "LinkedIn",
                            "content_type": "Article",
                            "pillar_or_campaign": "Industry Insights",
                            "description": "Publish an article on industry trends.",
                            "week": 1,
                            "day": "Tuesday",
                            "time": "2:00 PM EST"
                        }
                    ]
            except Exception as e:
                st.error(f"Failed to generate schedule: {str(e)}")
                logger.error(f"Error in Streamlit app: %s", str(e))

    # Display results
    if "schedule_posts" in st.session_state and st.session_state.schedule_posts:
        st.header("Interactive Posting Schedule")
        
        # Convert posts to DataFrame
        df = pd.DataFrame(st.session_state.schedule_posts)
        
        # Apply filters
        filtered_df = df.copy()
        if "All" not in platform_filter:
            filtered_df = filtered_df[filtered_df["platform"].isin(platform_filter)]
        if "All" not in week_filter:
            filtered_df = filtered_df[filtered_df["week"].isin([int(w) for w in week_filter])]
        if search_query:
            filtered_df = filtered_df[
                filtered_df["pillar_or_campaign"].str.contains(search_query, case=False, na=False) |
                filtered_df["description"].str.contains(search_query, case=False, na=False)
            ]
        
        # Add color-coding by platform
        def highlight_platform(row):
            # Static counter to simulate alternating rows
            highlight_platform._counter = getattr(highlight_platform, '_counter', 0) + 1
            color = "background-color: #f0f0f0" if highlight_platform._counter % 2 == 0 else "background-color: #e6f3ff"
            return [color] * len(row)
        
        # Display interactive table
        st.dataframe(
            filtered_df.style.apply(highlight_platform, axis=1),
            column_config={
                "platform": st.column_config.TextColumn("Platform", width="medium"),
                "content_type": st.column_config.TextColumn("Content Type", width="medium"),
                "pillar_or_campaign": st.column_config.TextColumn("Pillar/Campaign", width="large"),
                "description": st.column_config.TextColumn("Description", width="large"),
                "week": st.column_config.NumberColumn("Week", format="%d", width="small"),
                "day": st.column_config.TextColumn("Day", width="medium"),
                "time": st.column_config.TextColumn("Time (EST)", width="medium"),
                "date": st.column_config.TextColumn("Date", width="medium"),
                "datetime": st.column_config.TextColumn("Datetime (EST)", width="medium"),
                "time": st.column_config.TextColumn("Time (EST)", width="medium")
            },
            hide_index=True,
            use_container_width=True,
            height=400
        )
        
        # Display total posts
        st.write(f"**Total Posts:** {len(filtered_df)}")
        
        # Interactive post details
        st.subheader("Post Details")
        if len(filtered_df) > 0:
            selected_post_idx = st.selectbox(
                "Select a post to view details:",
                options=range(len(filtered_df)),
                format_func=lambda i: f"{filtered_df.iloc[i]['platform']} - {filtered_df.iloc[i]['pillar_or_campaign']} (Week {filtered_df.iloc[i]['week']})",
                key="post_selector"
            )
            
            selected_post = filtered_df.iloc[selected_post_idx]
            with st.expander("Post Details", expanded=True):
                st.markdown(f"""
                    **Platform:** {selected_post['platform']}  
                    **Content Type:** {selected_post['content_type']}  
                    **Pillar/Campaign:** {selected_post['pillar_or_campaign']}  
                    **Description:** {selected_post['description']}  
                    **Week:** {selected_post['week']}  
                    **Day:** {selected_post['day']}  
                    **Date:** {selected_post['date']}  
                    **Datetime:** {selected_post['datetime']}  
                    **Time:** {selected_post['time']}  
                    **Preview Caption (Simulated):**  
                    {selected_post['description'].split('.')[0]}. Join the conversation! #{selected_post['pillar_or_campaign'].replace(' ', '')}
                """)
        
        # Export options
        st.subheader("Export Schedule")
        col_export1, col_export2 = st.columns(2)
        with col_export1:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name="social_media_schedule.csv",
                mime="text/csv",
                key="csv_download"
            )
        with col_export2:
            json_data = json.dumps(filtered_df.to_dict(orient="records"))
            st.download_button(
                label="Download as JSON",
                data=json_data,
                file_name="social_media_schedule.json",
                mime="application/json",
                key="json_download"
            )

    # Replace switch_page with session state navigation
    if st.button("⬅️ Back to Setup", key="back_button"):
        st.session_state.page = "Setup"
        st.rerun()
        
    # Instructions
    st.sidebar.header("Instructions")
    st.sidebar.markdown("""
    1. Enter or edit your content strategy in the text area.
    2. Use filters to select platforms, weeks, or search by pillar/description.
    3. Click **Generate Schedule** to fetch the schedule via API.
    4. Explore posts in the table, select a post for details, or export as CSV/JSON.
    """)