"""A simple MCP server creates game entities like characters and environments.

This server provides character and environment creation operations as tools that can be discovered and used by MCP clients.
"""

from mcp.server.fastmcp import FastMCP
from typing import Optional
from servers.character_creator.character import build_random_character, log
from servers.environments.environments import Environment
from servers.file_utils.ripgrep import find_entity_by_id
import json
from typing import Dict, List

mcp = FastMCP("Character")

@mcp.tool()
def make_character(
    request_id: str,
    game_id: str,
    description: str,
    name: Optional[str] = None,
    level: Optional[int] = None,
    # cr: Optional[int] = None,
    # strength: Optional[int] = None,
    # dexterity: Optional[int] = None,
    # constitution: Optional[int] = None,
    # intelligence: Optional[int] = None,
    # wisdom: Optional[int] = None,
    # charisma: Optional[int] = None,
    # personality_profile: Optional[str] = None,
    # current_goal: Optional[str] = None
) -> dict:
    """Create a D&D character based on the provided parameters. Only request_id and description are required; other parameters will be filled in deterministically if not provided.
    
    Args:
        request_id (str): The ID of the request.
        game_id (str): The ID of the game.
        description (str): A description of the creature.
        name (Optional[str]): The name of the creature. If None, will be generated from the description.
        level (Optional[int]): The level of the creature. If None, will be determined from the description.
    """
    #  cr (Optional[int]): The challenge rating of the creature. If None, will be determined from the description.
    # strength (Optional[int]): The strength of the creature. If None, will be determined from the description.
    # dexterity (Optional[int]): The dexterity of the creature. If None, will be determined from the description.
    # constitution (Optional[int]): The constitution of the creature. If None, will be determined from the description.
    # intelligence (Optional[int]): The intelligence of the creature. If None, will be determined from the description.
    # wisdom (Optional[int]): The wisdom of the creature. If None, will be determined from the description.
    # charisma (Optional[int]): The charisma of the creature. If None, will be determined from the description.
    # personality_profile (Optional[str]): The personality profile of the creature. If None, will be determined from the description.
    # current_goal (Optional[str]): The current goal of the creature. If None, will be determined from the description.
    log({"name": name}, "Tool Calledmake_character - name")
    character = build_random_character(name=name, description=description, request_id=request_id, game_id=game_id)
    if level and level > 0:
        for _ in range(level):
            character.level_up()
    
    return character.as_dict()

@mcp.tool()
def set_personality_profile(
    request_id: str,
    game_id: str,
    character_id: str,
    personality_profile: str
) -> dict | str:
    """Set the personality profile of the character.
    
    Args:
        request_id (str): The ID of the request.
        game_id (str): The ID of the game.
        character_id (str): The ID of the character to set the personality profile for.
        personality_profile (str): The personality profile of the character.
    Returns:
        dict | str: The character dictionary with the new personality_profile field set, or an error message.
    """
    matches = find_entity_by_id(character_id, game_id, "character")
    if matches:
        character = json.load(open(matches[0]))
        character["personality_profile"] = personality_profile
        with open(matches[0], "w") as f:
            json.dump(character, f)
        return character
    return "ERROR: No game entity found with that id."

@mcp.tool()
def create_environment(
    request_id: str,
    game_id: str,
    name: str,
    kind: str,
    summary: str,
    ambience: Optional[Dict[str, str]] = None,
    landmarks: Optional[List[str]] = None,
    creatures: Optional[List[str]] = None,
    threats: Optional[List[str]] = None,
    loot_or_clues: Optional[List[str]] = None,
    state: Optional[Dict[str, bool]] = None,
    hooks: Optional[str] = None,
    closed_spec: Optional[Dict[str, str]] = None,
    open_spec: Optional[Dict[str, str]] = None,
    description: Optional[str] = None,
) -> dict:
    """
    Factory endpoint for agents to spawn a new **Environment** object.

    Parameters (match call signature)
    ---------------------------------
    request_id : str
        Correlates this invocation to the inbound request or message.
    game_id : str
        Campaign / session identifier.
    name : str
        Human-readable label (“Shadowed Armory”).
    kind : str
        ``"<Open|Closed>:<Subtype>"`` e.g. ``"Closed:DungeonRoom"`` or ``"Open:Forest"``.
    summary : str
        One-sentence flavor (“Dusty dwarven armory littered with broken blades”).
    ambience : dict[str, str], optional
        Lite atmosphere triad with keys ``light``, ``sound``, ``smell``.
    landmarks, creatures, threats, loot_or_clues : list[str], optional
        World-objects, NPC IDs, hazard blurbs, and discoverables.
    state : dict[str, bool], optional
        Flip-able flags that track live changes (``{"door_open": false}``).
    hooks : str, optional
        Why this location matters to the plot right now.
    closed_spec / open_spec : dict[str, str], optional
        Tactical add-ons — only include the one that matches *kind*.
    description : str, optional
        Free-form GM notes.

    Returns
    -------
    dict
        JSON-serialisable representation of the new environment (same as ``Environment.as_dict()``).

    Examples
    --------
    >>> env_dict = create_environment(
    ...     request_id="req-123",
    ...     game_id="game-42",
    ...     name="Wind-Swept Hill",
    ...     kind="Open:Hill",
    ...     summary="Grassy ridge overlooking farmland."
    ... )
    """
    # ── Minimal validation so the agent can't generate illegal payloads ─────────
    if not kind.lower().startswith(("open:", "closed:")):
        raise ValueError('kind must start with "Open:" or "Closed:".')

    if ambience:
        for k in ambience:
            if k not in {"light", "sound", "smell"}:
                raise ValueError(f"ambience key '{k}' is invalid; use light/sound/smell.")

    # ── Build the environment object ───────────────────────────────────────────
    environment = Environment(
        name=name,
        kind=kind,
        summary=summary,
        ambience=ambience,
        landmarks=landmarks,
        creatures=creatures,
        threats=threats,
        loot_or_clues=loot_or_clues,
        state=state,
        hooks=hooks,
        closed_spec=closed_spec,
        open_spec=open_spec,
        request_id=request_id,
        game_id=game_id,
        description=description,
    )

    return environment.as_dict()


if __name__ == "__main__":
    mcp.run(transport="stdio")