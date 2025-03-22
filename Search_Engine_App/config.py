import json
import os


class Config:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = {}
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                self.config = json.load(f)
        else:
            self.save_config()

    def save_config(self):
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=4)

    def get_ignore_patterns(self):
        return self.config.get("ignore_patterns", [])
