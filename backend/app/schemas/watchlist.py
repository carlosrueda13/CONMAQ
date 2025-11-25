from pydantic import BaseModel, ConfigDict
from datetime import datetime

class WatchlistBase(BaseModel):
    machine_id: int

class WatchlistCreate(WatchlistBase):
    pass

class Watchlist(WatchlistBase):
    id: int
    user_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
