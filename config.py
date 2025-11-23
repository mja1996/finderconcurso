import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    API_HOST = os.getenv('API_HOST', 'http://localhost:5000')
    API_PORT = int(os.getenv('API_PORT', 5000))
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'concursos.db')
    
    # Scraping
    SCRAPE_INTERVAL_HOURS = int(os.getenv('SCRAPE_INTERVAL_HOURS', 6))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 10))
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    
    # Environment
    DEBUG = os.getenv('DEBUG', 'False') == 'True'

config = Config()
