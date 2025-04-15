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
        goal="Generate platform-specific social media content based on post details, post should be of high-quality, engaging, and SEO-optimized blog posts for given platform based on specified topics.",
        backstory=dedent("""
            A skilled content specialist with expertise in crafting professional, engaging social media posts
            that adhere to brand guidelines and resonate with targeted audiences. Proficient in creating
            minimalist visuals and formal, impactful captions to drive engagement.
            As a Content Creation Agent, I am designed to assist bloggers and content creators by automating the process of writing. 
            Leveraging advanced AI capabilities, I synthesize information from various sources to produce coherent, insightful,
            and engaging articles that resonate with readers and adhere to SEO best practices.
        """),
        tools=[content_generator_tool],
        llm=llm,
        verbose=True
    )

# Task to generate content
def content_generator_task(agent, platform,description):
    return Task(
            description=dedent(f"""
                Generate engaging and platform-optimized content for {platform}. The content should be tailored to the platform's audience and adhere to its specific formatting and content guidelines.

                The content must be compelling, providing valuable insights and narratives that resonate with the audience. It should also be optimized for SEO if applicable, incorporating relevant keywords to enhance visibility and engagement.

                Platform: {platform}
                Content Description/Title/Topic: {description}
                Ensure the content strictly adheres to the specified word count range to maintain the effectiveness and appropriateness for the platform. No need to give any extra thing other than content.
            """),
            agent=agent,
            expected_output=f"A fully tailored, engaging, and platform-optimized post ready for publication on {platform}, incorporating the provided descriptions and adhering to the platform's content guidelines."
        )

# Main function to run the content generator
import json
import logging
from crewai import Crew

logger = logging.getLogger(__name__)

def text_generator(platform, description):
    logger.info("Starting content generation process")
    try:
        # Prepare input dictionary
        post_details = {
            "platform": platform,
            "description": description
        }
        post_details_json = json.dumps(post_details)

        # Instantiate agent (assuming content_generator_agent is defined elsewhere)
        creator = content_generator_agent()

        # Define task (assuming content_generator_task is defined elsewhere)
        task = content_generator_task(creator, platform, description)

        # Define Crew
        crew = Crew(
            agents=[creator],
            tasks=[task],
            verbose=True
        )

        # Run the crew
        result = crew.kickoff(inputs={"post_details": post_details_json})

        # Parse the output
        content = json.loads(result.tasks_output[0].output)
        logger.info("Content generated successfully")
        return content

    except json.JSONDecodeError as e:
        logger.error("JSON parsing error: %s", str(e))
        raise
    except Exception as e:
        logger.error("Error in content generation: %s", str(e))
        raise

# # Example usage
# if __name__ == "__main__":
#     example_post = {
#         "platform": "Instagram",
#         "content_type": "Article",
#         "pillar_or_campaign": "Industry Insights",
#         "description": "Share a key industry statistic with a minimalist visual.",
#         "week": 1,
#         "day": "Monday",
#         "time": "11:00 AM EST"
#     }
#     # try:
#     content = generate_post_content(example_post)
#     print(json.dumps(content, indent=2))
    # except Exception as e:
    #     print(f"Failed to generate content: {e}")