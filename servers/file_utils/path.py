BASE_PATH="output/"

def get_path(game_entity: dict) -> str:
    game_id = game_entity["game_id"]
    entity_type = game_entity["entity_type"]
    directory = BASE_PATH + game_id + "/" + entity_type + "/"
    return directory
