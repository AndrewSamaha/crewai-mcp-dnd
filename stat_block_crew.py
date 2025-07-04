from crewai import Agent, Task, Crew
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters
import dotenv
import os
import warnings
from pydantic import PydanticDeprecatedSince20
from datetime import datetime
from uuid import uuid4
from crewai import LLM

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
        args=["servers/stat_block_maker.py"],
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
        role="Stat Block Maker",
        goal="Make a stat block for the player.",
        backstory="An experienced Dungeon Master that can make stat blocks for the player.",
        tools=aggregated_tools,
        verbose=True,
        llm=llm
    )
    task = Task(
        description="Make a stat block for the user's request with this description: '{description}'. Here is the request ID: '{request_id}' and the game ID: '{game_id}'. Do not make up values, just pass whatever values the user gives you to the tool and let it do the rest.",
        expected_output="The resulting game entity (stat block) as a dictionary.",
        agent=agent,
        verbose=True,
    )
    save_entity_task = Task(    
        description="Save the game entity (the stat block) as a JSON file.",
        expected_output="The filename where the stat block was saved.",
        agent=agent,
        verbose=True,
    )
    crew = Crew(
        agents=[agent],
        tasks=[task, save_entity_task],
        verbose=True,
    )
    result = crew.kickoff(inputs=crew_input)
    print(result)