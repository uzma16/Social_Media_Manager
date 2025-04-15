from crewai import Agent, Task, Crew
from langchain.tools import Tool
import os

# Define Agents
class ContentCreationCrew:
    def __init__(self):
        # Agent 1: Content Strategist
        self.content_strategist = Agent(
            role='Content Strategist',
            goal='Analyze the description and determine the best content approach for the specified platform',
            backstory='Experienced digital marketer with expertise in platform-specific content strategies',
            verbose=True,
            allow_delegation=False
        )

        # Agent 2: Image Creator
        self.image_creator = Agent(
            role='Image Creator',
            goal='Generate image based on the description and platform requirements',
            backstory='Creative designer skilled in visual storytelling and image generation',
            verbose=True,
            allow_delegation=False
        )

        # Agent 3: Copywriter
        self.copywriter = Agent(
            role='Copywriter',
            goal='Write platform-specific post text to accompany the image',
            backstory='Professional writer adept at crafting engaging posts for various social platforms',
            verbose=True,
            allow_delegation=False
        )

    # Define Tasks
    def create_content(self, description: str, platform: str):
        # Task 1: Content Strategy
        strategy_task = Task(
            description=f'''Analyze this description: "{description}" and determine the best content approach 
            for {platform}. Specify tone, style, and key elements to include in both image and text.''',
            agent=self.content_strategist,
            expected_output='Content strategy plan with tone, style, and key elements'
        )

        # Task 2: Image Creation
        image_task = Task(
            description=f'''Based on the content strategy, create a description for an image that would 
            effectively convey the message for {platform}. The original description is: "{description}"''',
            agent=self.image_creator,
            expected_output='Detailed image description ready for generation'
        )

        # Task 3: Post Writing
        post_task = Task(
            description=f'''Write a {platform}-specific post to accompany the image, based on the content 
            strategy and the original description: "{description}". Adjust tone and style accordingly.''',
            agent=self.copywriter,
            expected_output=f'{platform}-formatted post text'
        )

        # Create and run the crew
        crew = Crew(
            agents=[self.content_strategist, self.image_creator, self.copywriter],
            tasks=[strategy_task, image_task, post_task],
            verbose=2
        )
        
        return crew.kickoff()

# Platform-specific formatting guidelines
def format_post(platform: str, text: str) -> str:
    if platform.lower() == 'linkedin':
        return f"{text}\n\n#ProfessionalDevelopment #IndustryInsights"
    elif platform.lower() == 'twitter' or platform.lower() == 'x':
        return f"{text[:260]} #ContentCreation"
    elif platform.lower() == 'instagram':
        return f"{text}\n.\n.\n#VisualStorytelling #CreativeContent"
    else:
        return text

# Example Usage
def image_generator():
    # Sample description and platform
    description = "A team of developers working together on an innovative AI project"
    platform = "LinkedIn"  # Can be changed to Twitter/X, Instagram, etc.

    # Initialize crew
    content_crew = ContentCreationCrew()
    
    # Execute tasks
    result = content_crew.create_content(description, platform)
    
    # Extract results (assuming CrewAI returns results in a structured way)
    strategy = result.tasks[0].output
    image_desc = result.tasks[1].output
    post_text = result.tasks[2].output
    
    # Format the post
    formatted_post = format_post(platform, post_text)
    
    # Output results
    print(f"\nContent Strategy:\n{strategy}")
    print(f"\nImage Description:\n{image_desc}")
    print(f"\nFormatted {platform} Post:\n{formatted_post}")
    
    # Note: Actual image generation would require confirmation and an external tool
    print("\nNote: To generate the actual image based on the description above, please confirm.")

if __name__ == "__main__":
    image_generator()