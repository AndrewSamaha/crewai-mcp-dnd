from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters

import os

from uuid import uuid4
from crewai import LLM

import instrumentation.langfuse



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

history = [
    {
        "character_id": "eca9aecd-dfa3-4308-b621-b2f4a05cbad3",
        "character_name": "Aentzheigkeishcrast",
        "action": "says: Eetaiouth, you're doing the right thing by staying home and not going to the tavern to confront Bruaplueshee. The town folk will surely see through his lies without your testimony."
    },
    {
        "character_id": "3f42730a-78d0-4448-b15b-b43ecb787c2c",
        "character_name": "Vejeafoeaest",
        "action": "says: Eataiouth, that's ridiculous! You need to do something to stop Bruaplueshee from lying to the town folk. He's dangerous and a murderer!"
    },
]

crew_input = {
    "request_id": str(uuid4()),
    "current_character_id": "924c2dce-33a7-48a0-90ef-3ac7bee36070",
    "current_character_name": "Eataiouth",
    "history": history,
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
    intention_planning_agent = Agent(
        role="Character Intention Planner",
        goal="Plan the next action for the character.",
        backstory="An experienced Dungeons and Dragons player that can assume the role of the character and use it to plan the character's next intentions given the recent history.",
        tools=aggregated_tools,
        verbose=True,
        llm=llm
    )
    intention_planning_task = Task(
        name="intention_planning",
        description="Plan the next action for the character named '{current_character_name}', id '{current_character_id}'. Here is a list of recent events: '{history}'. Here is the request ID: '{request_id}' and the game ID: '{game_id}'. Use tools to get the character's personality profile and other relevant information before deciding two things: the very next thing he intends to do AND the rational for doing that.",
        expected_output="A brief summary of the character's intentions.",
        agent=intention_planning_agent,
        verbose=True,
    )

    crew = Crew(
        agents=[intention_planning_agent],
        tasks=[intention_planning_task],
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff(inputs=crew_input)
    print(result)