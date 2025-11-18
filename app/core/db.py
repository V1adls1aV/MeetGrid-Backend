from pydantic import BaseModel
from pydantic import computed_field
from functools import cached_property


class RedisSettings(BaseModel):
    HOST: str
    PORT: int
    DB: int

    PASSWORD: str | None = None
    USE_TLS: bool = False

    TTL_DAYS: int

    @computed_field
    @cached_property
    def URL(self) -> str:
        if self.USE_TLS:
            return (
                f"rediss://"
                f":{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}"
                f"?ssl_cert_reqs=none&ssl_check_hostname=false"
            )

        return f"redis://:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}"
