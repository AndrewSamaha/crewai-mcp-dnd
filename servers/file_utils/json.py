import json
import os
from copy import deepcopy
from glom import glom, assign

from servers.file_utils.path import get_path
from servers.file_utils.filename import make_filename
from servers.file_utils.ripgrep import find_entity_by_id
from servers.utils.logging import log

def save_game_entity_fn(game_entity: dict) -> str:
    filename = make_filename(game_entity)
    directory = get_path(game_entity)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(directory + filename, "w") as f:
        json.dump(game_entity, f, indent="\t")
    return filename

def read_game_entity_fn(entity_id: str) -> dict:
    matches = find_entity_by_id(entity_id)
    if len(matches) == 0:
        raise FileNotFoundError(f"No entity found with id: {entity_id}")
    filepath = matches[0]
    # example match = output/errotin/environment/Village_of_Unka.2a98cbf2-4fec-45f9-92e8-298f55bfa93a.json
    extracted_game_id = filepath.split("/")[1]
    extracted_entity_type = filepath.split("/")[2]
    entity = None
    with open(filepath, "r") as f:
        entity = json.load(f)
    entity_file_match = {
        "filepath": filepath,
        "game_id": extracted_game_id,
        "entity_type": extracted_entity_type,
        "entity": entity
    }
    return entity_file_match

def update_entity_field_fn(entity_id: str, field: str, value: str or int or float or bool or dict or list) -> str:
    # ToDo: Make sure thee changes match the schema defintions
    try:
        entity_file_match = read_game_entity_fn(entity_id)
        filepath = entity_file_match["filepath"]
        game_id = entity_file_match["game_id"]
        entity_type = entity_file_match["entity_type"]
        old_entity = entity_file_match["entity"]
        previous_value = glom(old_entity, field, default=None)
        new_entity = deepcopy(old_entity)
        assign(new_entity, field, value)
        save_game_entity_fn(new_entity)
        return new_entity    
    except Exception as e:
        raise Exception(e)
    

        

