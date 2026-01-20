import os

class Config:
    def __init__(self):        
        self.BASIC_AUTH_USERNAME = os.getenv("BASIC_AUTH_USERNAME")
        self.BASIC_AUTH_PASSWORD = os.getenv("BASIC_AUTH_PASSWORD")
        self.OLLAMA_URL = os.getenv("OLLAMA_URL")
        self.OLLAMA_LANG = os.getenv("OLLAMA_LANG", "en")
        self.WOLFRAM_URL = os.getenv("WOLFRAM_URL")
        self.YOLO_PATH = os.getenv("YOLO_PATH")

config = Config()
