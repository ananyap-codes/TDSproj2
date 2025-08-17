"""
Configuration settings for the Data Analyst Agent API
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')

    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 104857600))  # 100MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'temp_uploads')

    # Chart Configuration
    CHART_DPI = int(os.getenv('CHART_DPI', 100))
    CHART_MAX_SIZE_BYTES = int(os.getenv('CHART_MAX_SIZE_BYTES', 100000))  # 100KB
    CHART_FIGURE_SIZE = (10, 6)

    # Analysis Configuration
    ANALYSIS_TIMEOUT = int(os.getenv('ANALYSIS_TIMEOUT', 180))  # 3 minutes
    MAX_DATA_ROWS = int(os.getenv('MAX_DATA_ROWS', 100000))

    @staticmethod
    def validate():
        """Validate critical configuration"""
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")

        return True

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # Add production-specific settings

class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    # Use test database, etc.

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
