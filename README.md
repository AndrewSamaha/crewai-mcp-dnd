# CrewAI MCP DnD

Agents for creating Dungeons and Dragons environments and characters.

## Prerequisites

- uv [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)
- Python >= 3.12 < 3.13
- OPENAI API Key or an API key from another LLM provider
- Langfuse API Key

## Installation

```bash
uv venv .venv
```

## Usage

1. Copy `.env.example` to `.env` and add parameters:
 - OPENAI_API_KEY
 - MODEL (e.g., openai/gpt-4o-mini)
 - LANGFUSE related parameters
 - GAME_ID (an arbitrary identifier for a given 'world')

2. Run a crew, e.g.,:
 - `uv run environment_crew.py`
 - `uv run character_crew.py`
