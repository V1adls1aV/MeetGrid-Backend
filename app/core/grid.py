from pydantic import BaseModel


class GridSettings(BaseModel):
    SLOT_MINUTES_SIZE: int
