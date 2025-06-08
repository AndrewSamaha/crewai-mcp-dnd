import json
import os
from datetime import datetime
from pathlib import Path


def log(data, tool_name, label, log_file="tool_calls_log.json", indent=2):
    """
    Log data to a JSON file with proper formatting.
    
    Args:
        data: The data to log
        tool_name: Name of the tool generating the log
        label: Label for the log entry
        log_file: Path to the log file (default: tool_calls_log.json)
        indent: Number of spaces for JSON indentation (default: 2)
    """
    try:
        output = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "label": label,
            "data": data,
        }
        
        # Create directory for log file if it doesn't exist
        log_path = Path(log_file)
        if log_path.parent != Path('.'):
            os.makedirs(log_path.parent, exist_ok=True)
            
        with open(log_file, "a") as f:
            # Use pretty formatting with specified indent
            formatted_json = json.dumps(output, indent=indent, sort_keys=False)
            f.write(formatted_json + "\n")
    except Exception as e:
        print(f"Error logging to {log_file}: {str(e)}")