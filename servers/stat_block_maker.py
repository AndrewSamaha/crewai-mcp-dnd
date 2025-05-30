"""A simple dice-rolling MCP server that implements the Model Context Protocol.

This server provides dice-rolling operations as tools that can be discovered and used by MCP clients.
"""

from mcp.server.fastmcp import FastMCP
import random
from typing import Optional
from character_creator.name_generator import FantasyNameGenerator

mcp = FastMCP("Dice")

@mcp.tool()
def make_stat_block(request_id: str, description: str, name: Optional[str] = None, level: Optional[int] = None, cr: Optional[int] = None, strength: Optional[int] = None, dexterity: Optional[int] = None, constitution: Optional[int] = None, intelligence: Optional[int] = None, wisdom: Optional[int] = None, charisma: Optional[int] = None) -> dict:
    """Create a D&D character stat block based on the provided parameters. Only request_id and description are required; other parameters will be filled in deterministically if not provided.
    
    Args:
        request_id (str): The ID of the request.
        description (str): A description of the creature.
        name (Optional[str]): The name of the creature. If None, will be generated from the description.
        level (Optional[int]): The level of the creature. If None, will be determined from the description.
        cr (Optional[int]): The challenge rating of the creature. If None, will be determined from the description.
        strength (Optional[int]): The strength of the creature. If None, will be determined from the description.
        dexterity (Optional[int]): The dexterity of the creature. If None, will be determined from the description.
        constitution (Optional[int]): The constitution of the creature. If None, will be determined from the description.
        intelligence (Optional[int]): The intelligence of the creature. If None, will be determined from the description.
        wisdom (Optional[int]): The wisdom of the creature. If None, will be determined from the description.
        charisma (Optional[int]): The charisma of the creature. If None, will be determined from the description.
    """
    # Fill in any missing stats deterministically based on the description
    if level is None:
        level = 1  # Default level
        
    if cr is None:
        cr = max(1, level // 4)  # Default CR based on level
        
    # Generate ability scores if not provided
    if strength is None:
        # Using the description to deterministically generate a value
        # For simplicity, using hash of the description to seed random
        random.seed(hash(description) % 10000)
        strength = random.randint(8, 18)
        
    if dexterity is None:
        random.seed(hash(description + "dex") % 10000)
        dexterity = random.randint(8, 18)
        
    if constitution is None:
        random.seed(hash(description + "con") % 10000)
        constitution = random.randint(8, 18)
        
    if intelligence is None:
        random.seed(hash(description + "int") % 10000)
        intelligence = random.randint(8, 18)
        
    if wisdom is None:
        random.seed(hash(description + "wis") % 10000)
        wisdom = random.randint(8, 18)
        
    if charisma is None:
        random.seed(hash(description + "cha") % 10000)
        charisma = random.randint(8, 18)
    
    if name is None:
        name = FantasyNameGenerator().generate_name()
    
    # Calculate modifiers
    str_mod = (strength - 10) // 2
    dex_mod = (dexterity - 10) // 2
    con_mod = (constitution - 10) // 2
    int_mod = (intelligence - 10) // 2
    wis_mod = (wisdom - 10) // 2
    cha_mod = (charisma - 10) // 2
    
    # Calculate derived stats
    hp = 10 + (level - 1) * 5 + con_mod * level
    ac = 10 + dex_mod
    
    # Build the stat block as a dictionary
    stat_block = {
        "request_id": request_id,
        "name": name,
        "description": description,
        "level": level,
        "cr": cr,
        "ability_scores": {
            "strength": {
                "score": strength,
                "modifier": str_mod
            },
            "dexterity": {
                "score": dexterity,
                "modifier": dex_mod
            },
            "constitution": {
                "score": constitution,
                "modifier": con_mod
            },
            "intelligence": {
                "score": intelligence,
                "modifier": int_mod
            },
            "wisdom": {
                "score": wisdom,
                "modifier": wis_mod
            },
            "charisma": {
                "score": charisma,
                "modifier": cha_mod
            }
        },
        "derived_stats": {
            "hp": hp,
            "ac": ac
        }
    }
    
    return stat_block

if __name__ == "__main__":
    mcp.run(transport="stdio")

