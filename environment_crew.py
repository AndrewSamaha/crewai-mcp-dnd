from instrumentation.langfuse import tracer
from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters
import json
import os

from uuid import uuid4
from crewai import LLM
from utils.game import get_game_information

GAME_ID = os.getenv("GAME_ID")

GAME_INFORMATION = get_game_information(GAME_ID)

crew_input = {
    "request_id": str(uuid4()),
    "description": "The village of Unka",
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

def step_callback(data):
    with tracer.start_span("crew_step_callback") as span:
        span.set_attribute("langfuse.user.id", "user-123")
        span.set_attribute("langfuse.session.id", "123456789")
        span.set_attribute("langfuse.tags", ["staging", "demo"])
        span.set_attribute("client_id", "123456789")
        # check if data is a dictionary
        if isinstance(data, dict):
            span.set_attribute("output.value", json.dumps(data))
        else:
            span.set_attribute("output.value", str(data))
        #span.end()

def task_callback(data):
    with tracer.start_span("crew_task_callback") as span:
        span.set_attribute("langfuse.user.id", "user-123")
        span.set_attribute("langfuse.session.id", "123456789")
        span.set_attribute("langfuse.tags", ["staging", "demo"])
        span.set_attribute("client_id", "123456789")
        # check if data is a dictionary
        if isinstance(data, dict):
            span.set_attribute("output.value", json.dumps(data))
        else:
            span.set_attribute("output.value", str(data))

def callback_factory(span_name: str, tags: list[str] = []):
    def callback(data):
        with tracer.start_span(span_name) as span:
            span.set_attribute("langfuse.user.id", "user-123")
            span.set_attribute("langfuse.session.id", "123456789")
            if tags and len(tags) > 0:
                span.set_attribute("langfuse.tags", tags)
            span.set_attribute("client_id", "123456789")
            # check if data is a dictionary
            if isinstance(data, dict):
                span.set_attribute("output.value", json.dumps(data))
            else:
                span.set_attribute("output.value", str(data))
            span.end()
    return callback

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
        #callback=callback_factory("llm_callback")
    )
    
    with MCPServerAdapter(server_params_list) as aggregated_tools:
        research_agent = Agent(
            role="Lore Archivist of Continuity",
            goal=(
                "Unearth every existing character, item, location or plot thread that "
                "could influence the NEW environment described by the user. Compile a "
                "clear, structured dossier so later agents keep tone, wealth level, "
                "architectural style, alliances and story hooks 100-percent consistent with "
                "established canon."
            ),
            backstory=(
                "You are a meticulous collector and curator of story cannon. You are"
                "excellent at gathering all details related to a topic and compiling them"
                "into a clear and actionable dossier."
            ),
            tools=aggregated_tools,
            verbose=True,
            llm=llm,
        )

        research_task = Task(
            name="gather_lore_context",
            description=(
                "Use the search-oriented tools to locate any *existing* game "
                "entities that relate to the proposed environment: **{description}**.\n"
                "   - Search for characters who own, inhabit or neighbour the space.\n"
                "   - Search for previously created environments that share location,\n"
                "     culture, wealth level or architectural style.\n"
                "   - Summarise findings in a JSON object with keys:\n"
                "   - related_entities\n"
                "   - list of IDs or filenames\n"
                "   - narrative_clues\n"
                "   - bullet list of facts that must stay coherent\n"
                "   - tonal_guidelines\n"
                "   - short phrases that describe mood / aesthetic\n\n"
                "Return ONLY this JSON—no extra narration—so the next agent can parse it."
                "Here is the request ID: '{request_id}' and the game ID: '{game_id}'."
            ),
            expected_output="JSON dossier as described above.",
            agent=research_agent,
            verbose=True,
            callback=callback_factory("research_task_callback"),
        )


        environment_creator_agent = Agent(
            role="Environment Creator",
            goal=(
                "Given a brief description of the environment and maybe some expectations about how"
                "the space will be used in the story, elaborate on the description to create a fully"
                "realized space."
            ),
            backstory=(
                "A seasoned Dungeon Master and story creator who can turn descriptions into elaborate"
                "spaces for the story to unfold in rich ways. It is important for game entities to be"
                "consistent with the world in which they exist. So, usually the work flow when creating"
                "a new entity is to first do research by searching for existing entities"
                "(using the find_entities tool) and then create a new entity (using the create_entity tool)."
                "Generally, game entities like characters"
                "and environments need to be CREATED first before they can be SAVED. So, tool calls"
                "should happen in that order -- creation tools return properly formatted JSON objects"
                "and save functions use those as input. Here is some information about the world in"
                "which this story takes place: "
                f"{GAME_INFORMATION['background']}"
            ),
            tools=aggregated_tools,
            verbose=True,
            cache=False,
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
            callback=callback_factory("environment_creation_task_callback", tags=["environment_creation"]),
        )

        save_entity_task = Task(
            name="save_entity_task",
            description="Save the game entity (the environment) as a JSON file:\n\n{environment_creation_task.output.raw_output}",
            expected_output="The filename where the environment was saved and looks something like this: The_Barbers_Tavern.3d0dc1e1-89de-497c-9d43-9ba9b8442744.json",
            agent=environment_creator_agent,
            verbose=True,
            callback=callback_factory("save_entity_task_callback"),
        )

    
        crew = Crew(
            agents=[research_agent, environment_creator_agent],
            tasks=[research_task, environment_creation_task, save_entity_task],
            process=Process.sequential,
            verbose=True,
            step_callback=step_callback,
            task_callback=task_callback,
        )
        result = crew.kickoff(inputs=crew_input)
        print(result)
        span.set_attribute("input.value", json.dumps(crew_input))
        span.set_attribute("output.value", str(result))

