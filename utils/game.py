from .fileutils import read_json_file

def get_game_information(game_id: str) -> dict:
    return read_json_file(f"output/{game_id}/game_information.json")
