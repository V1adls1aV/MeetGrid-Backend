from pathlib import Path

from pydantic import computed_field
from pydantic_config import SettingsConfig, SettingsModel

from .db import RedisSettings
from .grid import GridSettings

PUBLIC_CONFIG_PATH = Path("config.yaml")

ENV_PREFIX = "MEET_GRID__"
ENV_SEPARATOR = "__"


class Settings(SettingsModel):
    APP_NAME: str
    ALLOW_ORIGINS: str
    SITE_BASE_URL: str

    REDIS: RedisSettings
    GRID: GridSettings

    @computed_field
    @property
    def ALLOW_ORIGINS_LIST(self) -> list[str]:
        return self.ALLOW_ORIGINS.split(",")

    model_config = SettingsConfig(
        nested_model_default_partial_update=True,
        config_merge=True,
        enable_decoding=True,
        case_sensitive=True,
        env_prefix=ENV_PREFIX,
        env_nested_delimiter=ENV_SEPARATOR,
        config_file=[PUBLIC_CONFIG_PATH],
        extra="allow",
    )
