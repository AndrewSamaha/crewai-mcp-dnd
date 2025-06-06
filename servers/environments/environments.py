# environments.py
import json
import random
import uuid
from typing import Dict, List, Optional

# ── Optional fallback for your existing `log()` helper ──────────────────────────
try:
    from utils import log                      # or wherever your helper lives
except ImportError:                            # silently no-op if not found
    def log(*_, **__):  # type: ignore
        pass

SCHEMA_VERSION = 1


class Environment:
    """Lightweight container for any scene—room, hilltop, street, etc."""
    entity_type = "environment"  # Class-level constant

    # ── Init ────────────────────────────────────────────────────────────────────
    def __init__(
        self,
        name: str,
        kind: str,                          # "Closed:DungeonRoom", "Open:Forest", …
        summary: str,
        ambience: Dict[str, str] | None = None,    # {"light": "dim", "sound": "rustling", …}
        landmarks: List[str] | None = None,
        creatures: List[str] | None = None,        # IDs that point to stat blocks elsewhere
        threats: List[str] | None = None,
        loot_or_clues: List[str] | None = None,
        state: Dict[str, bool] | None = None,
        hooks: Optional[str] = None,
        closed_spec: Dict[str, str] | None = None, # Only for Closed scenes
        open_spec: Dict[str, str] | None = None,   # Only for Open scenes
        request_id: Optional[str] = None,
        game_id: Optional[str] = None,
        description: Optional[str] = None,
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.kind = kind
        self.summary = summary
        self.ambience = ambience or {}
        self.landmarks = landmarks or []
        self.creatures = creatures or []
        self.threats = threats or []
        self.loot_or_clues = loot_or_clues or []
        self.state = state or {}
        self.hooks = hooks
        self.closed_spec = closed_spec
        self.open_spec = open_spec
        self.request_id = request_id
        self.game_id = game_id
        self.description = description
        self.schema_version = SCHEMA_VERSION

        log({"name": name, "kind": kind}, "Environment.init – input params")
        log(self.as_dict(), "Environment.init – created environment")

    # ── Export helpers ──────────────────────────────────────────────────────────
    def as_dict(self) -> Dict:
        data = {
            "id": self.id,
            "entity_type": self.entity_type,
            "name": self.name,
            "kind": self.kind,
            "summary": self.summary,
            "ambience": self.ambience,
            "landmarks": self.landmarks,
            "creatures": self.creatures,
            "threats": self.threats,
            "loot_or_clues": self.loot_or_clues,
            "state": self.state,
            "hooks": self.hooks,
            "request_id": self.request_id,
            "game_id": self.game_id,
            "description": self.description,
            "schema_version": self.schema_version,
        }
        if self.closed_spec:
            data["closed_spec"] = self.closed_spec
        if self.open_spec:
            data["open_spec"] = self.open_spec
        return data

    def to_json(self, **kwargs) -> str:
        """Return a JSON string of the environment; **kwargs passed to json.dumps."""
        return json.dumps(self.as_dict(), **kwargs)

    # ── String representation – handy for quick debugging ──────────────────────
    def __str__(self) -> str:
        return f"{self.name} ({self.kind}) – {self.summary}"


# ────────────────────────────────────────────────────────────────────────────────
# Convenience builder – mirrors build_random_character() style
# ────────────────────────────────────────────────────────────────────────────────

def build_random_environment(
    name: str | None = None,
    rng: random.Random = random,
    kind: str | None = None,
    request_id: str = str(uuid.uuid4()),
    game_id: str | None = None,
    description: str | None = None,
) -> Environment:
    """
    Quickly spit out a lightweight Environment instance with sensible defaults.
    Replace tables/lists below with your own world-specific data as needed.
    """
    # ------------  Name & Kind  -------------------------------------------------
    default_names = [
        "Shadowed Armory", "Wind-Swept Hill", "Gloomwood Clearing",
        "Crystal Cavern", "Sun-Bleached Plaza"
    ]
    if name is None:
        name = rng.choice(default_names)

    default_kinds = ["Closed:DungeonRoom", "Open:Forest", "Open:Hill", "Closed:Cavern"]
    if kind is None:
        kind = rng.choice(default_kinds)

    is_closed = kind.lower().startswith("closed")

    # ------------  Summary & Ambience  -----------------------------------------
    summary_map = {
        "Closed:DungeonRoom": "Dusty dwarven armory littered with broken blades.",
        "Closed:Cavern": "Natural cave glittering with quartz.",
        "Open:Forest": "Leafy glade dappled with sunlight.",
        "Open:Hill": "Grassy ridge overlooking farmland.",
    }
    summary = summary_map.get(kind, "A featureless stretch of land.")

    ambience = {
        "light": rng.choice(["dim", "bright", "gloomy"]),
        "sound": rng.choice(["dripping", "rustling", "whistling wind", "silent"]),
        "smell": rng.choice(["musty", "pine-fresh", "earthy", "ozone"]),
    }

    # ------------  Flavor Lists  ------------------------------------------------
    landmarks = rng.sample(
        [
            "weapon rack",
            "lone oak tree",
            "stone altar",
            "collapsed wall",
            "old well",
            "fallen log",
            "rocky outcrop",
        ],
        k=3,
    )

    threats = rng.sample(
        [
            "loose stones (DC 12 Dex save, 2d6 bludgeoning)",
            "hidden snare (DC 14 Dex, restrained)",
            "swivelling blade trap (DC 15, 2d8 slashing)",
            "sudden gusts (DC 12 Dex, may knock prone)",
        ],
        k=1,
    )

    loot = rng.sample(
        [
            "warhammer +1",
            "potion of healing",
            "silver locket",
            "ancient map fragment",
        ],
        k=1,
    )

    hooks = rng.choice(
        [
            "needed to secure dwarf alliance quest.",
            "ideal spot to signal allies with bonfire.",
            "rumored treasure buried here.",
            "serves as shortcut to hidden stronghold.",
        ]
    )

    # ------------  Open/Closed spec  -------------------------------------------
    closed_spec = open_spec = None
    if is_closed:
        closed_spec = {
            "shape": rng.choice(
                ["30 × 40 ft rectangle", "circular 50 ft diameter", "irregular cavern"]
            ),
            "exits": rng.sample(
                ["wooden door (east)", "iron gate (west)", "secret hatch (floor)"], k=2
            ),
            "ceiling_height": rng.choice(["10 ft", "15 ft", "20 ft"]),
        }
    else:
        open_spec = {
            "scope": f"≈{rng.randint(150, 300)} ft radius",
            "terrain_tags": rng.sample(
                ["grassy", "rocky", "sandy", "muddy", "snow-dusted"], k=2
            ),
            "edges": rng.sample(
                [
                    "forest edge (north)",
                    "river gorge (south)",
                    "cliff (east)",
                    "road (west)",
                ],
                k=2,
            ),
        }

    # ------------  Build & return  ---------------------------------------------
    env = Environment(
        name=name,
        kind=kind,
        summary=summary,
        ambience=ambience,
        landmarks=landmarks,
        creatures=[],                # Fill in if you have random-encounter tables
        threats=threats,
        loot_or_clues=loot,
        state={},
        hooks=hooks,
        closed_spec=closed_spec,
        open_spec=open_spec,
        request_id=request_id,
        game_id=game_id,
        description=description,
    )
    return env


# ─── Quick demo ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    env = build_random_environment(game_id="demo-game-123")
    print(env.to_json(indent=2))
