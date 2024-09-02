import os
import yaml
from src.global_settings import get_paths

class SessionManager:
    def __init__(self, theme, title):
        self.paths = get_paths(theme, title)

    def save_session(self, state):
        state_to_save = {key: value for key, value in state.items()}
        try:
            with open(self.paths["SESSION_FILE"], 'w') as file:
                yaml.dump(state_to_save, file)
        except IOError as e:
            print(f"Error saving session: {e}")

    def load_session(self, state):
        if os.path.exists(self.paths["SESSION_FILE"]):
            try:
                with open(self.paths["SESSION_FILE"], 'r') as file:
                    loaded_state = yaml.safe_load(file) or {}
                    state.update(loaded_state)
                    return True
            except (IOError, yaml.YAMLError) as e:
                print(f"Error loading session: {e}")
                return False
        return False

    def delete_session(self, state):
        # Delete the session file if it exists
        if os.path.exists(self.paths["SESSION_FILE"]):
            try:
                os.remove(self.paths["SESSION_FILE"])
            except IOError as e:
                print(f"Error deleting session file: {e}")
        
        # Delete all files in the storage path
        if os.path.exists(self.paths["STORAGE_PATH"]):
            for filename in os.listdir(self.paths["STORAGE_PATH"]):
                file_path = os.path.join(self.paths["STORAGE_PATH"], filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.remove(file_path)
                except IOError as e:
                    print(f"Error deleting file {file_path}: {e}")
        
        # Clear the state dictionary
        state.clear()
