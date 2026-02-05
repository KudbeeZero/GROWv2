"""
Main Application Manager for GrowPodEmpire
Coordinates all services and provides high-level interface
"""

from typing import Dict, List, Optional
from datetime import datetime
from .models import Plant, GrowPod, EnvironmentalCondition, GrowthStage
from .services import GrowthTracker, EnvironmentalMonitor
from .blockchain import CultivationBlockchain


class GrowPodEmpire:
    """
    Main application class for GrowPodEmpire v1.0
    Professional Cannabis Cultivation Management Platform
    """
    
    def __init__(self):
        self.plants: Dict[str, Plant] = {}
        self.pods: Dict[str, GrowPod] = {}
        self.growth_tracker = GrowthTracker()
        self.environmental_monitor = EnvironmentalMonitor()
        self.blockchain = CultivationBlockchain()
    
    # Pod Management
    def create_pod(self, pod_id: str, name: str, capacity: int) -> GrowPod:
        """Create a new growing pod"""
        pod = GrowPod(id=pod_id, name=name, capacity=capacity)
        self.pods[pod_id] = pod
        return pod
    
    def get_pod(self, pod_id: str) -> Optional[GrowPod]:
        """Get pod by ID"""
        return self.pods.get(pod_id)
    
    def list_pods(self) -> List[GrowPod]:
        """List all pods"""
        return list(self.pods.values())
    
    # Plant Management
    def add_plant(self, plant_id: str, strain: str, pod_id: str) -> Plant:
        """Add a new plant to a pod"""
        if pod_id not in self.pods:
            raise ValueError(f"Pod {pod_id} not found")
        
        pod = self.pods[pod_id]
        if len(pod.current_plants) >= pod.capacity:
            raise ValueError(f"Pod {pod_id} is at full capacity")
        
        plant = Plant(
            id=plant_id,
            strain=strain,
            pod_id=pod_id,
            planted_date=datetime.now()
        )
        
        self.plants[plant_id] = plant
        pod.current_plants.append(plant_id)
        
        # Record on blockchain
        self.blockchain.record_plant_data(plant_id, {
            "action": "planted",
            "strain": strain,
            "pod_id": pod_id
        })
        
        return plant
    
    def get_plant(self, plant_id: str) -> Optional[Plant]:
        """Get plant by ID"""
        return self.plants.get(plant_id)
    
    def list_plants(self, pod_id: Optional[str] = None) -> List[Plant]:
        """List all plants, optionally filtered by pod"""
        plants = list(self.plants.values())
        if pod_id:
            plants = [p for p in plants if p.pod_id == pod_id]
        return plants
    
    def update_plant_stage(self, plant_id: str, stage: GrowthStage) -> Plant:
        """Update plant growth stage"""
        if plant_id not in self.plants:
            raise ValueError(f"Plant {plant_id} not found")
        
        plant = self.plants[plant_id]
        old_stage = plant.growth_stage
        plant.growth_stage = stage
        
        # Record stage change on blockchain
        self.blockchain.record_plant_data(plant_id, {
            "action": "stage_change",
            "old_stage": old_stage.value,
            "new_stage": stage.value
        })
        
        return plant
    
    # Growth Tracking
    def record_growth(self, plant_id: str, height: float, leaf_count: Optional[int] = None) -> Dict:
        """Record plant growth measurement"""
        if plant_id not in self.plants:
            raise ValueError(f"Plant {plant_id} not found")
        
        plant = self.plants[plant_id]
        metrics = self.growth_tracker.track_growth(plant, height, leaf_count)
        
        # Update plant data
        plant.height = height
        plant.health_score = metrics.health_score
        
        # Record on blockchain
        self.blockchain.record_plant_data(plant_id, {
            "action": "growth_measurement",
            "height": height,
            "health_score": metrics.health_score,
            "growth_rate": metrics.growth_rate
        })
        
        return metrics.model_dump()
    
    def get_growth_analytics(self, plant_id: str) -> Dict:
        """Get growth analytics for a plant"""
        return self.growth_tracker.get_growth_analytics(plant_id)
    
    # Environmental Monitoring
    def record_environment(self, pod_id: str, conditions: EnvironmentalCondition) -> Dict:
        """Record environmental conditions for a pod"""
        if pod_id not in self.pods:
            raise ValueError(f"Pod {pod_id} not found")
        
        result = self.environmental_monitor.record_conditions(pod_id, conditions)
        
        # Update pod current conditions
        self.pods[pod_id].current_conditions = conditions
        
        # Record on blockchain
        self.blockchain.record_environmental_data(pod_id, conditions.model_dump())
        
        return result
    
    def get_environment_analytics(self, pod_id: str, hours: int = 24) -> Dict:
        """Get environmental analytics for a pod"""
        return self.environmental_monitor.get_environment_analytics(pod_id, hours)
    
    # Harvest Management
    def record_harvest(self, plant_id: str, yield_amount: float, quality_score: float) -> Dict:
        """Record plant harvest"""
        if plant_id not in self.plants:
            raise ValueError(f"Plant {plant_id} not found")
        
        plant = self.plants[plant_id]
        plant.growth_stage = GrowthStage.HARVEST
        
        harvest_data = {
            "plant_id": plant_id,
            "strain": plant.strain,
            "harvest_date": datetime.now().isoformat(),
            "yield_amount": yield_amount,
            "quality_score": quality_score,
            "days_to_harvest": (datetime.now() - plant.planted_date).days
        }
        
        # Record on blockchain
        blockchain_record = self.blockchain.record_harvest(plant_id, harvest_data)
        
        # Remove from pod
        if plant.pod_id in self.pods:
            pod = self.pods[plant.pod_id]
            if plant_id in pod.current_plants:
                pod.current_plants.remove(plant_id)
        
        return {
            **harvest_data,
            "blockchain_record": blockchain_record.model_dump()
        }
    
    # Blockchain Operations
    def get_blockchain_info(self) -> Dict:
        """Get blockchain information"""
        return self.blockchain.get_chain_info()
    
    def get_plant_history(self, plant_id: str) -> List[Dict]:
        """Get complete blockchain history for a plant"""
        return self.blockchain.get_records_by_id(plant_id)
    
    def verify_data_integrity(self) -> bool:
        """Verify blockchain data integrity"""
        return self.blockchain.verify_chain()
    
    # System Stats
    def get_system_stats(self) -> Dict:
        """Get overall system statistics"""
        active_plants = [p for p in self.plants.values() if p.growth_stage != GrowthStage.HARVEST]
        
        return {
            "total_pods": len(self.pods),
            "active_pods": len([p for p in self.pods.values() if p.active]),
            "total_plants": len(self.plants),
            "active_plants": len(active_plants),
            "plants_by_stage": {
                stage.value: len([p for p in active_plants if p.growth_stage == stage])
                for stage in GrowthStage
            },
            "blockchain": self.blockchain.get_chain_info(),
            "data_integrity": self.verify_data_integrity()
        }
