from crewai import Agent, Task

def build_environment_creator_agent(llm, tools, game_information):
    return Agent(
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
                f"{game_information['background']}"
            ),
            tools=tools,
            verbose=True,
            cache=False,
            llm=llm,
        )

def build_environment_creation_task(agent, callback_factory):
    return Task(
            name="environment_creation",
            description=(
                "Use the appropriate tools to create an environment for the user's request with this "
                "description: '{description}'. "
                "Here is the request ID: '{request_id}' and the game ID: '{game_id}'. "
                "Be creative and elaborate in rich detail for story and game hooks."
            ),
            expected_output="The resulting game entity (environment) as a dictionary.",
            agent=agent,
            verbose=True,
            callback=callback_factory("environment_creation_task_callback", tags=["environment_creation"]),
        )