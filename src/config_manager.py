
import json
import os

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_file):
            return self._get_default_config()
        
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()

    def _get_default_config(self):
        return {
            "save_format": "txt", # txt or json
            "local_llm": {
                "enabled": True,
                "url": "http://localhost:11434/v1",
                "model": "llama3",
                "api_key": "ollama" # Ollama usually handles any string
            },
            "gemini": {
                "enabled": True,
                "api_key": "",
                "model": "gemini-pro"
            }
        }

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save()

    def get_nested(self, section, key, default=None):
        return self.config.get(section, {}).get(key, default)

    def set_nested(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save()

    def save(self):
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
