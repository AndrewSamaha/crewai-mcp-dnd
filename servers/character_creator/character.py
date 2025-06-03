"""
dnd_character.py - complete

Generates level‑1 D&D characters with race, class, and refreshed 2024
backgrounds, plus derived HP and AC.  Added JSON export helpers.
"""
import random
import json
from typing import Dict, List
try:
    from character_creator.name_generator import FantasyNameGenerator  # Absolute import for package usage
except ImportError:
    from name_generator import FantasyNameGenerator  # Fallback for direct script execution
import json
import uuid
import os
import dotenv


# ---------- Helpers --------------------------------------------------

def ability_mod(score: int) -> int:
    return (score - 10) // 2

# ---------- Constants ------------------------------------------------
ABILITIES: List[str] = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]

RACES: Dict[str, Dict] = {
    "Human":      {"fixed": {"ALL": 1}},
    "Dwarf":      {"fixed": {"CON": 2}},
    "Elf":        {"fixed": {"DEX": 2}},
    "Halfling":   {"fixed": {"DEX": 2}},
    "Dragonborn": {"fixed": {"STR": 2, "CHA": 1}},
    "Gnome":      {"fixed": {"INT": 2}},
    "Half-Elf":   {"fixed": {"CHA": 2}, "variable": {"count": 2, "choices": ["STR","DEX","CON","INT","WIS"]}},
    "Half-Orc":   {"fixed": {"STR": 2, "CON": 1}},
    "Tiefling":   {"fixed": {"CHA": 2, "INT": 1}},
}

CLASSES: Dict[str, Dict] = {
    "Barbarian": {"saves": ["STR", "CON"], "hit_die": 12},
    "Bard":      {"saves": ["DEX", "CHA"], "hit_die": 8},
    "Cleric":    {"saves": ["WIS", "CHA"], "hit_die": 8},
    "Druid":     {"saves": ["INT", "WIS"], "hit_die": 8},
    "Fighter":   {"saves": ["STR", "CON"], "hit_die": 10},
    "Monk":      {"saves": ["STR", "DEX"], "hit_die": 8},
    "Paladin":   {"saves": ["WIS", "CHA"], "hit_die": 10},
    "Ranger":    {"saves": ["STR", "DEX"], "hit_die": 10},
    "Rogue":     {"saves": ["DEX", "INT"], "hit_die": 8},
    "Sorcerer":  {"saves": ["CON", "CHA"], "hit_die": 6},
    "Warlock":   {"saves": ["WIS", "CHA"], "hit_die": 8},
    "Wizard":    {"saves": ["INT", "WIS"], "hit_die": 6},
}

BACKGROUNDS: Dict[str, Dict] = {
    "Acolyte": dict(ability_options=["CHA", "INT", "WIS"], skills=["Insight", "Religion"], tool="Calligrapher's Supplies", origin_feat="Magic Initiate (Cleric)"),
    "Artisan": dict(ability_options=["STR", "DEX", "INT"], skills=["Investigation", "Persuasion"], tool="One Artisan's Tools", origin_feat="Crafter"),
    "Charlatan": dict(ability_options=["DEX", "CON", "CHA"], skills=["Deception", "Sleight of Hand"], tool="Forgery Kit", origin_feat="Skilled"),
    "Criminal": dict(ability_options=["DEX", "CON", "INT"], skills=["Sleight of Hand", "Stealth"], tool="Thieves' Tools", origin_feat="Alert"),
    "Entertainer": dict(ability_options=["STR", "DEX", "CHA"], skills=["Acrobatics", "Performance"], tool="One Musical Instrument", origin_feat="Musician"),
    "Farmer": dict(ability_options=["STR", "CON", "WIS"], skills=["Animal Handling", "Nature"], tool="Carpenter's Tools", origin_feat="Tough"),
    "Guard": dict(ability_options=["STR", "INT", "WIS"], skills=["Athletics", "Perception"], tool="One Gaming Set", origin_feat="Alert"),
    "Guide": dict(ability_options=["DEX", "CON", "WIS"], skills=["Stealth", "Survival"], tool="Cartographer's Tools", origin_feat="Magic Initiate (Druid)"),
    "Hermit": dict(ability_options=["CON", "WIS", "CHA"], skills=["Medicine", "Religion"], tool="Herbalism Kit", origin_feat="Healer"),
    "Merchant": dict(ability_options=["CON", "INT", "CHA"], skills=["Animal Handling", "Persuasion"], tool="Navigator's Tools", origin_feat="Lucky"),
    "Noble": dict(ability_options=["STR", "INT", "CHA"], skills=["History", "Persuasion"], tool="One Gaming Set", origin_feat="Skilled"),
    "Sage": dict(ability_options=["CON", "INT", "WIS"], skills=["Arcana", "History"], tool="Calligrapher's Supplies", origin_feat="Magic Initiate (Wizard)"),
    "Sailor": dict(ability_options=["STR", "DEX", "WIS"], skills=["Acrobatics", "Perception"], tool="Navigator's Tools", origin_feat="Tavern Brawler"),
    "Scribe": dict(ability_options=["DEX", "INT", "WIS"], skills=["Investigation", "Perception"], tool="Calligrapher's Supplies", origin_feat="Skilled"),
    "Soldier": dict(ability_options=["STR", "DEX", "CON"], skills=["Athletics", "Intimidation"], tool="One Gaming Set", origin_feat="Savage Attacker"),
    "Wayfarer": dict(ability_options=["DEX", "WIS", "CHA"], skills=["Insight", "Stealth"], tool="Thieves' Tools", origin_feat="Lucky"),
}

SCHEMA_VERSION = "1.0.0"

# ---------- Character class -----------------------------------------
class Character:
    entity_type = "character"  # Class-level constant
    def __init__(self, name: str, base_scores: Dict[str, int] | None = None, request_id: str = None, game_id: str = None, description: str = None, personality_profile: str = None, current_goal: str = None):
        self.entity_type = "character"
        self.id = str(uuid.uuid4())
        self.request_id = request_id
        self.name = name
        self.ability_scores = {a: 8 for a in ABILITIES}
        if base_scores:
            for a, v in base_scores.items():
                self.ability_scores[a] = v

        self.race = self.char_class = self.background = None
        self.skills, self.tool_proficiencies, self.feats = set(), set(), set()
        self.saving_throws = set()
        self.level = 1
        self.proficiency_bonus = 2  # 5e: +2 at level 1
        self.cr = max(1, self.level // 4)
        self.max_hp = self.ac = None
        self.hp_history = []  # track HP gained per level for reproducibility
        self.request_id = request_id
        self.game_id = game_id
        self.description = description
        self.schema_version = SCHEMA_VERSION
        self.personality_profile = personality_profile
        self.current_goal = current_goal

    def get_personality_profile(self):
        return self.personality_profile

    def set_personality_profile(self, value: str):
        self.personality_profile = value

    def get_current_goal(self):
        return self.current_goal

    def set_current_goal(self, value: str):
        self.current_goal = value

    def level_up(self, rng=random, average_hp=False):
        """Increase level by 1, update HP, proficiency, CR, and stub for features/ASI."""
        self.level += 1
        # Proficiency bonus increases at 5, 9, 13, 17 (5e rules)
        self.proficiency_bonus = 2 + ((self.level - 1) // 4)
        self.cr = max(1, self.level // 4)
        # HP gain: roll or average hit die + CON mod
        con_mod = ability_mod(self.ability_scores["CON"])
        if average_hp:
            gain = (self.hit_die // 2) + 1 + con_mod
        else:
            gain = rng.randint(1, self.hit_die) + con_mod
        self.max_hp += max(gain, 1)  # minimum 1 HP per level
        self.hp_history.append(gain)
        # TODO: Handle ASI/feat at levels 4, 8, etc.
        # TODO: Handle class features, spell slots, etc.
        # TODO: Handle skill/saving throw increases if needed
        self.compute_derived()


    # ---- Race ----
    def apply_race(self, race: str, rng=random):
        info = RACES[race]
        self.race = race
        for abl, inc in info.get("fixed", {}).items():
            if abl == "ALL":
                for a in ABILITIES:
                    self.ability_scores[a] += inc
            else:
                self.ability_scores[abl] += inc
        if "variable" in info:
            var = info["variable"]
            for a in rng.sample(var["choices"], k=var["count"]):
                self.ability_scores[a] += 1

    # ---- Class ----
    def apply_class(self, cls: str):
        info = CLASSES[cls]
        self.char_class = cls
        self.saving_throws.update(info["saves"])
        self.hit_die = info["hit_die"]

    # ---- Background ----
    def apply_background(self, bg: str, rng=random):
        info = BACKGROUNDS[bg]
        self.background = bg
        opts = info["ability_options"]
        if rng.choice([True, False]):
            primary = rng.choice(opts)
            secondary = rng.choice([o for o in opts if o != primary])
            self.ability_scores[primary] += 2
            self.ability_scores[secondary] += 1
        else:
            for o in opts:
                self.ability_scores[o] += 1
        self.skills.update(info["skills"])
        self.tool_proficiencies.add(info["tool"])
        self.feats.add(info["origin_feat"])

    # ---- Derived ----
    def compute_derived(self):
        con_mod = ability_mod(self.ability_scores["CON"])
        # Recalculate max_hp from scratch if hp_history exists
        if hasattr(self, "hp_history") and self.hp_history:
            self.max_hp = self.hit_die + con_mod + sum(self.hp_history)
        else:
            self.max_hp = self.hit_die + con_mod
        dex_mod = ability_mod(self.ability_scores["DEX"])
        base_ac = 10 + dex_mod
        if self.char_class == "Barbarian":
            self.ac = base_ac + con_mod
        elif self.char_class == "Monk":
            wis_mod = ability_mod(self.ability_scores["WIS"])
            self.ac = base_ac + wis_mod
        else:
            self.ac = base_ac

    # ---- Export helpers ----
    def as_dict(self) -> Dict:
        return {
            "id": self.id,
            "personality_profile": self.personality_profile,
            "current_goal": self.current_goal,
            "entity_type": self.entity_type,
            "name": self.name,
            "race": self.race,
            "class": self.char_class,
            "background": self.background,
            "level": self.level,
            "proficiency_bonus": self.proficiency_bonus,
            "cr": self.cr,
            "ability_scores": self.ability_scores.copy(),
            "max_hp": self.max_hp,
            "ac": self.ac,
            "saving_throws": sorted(self.saving_throws),
            "skills": sorted(self.skills),
            "tools": sorted(self.tool_proficiencies),
            "feats": sorted(self.feats),
            "request_id": self.request_id,
            "game_id": self.game_id,
            "description": self.description,
            "schema_version": self.schema_version
        }

    def to_json(self, **kwargs) -> str:
        """Return a JSON string of the character; **kwargs passed to json.dumps."""
        return json.dumps(self.as_dict(), **kwargs)

    # ---- String ----
    def __str__(self):
        lines = [f"=== {self.name} ===",
                 f"Race / Class / Background: {self.race} / {self.char_class} / {self.background}",
                 f"HP | AC : {self.max_hp} hp | {self.ac}",
                 "Ability Scores:"]
        lines += [f"  {a}: {self.ability_scores[a]}" for a in ABILITIES]
        lines += [f"Saving Throws: {', '.join(sorted(self.saving_throws))}",
                  f"Skills:        {', '.join(sorted(self.skills))}",
                  f"Tools:         {', '.join(sorted(self.tool_proficiencies))}",
                  f"Feats:         {', '.join(sorted(self.feats))}"]
        return "\n".join(lines)

# ---------- Builder --------------------------------------------------

def build_random_character(name: str = FantasyNameGenerator().generate_name(), rng=random, request_id: str = str(uuid.uuid4()), game_id: str = None, description: str = None, cr: int = None, personality_profile: str = None, current_goal: str = None) -> Character:
    array = rng.sample([15, 14, 13, 12, 10, 8], k=6)
    base = dict(zip(ABILITIES, array))
    pc = Character(name, base, request_id=request_id, game_id=game_id, description=description, personality_profile=personality_profile, current_goal=current_goal)
    pc.apply_race(rng.choice(list(RACES)), rng=rng)
    pc.apply_class(rng.choice(list(CLASSES)))
    pc.apply_background(rng.choice(list(BACKGROUNDS)), rng=rng)
    pc.compute_derived()
    return pc

# ---------- Demo -----------------------------------------------------
if __name__ == "__main__":
    dotenv.load_dotenv()

    hero = build_random_character(game_id=os.getenv("GAME_ID"))
    print(hero.to_json(indent=2))
    for _ in range(15):
        hero.level_up()
    print(hero.to_json(indent=2))
