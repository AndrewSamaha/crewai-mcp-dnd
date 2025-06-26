from crewai import Task

def build_research_task(agent, callback_factory):
    return Task(
        name="gather_lore_context",
        description=(
            "Use the search-oriented tools to locate any *existing* game "
            "entities that relate to the proposed environment: **{description}**.\n"
            "In some cases, you made need to perform more than one search. E.g.,\n"
            "If the input contains two nouns (e.g., the belrak from Ontabia),\n"
            "then you should conduct two separate searches. One for 'belrak' and one for 'Ontabia'.\n"
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
        agent=agent,
        verbose=True,
        callback=callback_factory("research_task_callback"),
    )