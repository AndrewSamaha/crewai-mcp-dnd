"""A JSON file tool that implements the Model Context Protocol.

This server provides JSON file operations as tools that can be discovered and used by MCP clients.
"""

from mcp.server.fastmcp import FastMCP
from servers.file_utils.filename import make_filename
from servers.file_utils.ripgrep import find_entities_fn
from servers.file_utils.json import save_game_entity_fn
from servers.utils.logging import log
from constants.paths import BASE_PATH

mcp = FastMCP("JSON File")

@mcp.tool()
def save_game_entity(request_id: str, game_entity: dict) -> str:
    """Save a game entity as a JSON file.
    
    Args:
        request_id (str): The ID of the request.
        game_entity (dict): The ENTIRE game entity to save as a JSON file.
    """
    return save_game_entity_fn(game_entity)

@mcp.tool()
def get_game_entity_by_id(request_id: str, game_id: str, game_entity_id: str) -> dict:
    """Get a game entity given a known game_entity_id.
    
    Args:
        request_id (str): The ID of the request.
        game_id (str): The ID of the game.
        game_entity_id (str): The ID of the game entity to get.
    Returns:
        dict: The loaded game entity, or raises FileNotFoundError if not found.
    """
    import os
    import json

    # Walk through BASE_PATH and look for files containing game_entity_id
    for root, dirs, files in os.walk(BASE_PATH):
        for file in files:
            if game_entity_id in file and file.endswith('.json'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    return json.load(f)
    raise FileNotFoundError(f"No game entity file found containing id: {game_entity_id}")

@mcp.tool()
def find_entities(request_id: str, game_id: str, search_query: str, entity_type: str = "") -> list:
    """Find entities that match the given search query and (optionally) entity_type.
    
    Args:
        request_id (str): The ID of the request.
        game_id (str): The ID of the game.
        search_query (str): The search query to use.
        entity_type (str, optional): The type of the entity to find (character or environment). Generally, this should be left empty in order to keep the story's cannon consistent. Defaults to "" (matches any type).
    Returns:
        list: A list of entities that match the given search query and entity_type.
    """
    log({"entity_type": entity_type, "search_query": search_query, "game_id": game_id, "request_id": request_id}, "find_entities", "input")
    result = find_entities_fn(search_query, game_id, entity_type)
    log({"result": result}, "find_entities", "output")
    return result

if __name__ == "__main__":
    mcp.run(transport="stdio")

