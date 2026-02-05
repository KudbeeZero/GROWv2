"""
Intelligent Growth Tracking Service
Analyzes plant growth patterns and provides predictions
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict
import numpy as np
from ..models import Plant, GrowthMetrics, GrowthStage


class GrowthTracker:
    """Intelligent growth tracking and prediction system"""
    
    def __init__(self):
        self.growth_history: Dict[str, List[GrowthMetrics]] = {}
        # Average growth rates by stage (cm per day)
        self.stage_growth_rates = {
            GrowthStage.SEEDLING: 0.5,
            GrowthStage.VEGETATIVE: 2.0,
            GrowthStage.FLOWERING: 0.3,
        }
        # Average stage durations (days)
        self.stage_durations = {
            GrowthStage.SEED: 3,
            GrowthStage.GERMINATION: 7,
            GrowthStage.SEEDLING: 14,
            GrowthStage.VEGETATIVE: 30,
            GrowthStage.FLOWERING: 60,
        }
    
    def track_growth(self, plant: Plant, height: float, leaf_count: Optional[int] = None) -> GrowthMetrics:
        """Track plant growth and calculate metrics"""
        plant_history = self.growth_history.get(plant.id, [])
        
        # Calculate growth rate
        growth_rate = None
        if plant_history:
            last_metric = plant_history[-1]
            time_diff = (datetime.now() - last_metric.timestamp).total_seconds() / 86400  # days
            if time_diff > 0:
                height_diff = height - last_metric.height
                growth_rate = height_diff / time_diff
        
        # Calculate health score based on growth rate
        health_score = plant.health_score
        if growth_rate is not None:
            expected_rate = self.stage_growth_rates.get(plant.growth_stage, 1.0)
            if growth_rate < expected_rate * 0.5:
                health_score = max(50, health_score - 10)
            elif growth_rate > expected_rate * 1.5:
                health_score = min(100, health_score + 5)
        
        # Predict harvest date
        predicted_harvest = self._predict_harvest_date(plant, plant_history)
        
        metrics = GrowthMetrics(
            plant_id=plant.id,
            height=height,
            leaf_count=leaf_count,
            health_score=health_score,
            growth_rate=growth_rate,
            predicted_harvest_date=predicted_harvest
        )
        
        # Store metrics
        if plant.id not in self.growth_history:
            self.growth_history[plant.id] = []
        self.growth_history[plant.id].append(metrics)
        
        return metrics
    
    def _predict_harvest_date(self, plant: Plant, history: List[GrowthMetrics]) -> datetime:
        """Predict harvest date based on current stage and growth rate"""
        days_since_planted = (datetime.now() - plant.planted_date).days
        remaining_days = 0
        
        # Calculate remaining days based on current stage
        current_stage_index = list(GrowthStage).index(plant.growth_stage)
        for stage in list(GrowthStage)[current_stage_index:]:
            if stage == GrowthStage.HARVEST:
                break
            remaining_days += self.stage_durations.get(stage, 0)
        
        # Adjust based on growth rate if available
        if history and len(history) > 3:
            recent_metrics = history[-5:]
            avg_growth_rate = np.mean([m.growth_rate for m in recent_metrics if m.growth_rate])
            expected_rate = self.stage_growth_rates.get(plant.growth_stage, 1.0)
            
            if avg_growth_rate > 0:
                rate_ratio = expected_rate / avg_growth_rate
                remaining_days = int(remaining_days * rate_ratio)
        
        return datetime.now() + timedelta(days=remaining_days)
    
    def get_growth_analytics(self, plant_id: str) -> Dict:
        """Get comprehensive growth analytics for a plant"""
        history = self.growth_history.get(plant_id, [])
        
        if not history:
            return {"error": "No growth data available"}
        
        heights = [m.height for m in history]
        growth_rates = [m.growth_rate for m in history if m.growth_rate is not None]
        
        analytics = {
            "total_measurements": len(history),
            "current_height": heights[-1] if heights else 0,
            "height_gained": heights[-1] - heights[0] if len(heights) > 1 else 0,
            "average_growth_rate": float(np.mean(growth_rates)) if growth_rates else 0,
            "current_health_score": history[-1].health_score,
            "predicted_harvest": history[-1].predicted_harvest_date.isoformat() if history[-1].predicted_harvest_date else None,
        }
        
        return analytics
