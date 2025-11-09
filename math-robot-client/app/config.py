import os
from dotenv import load_dotenv
from pathlib import Path

def _load_dotenv():
    this_file = Path(__file__)
    path = this_file.parent.parent.parent.joinpath('infrastructure/.env').resolve()
    if path.exists():
        load_dotenv(path)
        print(f"✅ Loaded environment from: {path}")
    else:
        print(f"⚠️  Environment file not found: {path}")

class Config:
    """Configuration class loaded from environment variables"""
    
    # API Configuration
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/api')
    API_USERNAME = os.getenv('API_USERNAME', 'admin')
    API_PASSWORD = os.getenv('API_PASSWORD', 'password')
    API_TARGET_REGIONS = os.getenv('API_TARGET_REGIONS', '1')
    
    # Wolfram Configuration
    WOLFRAM_KERNEL_PATH = os.getenv('WOLFRAM_KERNEL_PATH', '/usr/local/Wolfram/WolframEngine/13.1/Executables/WolframKernel')
    
    # Robot Configuration
    ROBOT_IP = os.getenv('ROBOT_IP', '127.0.0.1')
    ROBOT_PORT = int(os.getenv('ROBOT_PORT', '9559'))
    CAMERA_INDEX = int(os.getenv('CAMERA_INDEX', '0'))

_load_dotenv()
config = Config()