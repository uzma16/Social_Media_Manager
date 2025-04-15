import json
from crewai import Agent, Task, Crew
# from crewai_tools import tool
from textwrap import dedent
# from openai import OpenAI
from dotenv import load_dotenv
import os
import logging
from typing import Dict
from crewai.tools import tool 

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

# Tool to generate social media content
@tool
def content_generator_tool(post_details: str) -> str:
    """Generate social media content based on provided post details in JSON format."""
    logger.info("Generating content for post")
    
    try:
        # Parse JSON input
        if isinstance(post_details, str):
            details = json.loads(post_details)
        else:
            details = post_details  # If it's already a dict

        # Validate required fields
        required_fields = ["platform", "content_type", "pillar_or_campaign", "description", "week", "day", "time"]
        missing_fields = [field for field in required_fields if field not in details]
        
        if missing_fields:
            # Provide default values for missing fields
            defaults = {
                "platform": "LinkedIn",  # Default platform
                "content_type": "Post",  # Default content type
                "pillar_or_campaign": "General",  # Default pillar
                "description": "Professional content for social media",  # Default description
                "week": 1,  # Default week
                "day": "Monday",  # Default day
                "time": "9:00 AM EST"  # Default time
            }
            
            # Fill in missing fields with defaults
            for field in missing_fields:
                details[field] = defaults[field]
                logger.warning(f"Using default value for missing field '{field}': {defaults[field]}")

        # Adjust content type for Instagram (no "Article", use Carousel instead)
        content_type = details["content_type"]
        if details["platform"] == "Instagram" and content_type == "Article":
            content_type = "Carousel"
            logger.info("Adjusted content_type from Article to Carousel for Instagram")

        prompt = f"""
        You are a social media content creator tasked with generating a complete post for {details['platform']} 
        based on the following details:

        Platform: {details['platform']}
        Content Type: {content_type}
        Pillar/Campaign: {details['pillar_or_campaign']}
        Description: {details['description']}
        Week: {details['week']}
        Day: {details['day']}
        Time: {details['time']}

        Create a post that includes:
        1. A concise, engaging caption
        2. 5-8 relevant hashtags
        3. A description of the visual content

        The content should be professional, formal, and minimalist in style, targeting tech-savvy professionals.

        Return the response in this JSON format:
        {{
            "caption": "Your caption here",
            "hashtags": ["hash1", "hash2", "hash3"],
            "visual_description": "Description of the visual content",
            "platform": "{details['platform']}",
            "week": {details['week']},
            "day": "{details['day']}",
            "time": "{details['time']}"
        }}
        """

        # Generate content using LLM
        response = llm.invoke(prompt)
        
        # Ensure the response is properly formatted as JSON
        try:
            # Try to parse the response as JSON
            json_response = json.loads(response.content)
            return json.dumps(json_response)
        except json.JSONDecodeError:
            # If response is not JSON, create a structured response
            formatted_response = {
                "caption": response.content[:200],  # Truncate long responses
                "hashtags": ["#professional", "#business", "#innovation"],  # Default hashtags
                "visual_description": "Minimalist professional design with brand colors",
                "platform": details['platform'],
                "week": details['week'],
                "day": details['day'],
                "time": details['time']
            }
            return json.dumps(formatted_response)

    except Exception as e:
        logger.error(f"Error in content generation: {str(e)}")
        raise ValueError(f"Content generation failed: {str(e)}")

# Agent to handle content generation
def content_generator_agent():
    return Agent(
        role="Social Media Content Creator",
        goal="Generate platform-specific social media content based on post details",
        backstory=dedent("""
            A skilled content specialist with expertise in crafting professional, engaging social media posts
            that adhere to brand guidelines and resonate with targeted audiences. Proficient in creating
            minimalist visuals and formal, impactful captions to drive engagement.
        """),
        tools=[content_generator_tool],
        llm=llm,
        verbose=True
    )

# Task to generate content
def content_generator_task(agent, post_details):
    return Task(
        description=dedent(f"""
    Generate a complete social media post based on the provided JSON details, including a caption,
    hashtags, and visual description. The content must align with a professional voice, formal tone,
    and minimalist visual style, targeting a tech-savvy audience aged 25-34. Adapt the content type
    if needed (e.g., convert Article to Carousel for Instagram).

    Post Details (JSON): {post_details}

    The output should be a JSON object with caption, hashtags, visual description, and post metadata.
    """),
        agent=agent,
        expected_output=dedent("""
            A JSON string containing:
            - caption: The post caption (e.g., under 150 chars for Instagram)
            - hashtags: List of 5-8 relevant hashtags
            - visual_description: Description of minimalist visual(s)
            - platform: Platform name
            - week: Week number
            - day: Day of the week
            - time: Posting time (EST)
        """)
    )

# Main function to run the content generator
def text_generator(post_details: Dict) -> Dict:
    logger.info("Starting content generation process")
    try:
        # Convert input dict to JSON string for tool
        post_details_json = json.dumps(post_details)

        # Instantiate agent
        creator = content_generator_agent()

        # Define task
        task = content_generator_task(creator, post_details_json)
        print("----")
        # Define Crew
        crew = Crew(
            agents=[creator],
            tasks=[task],
            verbose=True
        )

        # Run the crew
        result = crew.kickoff(inputs={"post_details": post_details_json})

        # Parse the output (expecting JSON string)
        content = json.loads(result.tasks_output[0].output)
        logger.info("Content generated successfully")
        return content
    except Exception as e:
        logger.error("Error in content generation: %s", str(e))
        raise

# Example usage
if __name__ == "__main__":
    example_post = {
        "platform": "Instagram",
        "content_type": "Article",
        "pillar_or_campaign": "Industry Insights",
        "description": "Share a key industry statistic with a minimalist visual.",
        "week": 1,
        "day": "Monday",
        "time": "11:00 AM EST"
    }
    # try:
    content = generate_post_content(example_post)
    print(json.dumps(content, indent=2))
    # except Exception as e:
    #     print(f"Failed to generate content: {e}")