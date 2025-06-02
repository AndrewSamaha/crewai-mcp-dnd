import json

SCHEMA_DEFINITIONS = {
    "1.0.0": {
        "fields": {
            "id", "entity_type", "name", "race", "class", "background", "level", "proficiency_bonus", "cr",
            "personality_profile", "current_goal",
            "ability_scores", "max_hp", "ac", "saving_throws", "skills", "tools", "feats",
            "request_id", "game_id", "description", "schema_version"
        },
        "ability_scores": {"STR", "DEX", "CON", "INT", "WIS", "CHA"},
        "values": {
            "schema_version": "1.0.0"
        }
    },
    # Future versions can be added here
}

def detect_schema_version(input_data):
    """
    Detects the schema version by checking for the expected fields for each known schema.
    Returns the schema_version string if a match is found, else None.
    Accepts a dict or JSON string.
    """
    if isinstance(input_data, str):
        try:
            input_data = json.loads(input_data)
        except Exception:
            return None
    if not isinstance(input_data, dict):
        return None
    for version, schema in SCHEMA_DEFINITIONS.items():
        fields = schema["fields"]
        ability_score_fields = schema["ability_scores"]
        required_values = schema.get("values", {})
        top_keys = set(input_data.keys())
        if not fields.issubset(top_keys):
            continue
        if "ability_scores" not in input_data or not isinstance(input_data["ability_scores"], dict):
            continue
        if set(input_data["ability_scores"].keys()) != ability_score_fields:
            continue
        # Check required values
        values_ok = True
        for k, v in required_values.items():
            if input_data.get(k) != v:
                values_ok = False
                break
        if not values_ok:
            continue
        return version
    return None
