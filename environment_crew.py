from instrumentation.langfuse import tracer, callback_factory
from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters
import json
import os

from uuid import uuid4
from crewai import LLM
from utils.game import get_game_information
from crews.research.research_agent import build_research_agent
from crews.research.research_task import build_research_task
from crews.creation.environment import build_environment_creator_agent, build_environment_creation_task
from crews.saving.saving import build_saving_agent, build_saving_task

GAME_ID = os.getenv("GAME_ID")

GAME_INFORMATION = get_game_information(GAME_ID)

crew_input = {
    "request_id": str(uuid4()),
    "description": "The Great Tree in the center of Unka",
    "game_id": os.getenv("GAME_ID")
}

game_entity_server_params = StdioServerParameters(
    command="python3", 
    args=["-m", "servers.game_entity_maker"],
    env={"UV_PYTHON": "3.12", **os.environ},
)

json_file_tool_server_params = StdioServerParameters(
    command="python3", 
    args=["-m", "servers.json_file_tool"],
    env={"UV_PYTHON": "3.12", **os.environ},
)

server_params_list = [
    game_entity_server_params,
    json_file_tool_server_params,
]

# Use the StdioServerParameters object to create a MCPServerAdapter
with tracer.start_as_current_span("Environment Crew") as span:
    span.set_attribute("langfuse.user.id", "user-123")
    span.set_attribute("langfuse.session.id", "123456789")
    span.set_attribute("langfuse.tags", ["staging", "demo"])
    span.set_attribute("client_id", "123456789")
    
    llm = LLM(
        model="openai/gpt-4o-mini", # call model by provider/model_name
        temperature=0.8,
        max_tokens=1_000,
        top_p=0.9,
        frequency_penalty=0.1,
        presence_penalty=0.1,
        stop=["END"],
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    
    with MCPServerAdapter(game_entity_server_params) as game_entity_tools, MCPServerAdapter(json_file_tool_server_params) as json_file_tools:
        research_agent = build_research_agent(llm, json_file_tools)
        research_task = build_research_task(research_agent, callback_factory)

        environment_creator_agent = build_environment_creator_agent(llm, game_entity_tools, GAME_INFORMATION)
        environment_creation_task = build_environment_creation_task(environment_creator_agent, callback_factory)

        saving_agent = build_saving_agent(llm, json_file_tools)
        save_entity_task = build_saving_task(saving_agent, callback_factory)
    
        crew = Crew(
            agents=[research_agent, environment_creator_agent, saving_agent],
            tasks=[research_task, environment_creation_task, save_entity_task],
            process=Process.sequential,
            verbose=True,
            step_callback=callback_factory("crew_step_callback"),
            task_callback=callback_factory("crew_task_callback"),
        )
        result = crew.kickoff(inputs=crew_input)
        print(result)
        span.set_attribute("input.value", json.dumps(crew_input))
        span.set_attribute("output.value", str(result))

