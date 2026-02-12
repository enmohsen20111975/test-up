import os
from pathlib import Path
from dotenv import load_dotenv

_backend_env = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_backend_env)

class Settings:
    # Database - User Database (for users, subscriptions, history, etc.)
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./users.db")
    
    # Database - Workflow Database (for equations, workflows, categories, etc.)
    WORKFLOW_DATABASE_URL = os.getenv("WORKFLOW_DATABASE_URL", "sqlite:///./workflows.db")
    
    # JWT
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-here")
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # AI Services
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
    DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
    QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    # Stripe
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # Paymob
    PAYMOB_API_KEY = os.getenv("PAYMOB_API_KEY")
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

settings = Settings()