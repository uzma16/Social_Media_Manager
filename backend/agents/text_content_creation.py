from crewai import Agent, Task, Crew
from crewai_tools import tool
from openai import OpenAI
import os

# Custom tool to generate content using OpenAI
@tool
def generate_content_tool(title: str, platform: str) -> str:
    """Generate textual content based on a title and adapt it to the specified platform."""
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Define platform-specific styles
    platform_styles = {
        "linkedin": {
            "tone": "professional and polished",
            "length": "200-300 words",
            "style": "structured with insights, value-driven, and a call-to-action"
        },
        "twitter": {
            "tone": "casual and concise",
            "length": "up to 280 characters",
            "style": "witty, direct, and engaging with hashtags"
        },
        "facebook": {
            "tone": "friendly and conversational",
            "length": "100-150 words",
            "style": "story-driven with a personal touch"
        },
        "instagram": {
            "tone": "trendy and visual",
            "length": "50-100 words",
            "style": "captivating with emojis and hashtags"
        }
    }
    
    # Default to a generic style if platform not found
    platform_style = platform_styles.get(platform.lower(), {
        "tone": "neutral",
        "length": "100-200 words",
        "style": "clear and engaging"
    })
    
    # Construct the prompt
    prompt = f"""
    Create a textual post based on the title '{title}' for the platform '{platform}'.
    - Tone: {platform_style['tone']}
    - Length: {platform_style['length']}
    - Style: {platform_style['style']}
    Provide the content as a single paragraph without additional commentary.
    """
    
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

# Define the Content Creator Agent
content_creator_agent = Agent(
    role="Content Creator",
    goal="Generate platform-specific textual content based on a given title",
    backstory="You are a skilled writer with expertise in crafting tailored content for various social media platforms, adapting tone and style to suit each audience.",
    tools=[generate_content_tool],
    verbose=True
)

# Function to create a task dynamically based on title and platform
def create_content_task(title: str, platform: str) -> Task:
    return Task(
        description=f"Generate a textual post for the title '{title}' tailored to the {platform} platform.",
        expected_output=f"A {platform}-specific post based on the title '{title}'.",
        agent=content_creator_agent
    )

# Main function to run the system
def generate_post(title: str, platform: str) -> str:
    # Create the task
    task = create_content_task(title, platform)
    
    # Set up the crew
    crew = Crew(
        agents=[content_creator_agent],
        tasks=[task],
        verbose=True
    )
    
    # Execute the crew and return the result
    result = crew.kickoff()
    return result

# Example usage
if __name__ == "__main__":
    # Set your OpenAI API key as an environment variable or hardcode it (not recommended for production)
    os.environ["OPENAI_API_KEY"] = "your-openai-api-key-here"
    
    # Test cases
    title = "The Future of Artificial Intelligence"
    platforms = ["LinkedIn", "Twitter", "Facebook", "Instagram"]
    
    for platform in platforms:
        print(f"\nPost for {platform}:")
        post = generate_post(title, platform)
        print(post)