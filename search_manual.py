from servers.file_utils.ripgrep import run_ripgrep, find_entities_fn
import dotenv
import warnings
from pydantic import PydanticDeprecatedSince20
import json
import os
warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)

dotenv.load_dotenv()

search_query = input("What do you want to search for? ")

# format json
#print(json.dumps(run_ripgrep(search_query), indent=2))
print(f"Searching for {search_query} in {os.getenv("GAME_ID")}")
entities = find_entities_fn(search_query, os.getenv("GAME_ID"))

print(json.dumps(entities, indent=2))

