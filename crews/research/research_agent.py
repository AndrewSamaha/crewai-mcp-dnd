from crewai import Agent

def build_research_agent(llm, tools):
    return Agent(
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
        tools=tools,
        verbose=True,
        llm=llm,
        cache=False
    )