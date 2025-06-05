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
    {
        "character_id": "924c2dce-33a7-48a0-90ef-3ac7bee36070",
        "character_name": "Eataiouth",
        "action": "stands up and declares, 'I cannot let Bruaplueshee deceive the townsfolk any longer; I will confront him!'",
    }
]

crew_input = {
    "request_id": str(uuid4()),
    "current_character_id": "eca9aecd-dfa3-4308-b621-b2f4a05cbad3",
    "current_character_name": "Aentzheigkeishcrast",
    "history": history,
    "room_description": "Aentzheigkeishcrast, Vegjeafoeaest, and Eataiouth are in Eataiouth's home discussing Bruaplueshee. It's late and raining outside.",
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
        goal=(
            "Given recent history and the character’s full record (stats, personality, "
            "backstory, current conditions, etc.), decide what the character INTENDS to do next."
        ),
        backstory=(
            "A seasoned D&D player who always speaks in-character, framing intentions the same "
            "way a player would tell the DM: clear, actionable, and rooted in role-playing logic."
        ),
        tools=aggregated_tools,
        verbose=True,
        llm=llm,
    )

    lookup_character_task = Task(
        name="lookup_character",
        description="Lookup the character named '{current_character_name}', id '{current_character_id}'.",
        expected_output="The character as a dictionary.",
        agent=intention_planning_agent,
        verbose=True,
    )

    intention_planning_task = Task(
        name="intention_planning",
        description=(
            "## CONTEXT\n"
            "- Character: **{current_character_name}** (id {current_character_id})\n"
            "- Game ID: **{game_id}**, Request ID: **{request_id}**\n"
            "- Room Description: **{room_description}**\n"
            "- Recent events: **{history}**\n\n"
            "- Character: {lookup_character_task.output.raw_output}\n"
            "## INSTRUCTIONS\n"
            "1. Use the available tools to retrieve the character’s **personality_profile**, "
            "current hit points, spell slots, inventory, and any relevant conditions.\n"
            "2. Decide ONE concrete intention—exactly what the character will announce to the DM "
            "on their next turn. Phrase it in first-person present tense (e.g., "
            "“I charge the ogre and swing my greataxe” or “I cast *Hold Person* on the cultist in the rear”).\n"
            "3. Provide a brief **rationale** that cites at least one element from the personality "
            "profile *or* the recent events.\n\n"
            "## OUTPUT FORMAT (Markdown)\n"
            "```yaml\n"
            "intention: <one-sentence, first-person declaration>\n"
            "rationale: <one short sentence referencing personality/history>\n"
            "```\n\n"
            "## EXAMPLES\n"
            "### Example 1\n"
            "History snippet: *The party is pinned down behind crates while hobgoblins fire arrows.*\n"
            "Personality: ‘reckless, loyal, hates ranged combat’\n"
            "\n"
            "```yaml\n"
            "intention: I leap over the crates and rush the nearest hobgoblin, drawing their fire away from my friends!\n"
            "rationale: My recklessness and loyalty drive me to protect the party even if it means exposing myself.\n"
            "```\n"
            "### Example 2\n"
            "History snippet: *The necromancer just raised two skeletons; the cleric is out of spell slots.*\n"
            "Personality: ‘strategic thinker, values efficiency’\n"
            "\n"
            "```yaml\n"
            "intention: I hurl a flask of holy water to shatter between the skeletons and the necromancer.\n"
            "rationale: A single action that can damage multiple undead aligns with my efficiency-first mindset.\n"
            "```\n"
        ),
        expected_output=(
            "A YAML block with **intention** and **rationale** fields exactly as shown above, "
            "no extra keys, no narrative prose."
        ),
        agent=intention_planning_agent,
        verbose=True,
    )


    crew = Crew(
        agents=[intention_planning_agent],
        tasks=[lookup_character_task, intention_planning_task],
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff(inputs=crew_input)
    print(result)