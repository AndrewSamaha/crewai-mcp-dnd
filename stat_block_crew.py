from crewai import Agent, Task, Crew
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters
import dotenv
import os
import warnings
from pydantic import PydanticDeprecatedSince20
from datetime import datetime
from uuid import uuid4

warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)

dotenv.load_dotenv()

# Create a StdioServerParameters object
server_params=StdioServerParameters(
    command="python3", 
    args=["servers/stat_block_maker.py"],
    env={"UV_PYTHON": "3.12", **os.environ},
)

# Use the StdioServerParameters object to create a MCPServerAdapter
with MCPServerAdapter(server_params) as tools:
    print(f"Available tools from Stdio MCP server: {[tool.name for tool in tools]}")
    agent = Agent(
        role="Stat Block Maker",
        goal="Make a stat block for the player.",
        backstory="An experienced Dungeon Master that can make stat blocks for the player.",
        tools=tools,
        verbose=True,
    )
    task = Task(
        description="Make a stat block for the user's request with this description: {description}. Here is the request ID: {request_id}. Do not make up values, just pass whatever values the user gives you to the tool and let it do the rest.",
        expected_output="The result of rolling the dice.",
        agent=agent,
        verbose=True,
    )
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True,
    )
    result = crew.kickoff(inputs={"description": input("What kind of character do you want me to make? "), "request_id": str(uuid4())})
    print(result)