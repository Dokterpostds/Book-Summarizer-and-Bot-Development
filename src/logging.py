from datetime import datetime
from src.global_settings import get_paths
import os

class ActionLogger:
    def __init__(self, theme, title):
        self.paths = get_paths(theme, title)
        # Extract the directory from the log file path
        log_dir = os.path.dirname(self.paths["LOG_FILE"])
        # Check if the directory exists, and create it if it doesn't
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        self.log_file = self.paths["LOG_FILE"]

    def log_action(self, action, action_type):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp}: {action_type} : {action}\n"
        with open(self.log_file, 'a') as file:
            file.write(log_entry)
    
    def reset_log(self):
        with open(self.log_file, 'w') as file:
            file.truncate(0)
