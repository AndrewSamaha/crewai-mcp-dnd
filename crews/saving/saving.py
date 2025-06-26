from crewai import Agent, Task

def build_saving_agent(llm, tools):
    return Agent(
            role="Lore Chronicler",
            goal=(
                "Use the tools available to save the entity passed to you."
            ),
            backstory=(
                "You are a meticulous collector and curator of story cannon. You are"
                "excellent at documenting all pieces of history, persons, environments"
                "characters, monsters, and items."
            ),
            tools=tools,
            verbose=True,
            llm=llm,
            cache=False
        )

def build_saving_task(agent, callback_factory):
    return Task(
            name="save_entity_task",
            description=(
                "Use the appropriate tools to save the entity by passing it to the right tool."
            ),
            expected_output="The tool call to save the environment will return the filename where the environment was saved and looks something like this: The_Barbers_Tavern.3d0dc1e1-89de-497c-9d43-9ba9b8442744.json",
            agent=agent,
            verbose=True,
            callback=callback_factory("save_entity_task_callback"),
        )