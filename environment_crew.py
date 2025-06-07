from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters

import os

from uuid import uuid4
from crewai import LLM

import instrumentation.langfuse
from utils.game import get_game_information

GAME_ID = os.getenv("GAME_ID")

GAME_INFORMATION = get_game_information(GAME_ID)
print(GAME_INFORMATION)

llm = LLM(
    model="openai/gpt-4o-mini", # call model by provider/model_name
    temperature=0.8,
    max_tokens=500,
    top_p=0.9,
    frequency_penalty=0.1,
    presence_penalty=0.1,
    stop=["END"],
    api_key=os.getenv("OPENAI_API_KEY")
)

crew_input = {
    "request_id": str(uuid4()),
    "description": "The kitchen in Eataiouth's house.",
    "game_id": os.getenv("GAME_ID")
}

server_params_list = [
    StdioServerParameters(
        command="python3", 
        args=["servers/game_entity_maker.py"],
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

    environment_creator_agent = Agent(
        role="Environment Creator",
        goal=(
            "Given a brief description of the environment and maybe some expectations about how"
            "the space will be used in the story, elaborate on the description to create a fully"
            "realized space."
        ),
        backstory=(
            "A seasoned Dungeon Master and story creator who can turn descriptions into elaborate"
            "spaces for the story to unfold in rich ways. Generally, game entities like characters"
            "and environments need to be CREATED first before they can be SAVED. So, tool calls"
            "should happen in that order -- creation tools return properly formatted JSON objects"
            "and save functions use those as input. Here is some information about the world in"
            "which this story takes place: "
            f"{GAME_INFORMATION['background']}"
        ),
        tools=aggregated_tools,
        verbose=True,
        llm=llm,
    )

    environment_creation_task = Task(
        name="environment_creation",
        description=(
            "Use the appropriate tools to create an environment for the user's request with this"
            "description: '{description}'."
            "Here is the request ID: '{request_id}' and the game ID: '{game_id}'."
            "Be creative and elaborate in rich detail for story and game hooks"
        ),
        expected_output="The resulting game entity (environment) as a dictionary.",
        agent=environment_creator_agent,
        verbose=True,
    )

    save_entity_task = Task(
        name="save_entity_task",
        description="Save the game entity (the environment) as a JSON file:\n\n{environment_creation_task.output.raw_output}",
        expected_output="The filename where the environment was saved and looks something like this: The_Barbers_Tavern.3d0dc1e1-89de-497c-9d43-9ba9b8442744.json",
        agent=environment_creator_agent,
        verbose=True,
    )

    crew = Crew(
        agents=[environment_creator_agent],
        tasks=[environment_creation_task, save_entity_task],
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff(inputs=crew_input)
    print(result)