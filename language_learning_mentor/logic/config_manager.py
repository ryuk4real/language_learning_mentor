import json
import re
import os
from pathlib import Path

# --- Configuration ---
# Define CONFIG_DIR relative to this file's location
# This assumes the 'logic' directory is a sibling of 'config' and 'main.py'
# Adjust if your final structure is different
BASE_DIR = Path(__file__).resolve().parent.parent # Go up two levels from logic/config_manager.py
CONFIG_DIR = BASE_DIR / "config"
CONFIG_DIR.mkdir(exist_ok=True) # Create config directory if it doesn't exist


# --- Helper Functions ---
def get_config_path(username):
    """Generates the path for a user's config file."""
    # Sanitize username slightly for filename (replace spaces, common unsafe chars)
    safe_filename = re.sub(r'[\\/*?:"<>| ]', '_', username.lower())
    if not safe_filename:
        safe_filename = "default_user" # Fallback for empty/unsafe names
    return CONFIG_DIR / f"{safe_filename}.json"

def load_user_config(username):
    """Loads user configuration from JSON file."""
    config_path = get_config_path(username)
    try:
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            return None # User does not exist
    except json.JSONDecodeError:
        print(f"Warning: Corrupted config file for {username} at {config_path}. Using defaults.")
        return None # Treat as new user if file is corrupt
    except IOError as e:
         print(f"Error loading config for {username} from {config_path}: {e}")
         return None
    except Exception as e:
         print(f"An unexpected error occurred loading config for {username}: {e}")
         return None


def save_user_config(username, data):
    """Saves user configuration to JSON file."""
    if not username:
        print("Warning: Cannot save config, username is empty.")
        return False # Indicate failure

    config_path = get_config_path(username)
    try:
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Saved config for {username} to {config_path}")
        return True # Indicate success
    except IOError as e:
        print(f"Error saving config for {username} to {config_path}:\n{e}")
        # In a real app, you might want to signal this error to the UI
        return False # Indicate failure
    except Exception as e:
        print(f"An unexpected error occurred while saving config for {username}:\n{e}")
        return False # Indicate failure