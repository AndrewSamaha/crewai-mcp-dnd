import re

def sanitize(string: str) -> str:
    # Replace spaces with underscores, remove single/double quotes, then truncate
    sanitized = re.sub(r'[\s]', '_', string)  # Replace spaces with underscores
    sanitized = re.sub(r"['\",\\\`\>\<\{\}\[\]]", '', sanitized)  # Remove single and double quotes
    return sanitized[:20]

def make_filename(game_entity: dict) -> str:
    filename = f"{game_entity['name']}.{sanitize(game_entity['description'])}.{game_entity['id']}.json"
    return filename