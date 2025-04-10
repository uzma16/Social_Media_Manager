import os
from crewai import Agent, Task, Crew
from crewai.tools import tool  # Import tool decorator from crewai_tools
from openai import OpenAI
from config.database import get_db_connection
import json
import shutil
from textwrap import dedent
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    api_key=""
)



# Define Tools using @tool decorator
# Define your tools with @tool (singular)
@tool
def store_inputs_tool(brand_guidelines: dict, goals: str, target_audience: dict, platforms: dict, logos: list, fonts: list, templates: list, past_data: object) -> str:
    """Store user inputs in the database and filesystem."""
    db = get_db_connection()  # Assuming this function is defined elsewhere
    with db.cursor() as cursor:
        cursor.execute("""
            INSERT INTO setups (brand_guidelines, goals, target_audience, platforms)
            VALUES (%s, %s, %s, %s)
        """, (json.dumps(brand_guidelines), goals, json.dumps(target_audience), json.dumps(platforms)))
        db.commit()

    base_path = "backend/data/assets/"
    for logo in logos or []:
        with open(f"{base_path}logos/{logo.filename}", "wb") as f:
            shutil.copyfileobj(logo.file, f)
    for font in fonts or []:
        with open(f"{base_path}fonts/{font.filename}", "wb") as f:
            shutil.copyfileobj(font.file, f)
    for template in templates or []:
        with open(f"{base_path}templates/{template.filename}", "wb") as f:
            shutil.copyfileobj(template.file, f)
    if past_data:
        with open(f"{base_path}past_data/{past_data.filename}", "wb") as f:
            shutil.copyfileobj(past_data.file, f)
    return "Inputs stored successfully"

@tool
def parse_guidelines_tool(guidelines: dict) -> dict:
    """Parse brand guidelines into a structured profile using NLP."""
    nlp = pipeline("text-classification", model="distilbert-base-uncased")
    tone_analysis = nlp(guidelines["tone"])[0]
    voice_analysis = nlp(guidelines["voice"])[0]
    
    return {
        "voice": guidelines["voice"],
        "tone": guidelines["tone"],
        "keywords": [word for word in guidelines["voice"].split() if len(word) > 3],
        "sentiment_score": tone_analysis["score"],
        "visual_style": guidelines["visual_style"],
        "dos_donts": guidelines["dos_donts"]
    }

@tool
def validate_inputs_tool(brand_guidelines: dict, goals: str, target_audience: dict, platforms: dict) -> str:
    """Validate completeness of user inputs."""
    missing = []
    if not brand_guidelines["voice"] or not brand_guidelines["tone"]:
        missing.append("Brand voice or tone")
    if not goals:
        missing.append("Goals")
    if not target_audience["demographics"]:
        missing.append("Audience demographics")
    if not platforms["names"]:
        missing.append("Platforms")
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    return "Inputs validated successfully"

@tool
def generate_strategy_tool(brand_guidelines: dict, goals: str, target_audience: dict, platforms: dict) -> str:
    """Generate an initial content strategy using OpenAI."""
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"""
    Generate an initial social media content strategy based on:
    - Brand Guidelines: Voice={brand_guidelines['voice']}, Tone={brand_guidelines['tone']}
    - Goals: {goals}
    - Target Audience: {target_audience['demographics']}, {target_audience['psychographics']}
    - Platforms: {', '.join(platforms['names'])}
    """
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return response.choices[0].message.content

# Helper method for tip section
def __tip_section():
    return dedent("""
        Ensure all outputs are accurate and aligned with the provided inputs.
        Double-check data integrity and consistency before finalizing.
    """)

# Define Agents
def storage_agent(self):
    return Agent(
        role="Data Storage Expert",
        goal="Securely store user inputs in the database and filesystem",
        backstory=dedent("""
            A meticulous specialist in data persistence, ensuring all user-provided
            information and assets are safely stored for future use.
        """),
        tools=[store_inputs_tool],
        verbose=True
    )

def parser_agent(self):
    return Agent(
        role="Brand Guideline Analyst",
        goal="Analyze and distill brand guidelines into a structured profile using NLP",
        backstory=dedent("""
            A skilled expert in natural language processing, adept at extracting key
            elements of brand identity to create actionable profiles.
        """),
        tools=[parse_guidelines_tool],
        verbose=True
    )

def validator_agent(self):
    return Agent(
        role="Input Validation Specialist",
        goal="Ensure all required user inputs are complete and valid",
        backstory=dedent("""
            A detail-oriented checker with a keen eye for spotting missing or
            inconsistent data, ensuring a solid foundation for the system.
        """),
        tools=[validate_inputs_tool],
        verbose=True
    )

def strategy_agent(self):
    return Agent(
        role="Content Strategy Creator",
        goal="Create an initial content strategy tailored to user inputs",
        backstory=dedent("""
            A creative strategist with expertise in leveraging AI to craft effective
            social media plans based on brand and audience insights.
        """),
        tools=[generate_strategy_tool],
        verbose=True
    )

# Define Tasks
def store_task(self, agent, brand_guidelines, goals, target_audience, platforms, logos, fonts, templates, past_data):
    return Task(
        description=dedent(f"""
            Store all user-provided inputs securely in the database and filesystem.
            This task involves saving structured data like brand guidelines, goals,
            target audience, and platforms in a PostgreSQL database, as well as
            storing uploaded assets (logos, fonts, templates, and past data) in
            the appropriate filesystem directories.

            {self.__tip_section()}

            Brand Guidelines: {json.dumps(brand_guidelines)}
            Goals: {goals}
            Target Audience: {json.dumps(target_audience)}
            Platforms: {json.dumps(platforms)}
            Logos: {', '.join([logo.filename for logo in logos]) if logos else 'None'}
            Fonts: {', '.join([font.filename for font in fonts]) if fonts else 'None'}
            Templates: {', '.join([template.filename for template in templates]) if templates else 'None'}
            Past Data: {past_data.filename if past_data else 'None'}
        """),
        agent=agent,
        expected_output="Confirmation message: 'Inputs stored successfully'"
    )

def parse_task(self, agent, brand_guidelines):
    return Task(
        description=dedent(f"""
            Analyze and distill the provided brand guidelines into a structured,
            machine-readable voice profile using NLP. This task involves extracting
            key elements like voice, tone, keywords, sentiment, visual style, and
            dos/don'ts to create a comprehensive brand identity profile.

            {self.__tip_section()}

            Brand Guidelines: {json.dumps(brand_guidelines)}
        """),
        agent=agent,
        expected_output="JSON object with voice, tone, keywords, sentiment, visual style, and dos/don'ts"
    )

def validate_task(self, agent, brand_guidelines, goals, target_audience, platforms):
    return Task(
        description=dedent(f"""
            Validate the completeness and validity of all user inputs. This task
            involves checking for required fields such as brand voice, tone, goals,
            audience demographics, and platforms, raising an error if any are missing.

            {self.__tip_section()}

            Brand Guidelines: {json.dumps(brand_guidelines)}
            Goals: {goals}
            Target Audience: {json.dumps(target_audience)}
            Platforms: {json.dumps(platforms)}
        """),
        agent=agent,
        expected_output="Confirmation message: 'Inputs validated successfully' or error if missing fields"
    )

def strategy_task(self, agent, brand_guidelines, goals, target_audience, platforms):
    return Task(
        description=dedent(f"""
            Generate an initial social media content strategy tailored to the user’s
            inputs using OpenAI. This task involves creating a detailed plan based on
            brand guidelines, goals, target audience, and selected platforms, ensuring
            alignment with the brand’s identity and objectives.

            {self.__tip_section()}

            Brand Guidelines: {json.dumps(brand_guidelines)}
            Goals: {goals}
            Target Audience: {json.dumps(target_audience)}
            Platforms: {json.dumps(platforms)}
        """),
        agent=agent,
        expected_output="Text string containing the initial content strategy"
    )

# Main Function to Process Setup
async def process_setup(brand_guidelines, goals, target_audience, platforms, logos, fonts, templates, past_data):
    # Instantiate agents
    storage = storage_agent(None)
    parser = parser_agent(None)
    validator = validator_agent(None)
    strategist = strategy_agent(None)

    # Define tasks with agents and inputs
    tasks = [
        store_task(None, storage, brand_guidelines, goals, target_audience, platforms, logos, fonts, templates, past_data),
        parse_task(None, parser, brand_guidelines),
        validate_task(None, validator, brand_guidelines, goals, target_audience, platforms),
        strategy_task(None, strategist, brand_guidelines, goals, target_audience, platforms)
    ]

    # Define Crew
    setup_crew = Crew(
        agents=[storage, parser, validator, strategist],
        tasks=tasks,
        verbose=2
    )

    # Kick off the crew process
    result = setup_crew.kickoff(inputs={
        "brand_guidelines": brand_guidelines,
        "goals": goals,
        "target_audience": target_audience,
        "platforms": platforms,
        "logos": logos,
        "fonts": fonts,
        "templates": templates,
        "past_data": past_data
    })

    # Extract outputs from tasks
    brand_voice_profile = result.tasks_output[1].output  # From parse_task
    content_strategy = result.tasks_output[3].output     # From strategy_task

    return {
        "brand_voice_profile": brand_voice_profile,
        "content_strategy": content_strategy
    }