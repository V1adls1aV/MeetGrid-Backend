from dotenv import load_dotenv

from app.core.settings import Settings

load_dotenv()

config = Settings()

__all__ = ["config"]
