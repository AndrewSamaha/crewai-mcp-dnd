"""A JSON file tool that implements the Model Context Protocol.

This server provides JSON file operations as tools that can be discovered and used by MCP clients.
"""

from mcp.server.fastmcp import FastMCP
from file_utils.filename import make_filename
import json
import os

mcp = FastMCP("JSON File")

BASE_PATH="output/"
def get_path(game_entity: dict) -> str:
    game_id = game_entity["game_id"]
    entity_type = game_entity["entity_type"]
    directory = BASE_PATH + game_id + "/" + entity_type + "/"
    return directory

@mcp.tool()
def save_game_entity(request_id: str, game_entity: dict) -> str:
    """Save a game entity as a JSON file.
    
    Args:
        request_id (str): The ID of the request.
        game_entity (dict): The ENTIRE game entity to save as a JSON file.
    """
    filename = make_filename(game_entity)
    directory = get_path(game_entity)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(directory + filename, "w") as f:
        json.dump(game_entity, f, indent="\t")
    return filename

if __name__ == "__main__":
    mcp.run(transport="stdio")

