import subprocess
from typing import List, Dict
import json

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
    try:
        result = subprocess.run(
            ['rg', query, search_path],
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
        
        # split line on tab
        filename = line.split('\t')[0][:-1]
        matching_str = line.split('\t')[1]
        matches.append({'file': filename, 'line': matching_str.strip()})

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
    
    matches = run_ripgrep(search_query, search_path)
    if matches:
        entities = []
        for match in matches:
            entity = json.load(open(match['file']))
            # if entity_type and entity["entity_type"] != entity_type:
            #     continue
            entities.append(entity)
        return entities
    return "No entities found matching search query: {} and entity_type: {}, search_path: {}, matches_result: {}".format(search_query, entity_type, search_path, matches)