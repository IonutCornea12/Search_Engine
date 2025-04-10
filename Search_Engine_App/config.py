import json
import os

class Config:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = {}
        self.ignore_patterns = []
        self.report_format = None
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "report_format" not in data:
            raise KeyError("Missing 'report_format' in config.json")

        self.config = data
        self.ignore_patterns = data.get("ignore_patterns", [])
        self.report_format = data["report_format"]

    def get_ignore_patterns(self):
        return self.ignore_patterns

    def get_report_format(self):
        return self.report_format