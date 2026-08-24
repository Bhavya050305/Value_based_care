from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class PeerTargetRequest(BaseModel):
    aco_id: str = Field(..., description="Target ACO ID")
    performance_year: Optional[int] = Field(2024, description="Performance year (2022, 2023, 2024)")
    target_year: Optional[int] = Field(None, description="Legacy year parameter fallback")
    limit: int = Field(20, ge=1, le=100, description="Page limit")
    offset: int = Field(0, ge=0, description="Page offset")
    features: Optional[Dict[str, float]] = None

    def get_year(self) -> int:
        return self.performance_year or self.target_year or 2024


class PeerItem(BaseModel):
    rank: int
    aco_id: str
    aco_name: str
    savings_rate: float
    quality_score: float
    pmpm: float
    benchmark_pmpm: float
    attributed_members: int
    similarity_score: float
    state: str = "US"
    track: str = "MSSP Track 1+"


class OpportunityGap(BaseModel):
    savings_gap: float = 0.0
    quality_gap: float = 0.0
    pmpm_gap: float = 0.0
    potential_gross_savings_impact: float = 0.0


class TargetAcoSummary(BaseModel):
    aco_id: str
    aco_name: str
    performance_year: int
    current_savings_rate: float
    current_quality: float
    current_pmpm: float
    target_savings_rate: float
    target_quality: float
    target_pmpm: float
    classification: str = "Mid Quartile"


class PeerTargetResponse(BaseModel):
    aco_id: str
    performance_year: int
    target_aco: Optional[TargetAcoSummary] = None
    peers: List[PeerItem] = Field(default_factory=list)
    total: int = 0
    limit: int = 20
    offset: int = 0
    has_more: bool = False
    opportunity_gap: Optional[OpportunityGap] = None
    recommendation: Optional[str] = None
    peer_indices: Optional[List[int]] = None
    distances: Optional[List[float]] = None