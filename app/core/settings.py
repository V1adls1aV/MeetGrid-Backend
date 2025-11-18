from pydantic import computed_field
from pathlib import Path
from .db import RedisSettings
from .grid import GridSettings
from pydantic_config import SettingsConfig, SettingsModel

PUBLIC_CONFIG_PATH = Path("config.yaml")

ENV_PREFIX = "MEET_GRID__"
ENV_SEPARATOR = "__"


class Settings(SettingsModel):
    APP_NAME: str
    REDIS: RedisSettings
    GRID: GridSettings
    ALLOW_ORIGINS: str

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
