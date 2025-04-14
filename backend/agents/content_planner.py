import json
from crewai import Agent, Task, Crew
# from crewai_tools import tool
from textwrap import dedent
from openai import OpenAI
from dotenv import load_dotenv
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from crewai.tools import tool 
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

import litellm
from langchain.chat_models import ChatLiteLLM
# Initialize Gemini LLM using LiteLLM
llm = ChatLiteLLM(
    model="gemini/gemini-2.0-flash",
    api_key=os.getenv("GOOGLE_API_KEY")
)

class ContentStrategyInput(BaseModel):
    strategy: str
    
# Tool to parse and schedule content
@tool
def content_scheduler_tool(strategy_text: str) -> str:
    """Parse a social media content strategy and generate an actionable 2-month posting schedule."""
    logger.info("Generating 2-month content schedule")
    
    prompt = dedent(f"""
        You are an expert social media scheduler tasked with converting a content strategy into a detailed, actionable posting plan for the next 2 months (8 weeks). The plan should specify each post's platform, content type, content pillar or campaign, description, exact posting date, datetime, and time (week number, day, date, datetime in EST). Follow these steps:

        1. **Parse the Strategy**: Extract content pillars, content types, posting schedules, and campaign ideas from the input strategy.
        2. **Assign Posts**: For each platform, distribute posts across the 8 weeks based on the specified frequency, balancing pillars and incorporating campaigns. Use the recommended timing (e.g., Instagram at 11:00 AM EST, LinkedIn at 2:00 PM EST).
        3. **Incorporate Campaigns**: Schedule campaign-specific posts (e.g., "Ask the Expert" weekly, "Behind the Scenes" biweekly, "Industry Insights Report" once per month).
        4. **Ensure Variety**: Mix content types (e.g., Images, Reels, Articles) and pillars (e.g., Industry Insights, Educational Content) to maintain engagement.
        5. **Calculate Dates**: Start scheduling from {start_date.strftime('%Y-%m-%d')} (current date + 1 day). For each post, calculate the exact date based on the week and day, and include the full datetime in EST.
        6. **Output Format**: Return a JSON object with a list of posts, each containing:
           - platform: "Instagram" or "LinkedIn"
           - content_type: e.g., "Image", "Reel", "Article"
           - pillar_or_campaign: e.g., "Industry Insights", "Ask the Expert"
           - description: Brief description of the post content
           - week: Integer (1 to 8)
           - day: e.g., "Monday"
           - date: e.g., "2025-04-15" (calculated from {start_date.strftime('%Y-%m-%d')})
           - datetime: e.g., "2025-04-15 11:00:00 EST"
           - time: e.g., "11:00 AM EST"

        Inputs:
        Strategy Text: 
        {strategy_text}

        Constraints:
        - Adhere to the strategy’s frequency (Instagram: 5 posts/week, LinkedIn: 3 posts/week).
        - Use minimalist visuals and professional tone as per brand guidelines.
        - Distribute campaigns evenly (e.g., "Ask the Expert" weekly, "Industry Insights Report" in weeks 4 and 8).
        - Ensure all posts align with the goal of increasing engagement by 20%.
        - Dates must start from {start_date.strftime('%Y-%m-%d')} and be calculated accurately for each week and day.

        Return the JSON string directly.
    """)
    
    response = llm.invoke(prompt)
    return response.content

# Agent to handle content scheduling
def scheduler_agent():
    return Agent(
        role="Social Media Scheduler",
        goal="Convert a content strategy into an actionable 2-month posting schedule",
        backstory=dedent("""
            A meticulous planner with expertise in social media management, skilled at transforming high-level
            strategies into precise, actionable posting schedules. Adept at balancing content types, campaigns,
            and brand guidelines to maximize engagement and consistency.
        """),
        tools=[content_scheduler_tool],
        llm=llm,
        verbose=True
    )

# Task to generate the schedule
def scheduler_task(agent, strategy_text):
    return Task(
        description=dedent(f"""
            Parse the provided social media content strategy and create an actionable posting schedule for the
            next 2 months (8 weeks). The schedule should detail each post’s platform, content type, pillar or
            campaign, description, exact posting date, datetime, and time (week, day, date, datetime in EST), 
            aligning with the strategy’s frequency, brand guidelines, and engagement goals. Start scheduling 
            from the current date + 1 day.

            {strategy_text}... (full strategy provided as input)

            The output should be a JSON object listing all posts, ensuring a balanced mix of content pillars
            and campaign activities.
        """),
        agent=agent,
        expected_output=dedent("""
            A JSON string containing a list of posts, each with:
            - platform: "Instagram" or "LinkedIn"
            - content_type: e.g., "Image", "Reel", "Article"
            - pillar_or_campaign: e.g., "Industry Insights", "Ask the Expert"
            - description: Brief description of the post content
            - week: Integer (1 to 8)
            - day: e.g., "Monday"
            - date: e.g., "2025-04-15"
            - datetime: e.g., "2025-04-15 11:00:00 EST"
            - time: e.g., "11:00 AM EST"
        """)
    )

# Main function to run the scheduler
def generate_content_schedule(strategy_text: str) -> Dict:
    logger.info("Starting content scheduling process")
    try:
        # Instantiate agent
        scheduler = scheduler_agent()

        # Define task
        task = scheduler_task(scheduler, strategy_text)

        # Define Crew
        crew = Crew(
            agents=[scheduler],
            tasks=[task],
            verbose=True
        )

        # Run the crew
        result = crew.kickoff(inputs={"strategy_text": strategy_text})

        # Parse the output (expecting JSON string)
        result_str = result if isinstance(result, str) else result.raw
        # Strip markdown-like ```json markers if present
        result_str = result_str.replace("```json\n", "").replace("\n```", "").strip()
        schedule = json.loads(result_str)
        
        # Ensure the output is a list
        if isinstance(schedule, dict) and "posts" in schedule:
            schedule = schedule["posts"]
        elif not isinstance(schedule, list):
            raise ValueError("Expected a list of posts, but got a different structure")

        logger.info("Content schedule generated successfully with %d posts", len(schedule))
        return schedule
    except Exception as e:
        logger.error("Error in content scheduling: %s", str(e))
        raise

# # Example usage
# if __name__ == "__main__":
#     try:
#         schedule = generate_content_schedule(CONTENT_STRATEGY)
#         print(json.dumps(schedule, indent=2))
#     except Exception as e:
#         print(f"Failed to generate schedule: {e}")