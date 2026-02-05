"""
Data models for GrowPodEmpire platform
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class GrowthStage(str, Enum):
    """Growth stages of cannabis plants"""
    SEED = "seed"
    GERMINATION = "germination"
    SEEDLING = "seedling"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    HARVEST = "harvest"


class EnvironmentalCondition(BaseModel):
    """Environmental monitoring data"""
    timestamp: datetime = Field(default_factory=datetime.now)
    temperature: float = Field(description="Temperature in Celsius")
    humidity: float = Field(description="Relative humidity percentage")
    co2_level: float = Field(description="CO2 level in ppm")
    light_intensity: float = Field(description="Light intensity in lumens")
    ph_level: float = Field(description="pH level of growing medium")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Plant(BaseModel):
    """Cannabis plant model"""
    id: str
    strain: str
    growth_stage: GrowthStage = GrowthStage.SEED
    planted_date: datetime = Field(default_factory=datetime.now)
    pod_id: str
    height: Optional[float] = None  # in cm
    health_score: float = Field(default=100.0, ge=0, le=100)
    notes: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class GrowPod(BaseModel):
    """Growing pod/container model"""
    id: str
    name: str
    capacity: int = Field(description="Maximum number of plants")
    current_plants: List[str] = Field(default_factory=list)
    current_conditions: Optional[EnvironmentalCondition] = None
    active: bool = True
    
    
class GrowthMetrics(BaseModel):
    """Intelligent growth tracking metrics"""
    plant_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    height: float
    leaf_count: Optional[int] = None
    health_score: float
    growth_rate: Optional[float] = None  # cm per day
    predicted_harvest_date: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BlockchainRecord(BaseModel):
    """Blockchain record for data integrity"""
    record_id: str
    record_type: str  # 'plant', 'environment', 'harvest', etc.
    data_hash: str
    previous_hash: str
    timestamp: datetime = Field(default_factory=datetime.now)
    block_number: int
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
