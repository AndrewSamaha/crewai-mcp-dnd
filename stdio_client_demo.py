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
    args=["servers/dice_server.py"],
    env={"UV_PYTHON": "3.12", **os.environ},
)

# Use the StdioServerParameters object to create a MCPServerAdapter
with MCPServerAdapter(server_params) as tools:
    print(f"Available tools from Stdio MCP server: {[tool.name for tool in tools]}")
    agent = Agent(
        role="Dice Roller",
        goal="Roll dice for the player.",
        backstory="An experienced Dungeon Master that can roll dice for the player.",
        tools=tools,
        verbose=False,
    )
    task = Task(
        description="Roll {dice} for the user's request. Here is the request ID: {request_id}",
        expected_output="The result of rolling the dice.",
        agent=agent,
        verbose=False,
    )
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=False,
    )
    result = crew.kickoff(inputs={"dice": input("What dice do you need to have rolled? "), "request_id": str(uuid4())})
    print(result)