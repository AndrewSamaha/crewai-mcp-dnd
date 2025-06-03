from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters
import dotenv
import os
import warnings
from pydantic import PydanticDeprecatedSince20
from uuid import uuid4
from crewai import LLM
import instrumentation.langfuse
import openlit

openlit.init()

llm = LLM(
    model="openai/gpt-4o-mini", # call model by provider/model_name
    temperature=0.8,
    max_tokens=350,
    top_p=0.9,
    frequency_penalty=0.1,
    presence_penalty=0.1,
    stop=["END"],
    api_key=os.getenv("OPENAI_API_KEY")
)

warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)

dotenv.load_dotenv()

character_description = input("What kind of character do you want me to make? ")

crew_input = {
    "request_id": str(uuid4()),
    "description": character_description,
    "game_id": os.getenv("GAME_ID")
}

server_params_list = [
    StdioServerParameters(
        command="python3", 
        args=["servers/character_maker.py"],
        env={"UV_PYTHON": "3.12", **os.environ},
    ),
    StdioServerParameters(
        command="python3", 
        args=["servers/json_file_tool.py"],
        env={"UV_PYTHON": "3.12", **os.environ},
    ),
]

# Use the StdioServerParameters object to create a MCPServerAdapter
with MCPServerAdapter(server_params_list) as aggregated_tools:
    print(f"Available tools from Stdio MCP server: {[tool.name for tool in aggregated_tools]}")
    agent = Agent(
        role="Character Maker",
        goal="Make a character for the player.",
        backstory="An experienced Dungeon Master that can make characters for the player.",
        tools=aggregated_tools,
        verbose=True,
        llm=llm
    )
    character_creation_task = Task(
        name="character_creation",
        description="Make a character for the user's request with this description: '{description}'. Here is the request ID: '{request_id}' and the game ID: '{game_id}'. Do not make up values, just pass whatever values the user gives you to the tool and let it do the rest.",
        expected_output="The resulting game entity (character) as a dictionary.",
        agent=agent,
        verbose=True,
    )

    personality_agent = Agent(
        role="Personality-Profile Scribe of The Forgotten Realms",
        goal="Forge a vivid 40- to 80-word personality_profile for the provided character JSON, capturing temperament, one driving ideal or bond, and one flaw or vulnerability, in third-person present tense, free of game-mechanic jargon.",
        backstory="You are a centuries-old elven chronicler who wandered every corner of Faerûn recording the quirks of heroes and horrors alike. Having studied Kenku street slang, draconic court etiquette, and even the silent rages of oozes, you distill lifetimes of observation into tight, flavorful prose. Your calling is to gift Game Masters an instant spark for role-play—never padding words, never revealing dice math, always spotlighting what makes each soul unforgettable.",
        tools=aggregated_tools,
        verbose=True,
        llm=llm
    )
    personality_task = Task(
        name="personality_task",
        description="Write a personality_profile for the character below and add it to the character using the tool. Here is the current character:\n\n{character_creation_task.output.raw_output}",
        expected_output="Single 40-80 word sentence fragment",
        agent=personality_agent,
        tools=aggregated_tools,
        verbose=True,
    )

    save_entity_task = Task(
        name="save_entity_task",
        description="Save the game entity (the character) as a JSON file:\n\n{personality_task.output.raw_output}",
        expected_output="The filename where the character was saved.",
        agent=agent,
        verbose=True,
    )
    crew = Crew(
        agents=[agent, personality_agent],
        tasks=[character_creation_task, save_entity_task, personality_task],
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff(inputs=crew_input)
    print(result)