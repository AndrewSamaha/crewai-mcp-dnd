import subprocess
from typing import List, Dict
import json
import os
from typing import Optional


BASE_PATH="output/"

def run_ripgrep(query: str, search_path: str = './output') -> List[Dict[str, str]]:
    """
    Runs ripgrep (rg) with the given query and returns a list of dicts with filename and matching line.

    Args:
        query (str): The search string to pass to rg.
        search_path (str): The directory or file path to search in (default: './output').
    Returns:
        list of dict: Each dict has 'file' (str) and 'line' (str) keys.
    """
    #query = f"/{query}/i"
    print(f"Running ripgrep with query: '{query}' and search_path: '{search_path}'")
    try:
        result = subprocess.run(
            ['rg', "-i", query, search_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        output = result.stdout
    except subprocess.CalledProcessError as e:
        output = e.stdout
        if not output:
            return []
    
    matches = []
    for line in output.splitlines():
        tab_split_line = line.split(':')
        filename = str(tab_split_line[0]).strip().replace("\t", "").replace(" ", "")
        matching_line = str(tab_split_line[1:]).strip().replace("\t", "").replace(" ", "")
        matches.append({'file': filename, 'line': matching_line})

    return matches



def find_entity_by_id(entity_id: str, game_id: Optional[str] = None, entity_type: Optional[str] = None, base_path: str = "output") -> list:
    """
    Find entities by their id, searching for files matching the pattern:
    output/GAME_ID/ENTITY_TYPE/NAME.DESCRIPTION.ENTITY_ID.json
    Returns a list of file paths that match the entity_id.
    """
    matches = []
    # Build the search directory
    search_dir = base_path
    if game_id:
        search_dir = os.path.join(search_dir, game_id)
    if entity_type:
        search_dir = os.path.join(search_dir, entity_type)
    if not os.path.isdir(search_dir):
        return []
    for root, dirs, files in os.walk(search_dir):
        for fname in files:
            if fname.endswith(f".{entity_id}.json"):
                matches.append(os.path.join(root, fname))
    return matches

def find_entities_fn(search_query: str, game_id: str, entity_type: str = "", search_path: str = './output') -> List[Dict[str, str]]:
    """
    Runs ripgrep (rg) with the given query and returns a list of dicts with filename and matching line.

    Args:
        query (str): The search string to pass to rg.
        search_path (str): The directory or file path to search in (default: './output').
    Returns:
        list of dict: Each dict has 'file' (str) and 'line' (str) keys.
    """
    
    if entity_type:
        search_path = BASE_PATH + game_id + "/" + entity_type + "/"
    else:
        search_path = BASE_PATH + game_id + "/"
    
    found_entity_ids = []
    matches = run_ripgrep(search_query, search_path)
    if matches:
        entities = []
        for match in matches:
            entity = json.load(open(match['file']))
            # if entity_type and entity["entity_type"] != entity_type:
            #     continue
            if entity["id"] in found_entity_ids:
                continue
            found_entity_ids.append(entity["id"])
            entities.append(entity)
        return entities
    return "No entities found matching search query: {} and entity_type: {}, search_path: {}, matches_result: {}".format(search_query, entity_type, search_path, matches)