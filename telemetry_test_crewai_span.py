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

llm = LLM(
    model="openai/gpt-4o-mini", # call model by provider/model_name
    temperature=0.8,
    max_tokens=1_000,
    top_p=0.9,
    frequency_penalty=0.1,
    presence_penalty=0.1,
    stop=["END"],
    api_key=os.getenv("OPENAI_API_KEY")
)

crew_input = {
    "request_id": str(uuid4()),
    "description": "The village of Varatoba",
    "game_id": os.getenv("GAME_ID")
}

environment_creator_agent = Agent(
  role="Environment Creator",
  goal=(
      "Given a brief description of the environment and maybe some expectations about how"
      "the space will be used in the story, elaborate on the description to create a fully"
      "realized space. Return ONLY this JSON—no extra narration—so the next agent can parse it."
  ),
  backstory=(
      "A seasoned Dungeon Master and story creator who can turn descriptions into elaborate"
      "spaces for the story to unfold in rich ways. It is important for game entities to be"
      "consistent with the world in which they exist. So, usually the work flow when creating"
      "a new entity is to first do research by searching for existing entities"
      "(using the find_entities tool) and then create a new entity (using the create_entity tool)."
      "Generally, game entities like characters"
      "and environments need to be CREATED first before they can be SAVED. Here is some information about the world in"
      "which this story takes place: "
      f"{GAME_INFORMATION['background']}"
  ),
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

with tracer.start_as_current_span("OpenAI-Trace") as span:
  span.set_attribute("langfuse.user.id", "user-123")
  span.set_attribute("langfuse.session.id", "123456789")
  span.set_attribute("langfuse.tags", ["staging", "demo"])


  crew = Crew(
    agents=[environment_creator_agent],
    tasks=[environment_creation_task],
    process=Process.sequential,
    verbose=True,
  )
  result = crew.kickoff(inputs=crew_input)
  span.set_attribute("input.value", json.dumps(crew_input))
  span.set_attribute("output.value", result)
  print(result)