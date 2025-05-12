from typing import Optional, List
from pydantic import BaseModel

from refiner.models.offchain_schema import OffChainSchema

class BrowsingEntryOutput(BaseModel):
    url: str
    timeSpent: int
    timestamp: int

class BrowsingStatsOutput(BaseModel):
    urls: int
    averageTimeSpent: float
    type: str

class BrowsingOutput(BaseModel):
    stats: BrowsingStatsOutput
    data: List[BrowsingEntryOutput]

class Output(BaseModel):
    refinement_url: Optional[str] = None
    schema: Optional[OffChainSchema] = None
    browsing_data: Optional[BrowsingOutput] = None
