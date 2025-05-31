import subprocess
from typing import List, Dict

def run_ripgrep(query: str, search_path: str = './output') -> List[Dict[str, str]]:
    """
    Runs ripgrep (rg) with the given query and returns a list of dicts with filename and matching line.

    Args:
        query (str): The search string to pass to rg.
        search_path (str): The directory or file path to search in (default: './output').
    Returns:
        list of dict: Each dict has 'file' (str) and 'line' (str) keys.
    """
    try:
        result = subprocess.run(
            ['rg', query, search_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        output = result.stdout
    except subprocess.CalledProcessError as e:
        output = e.stdout
        if not output:
            return []

    matches = []
    current_file = None
    last_file = None
    for line in output.splitlines():
        # Multi-file search: filename line
        if line.startswith(search_path) or line.startswith("./"):
            current_file = line.strip()
            last_file = current_file
            continue
        # Match lines like: 7:      "description": "a rotting hand",
        if ':' in line:
            # Single-file search: no filename line
            if current_file is None:
                # Use search_path as file if it's a file
                file_path = search_path if os.path.isfile(search_path) else last_file
            else:
                file_path = current_file
            matches.append({'file': file_path, 'line': line.strip()})
    return matches
