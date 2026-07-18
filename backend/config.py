import os
from dotenv import load_dotenv

load_dotenv()

# Database connection string
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/retail_intelligence"
)

# JWT settings
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
ALGORITHM = "HS256"

# File storage directories
UPLOAD_DIR = "uploads"
MODEL_DIR = "ml_models"

# Create directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
