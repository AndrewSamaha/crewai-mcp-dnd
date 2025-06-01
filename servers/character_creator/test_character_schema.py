import pytest
from character import build_random_character
from schema.utils import detect_schema_version


def test_character_schema_version():
    char = build_random_character()
    char_dict = char.as_dict()
    version = detect_schema_version(char_dict)
    assert version == "1.0.0", f"Expected schema version '1.0.0', got {version}"

    # Also test JSON string
    char_json = char.to_json()
    version_json = detect_schema_version(char_json)
    assert version_json == "1.0.0", f"Expected schema version '1.0.0' from JSON, got {version_json}"

def test_character_schema_version_negative():
    # Missing required fields
    invalid_data = {
        "name": "Test",
        "race": "Elf",
        # Missing many fields, e.g., 'class', 'level', etc.
        "ability_scores": {"STR": 10, "DEX": 10, "CON": 10, "INT": 10, "WIS": 10, "CHA": 10},
        "schema_version": "1.0.0"
    }
    assert detect_schema_version(invalid_data) is None
    # Also test with a wrong ability_scores structure
    invalid_data2 = {
        "name": "Test",
        "race": "Elf",
        "class": "Fighter",
        "background": "Sage",
        "level": 1,
        "proficiency_bonus": 2,
        "cr": 1,
        "ability_scores": {"STR": 10, "DEX": 10},  # Incomplete
        "max_hp": 10,
        "ac": 12,
        "saving_throws": [],
        "skills": [],
        "tools": [],
        "feats": [],
        "request_id": None,
        "game_id": None,
        "description": None,
        "schema_version": "1.0.0"
    }
    assert detect_schema_version(invalid_data2) is None
