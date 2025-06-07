import re

def sanitize(string: str) -> str:
    # Replace spaces with underscores, remove single/double quotes, then truncate
    sanitized = re.sub(r'[\s]', '_', string)  # Replace spaces with underscores
    sanitized = re.sub(r"['\",\\\`\>\<\{\}\[\]]", '', sanitized)  # Remove single and double quotes
    return sanitized[:20]

def make_filename_character(game_entity: dict) -> str:
    filename = f"{sanitize(game_entity['name'])}.{sanitize(game_entity['description'])}.{game_entity['id']}.json"
    return filename

def make_filename_environment(game_entity: dict) -> str:
    filename = f"{sanitize(game_entity['name'])}.{game_entity['id']}.json"
    return filename

def make_filename(game_entity: dict) -> str:
    if game_entity['entity_type'] == 'character':
        return make_filename_character(game_entity)
    
    if game_entity['entity_type'] == 'environment':
        return make_filename_environment(game_entity)

    filename = f"{game_entity['name']}.{game_entity['id']}.json"
    return filename