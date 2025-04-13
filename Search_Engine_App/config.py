import json
import os

class Config:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = {}
        self.ignore_patterns = []
        self.report_format = None
        self.ranking_method = None
        self.db_url = None
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
        self.ranking_method = data.get("ranking_method", "length")
        self.db_url = data.get("db_url")

    def get_ignore_patterns(self):
        return self.ignore_patterns

    def get_report_format(self):
        return self.report_format

    def get_allowed_extensions(self):
        return self.config.get("allowed_extensions", [".txt"])

    def get_ranking_method(self):
        return self.ranking_method

    def get_db_url(self):
        return self.config.get("db_url", "")