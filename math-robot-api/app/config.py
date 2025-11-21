import os

class Config:
    def __init__(self):        
        self.BASIC_AUTH_USERNAME = os.getenv("BASIC_AUTH_USERNAME")
        self.BASIC_AUTH_PASSWORD = os.getenv("BASIC_AUTH_PASSWORD")
        self.OLLAMA_URL = os.getenv("OLLAMA_URL")
        self.YOLO_PATH = os.getenv("YOLO_PATH")

config = Config()
