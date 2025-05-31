def sanitize(string: str) -> str:
    return string.replace(" ", "_").replace("'", "").replace("\"", "")[:20]

def make_filename(game_entity: dict) -> str:
    filename = f"{game_entity['name']}.{sanitize(game_entity['description'])}.{game_entity['id']}.json"
    return filename