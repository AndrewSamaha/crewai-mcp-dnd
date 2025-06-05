"""A simple character creation MCP server that implements the Model Context Protocol.

This server provides character creation operations as tools that can be discovered and used by MCP clients.
"""

from mcp.server.fastmcp import FastMCP
from typing import Optional
from character_creator.character import build_random_character, log
from file_utils.ripgrep import find_entity_by_id
import json

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

if __name__ == "__main__":
    mcp.run(transport="stdio")

