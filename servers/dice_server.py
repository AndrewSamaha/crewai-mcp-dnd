"""A simple dice-rolling MCP server that implements the Model Context Protocol.

This server provides dice-rolling operations as tools that can be discovered and used by MCP clients.
"""

from mcp.server.fastmcp import FastMCP
import random

mcp = FastMCP("Dice")

@mcp.tool()
def roll_dice(number_of_dice: int, number_of_sides: int, request_id: str) -> int:
    """Roll a number of dice with a given number of sides. When the user requests a 2d6, for example, they would pass 2 for number_of_dice and 6 for number_of_sides.
    
    Args:
        number_of_dice (int): The number of dice to roll.
        number_of_sides (int): The number of sides on each die.
        request_id (str): The ID of the request.
    """
    return sum([random.randint(1, number_of_sides) for _ in range(number_of_dice)])

if __name__ == "__main__":
    mcp.run(transport="stdio")

