from typing import Optional, List
from pydantic import BaseModel


class Profile(BaseModel):
    name: str
    locale: str

class Storage(BaseModel):
    percentUsed: float

class Metadata(BaseModel):
    source: str
    collectionDate: str
    dataType: str

class User(BaseModel):
    userId: str
    email: str
    timestamp: int
    profile: Profile
    storage: Optional[Storage] = None
    metadata: Optional[Metadata] = None

# New models for browsing data
class BrowsingData(BaseModel):
    url: str
    timeSpent: int
    timestamp: int

class EvaluationMetrics(BaseModel):
    url_count: int
    timeSpent: List[int]
    points: int

class BrowsingDataWrapper(BaseModel):
    data: dict
    created_time: int
    data_hash: str
    author: str
    random_string: str
