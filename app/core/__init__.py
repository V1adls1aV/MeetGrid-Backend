from app.core.settings import Settings
from dotenv import load_dotenv

load_dotenv()

config = Settings()

__all__ = ["config"]
