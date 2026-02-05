"""
Environmental Monitoring Service
Monitors and analyzes environmental conditions
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import numpy as np
from ..models import EnvironmentalCondition, GrowPod


class EnvironmentalMonitor:
    """Environmental monitoring and analysis system"""
    
    def __init__(self):
        self.condition_history: Dict[str, List[EnvironmentalCondition]] = {}
        # Optimal ranges for cannabis cultivation
        self.optimal_ranges = {
            "temperature": (20, 28),  # Celsius
            "humidity": (40, 60),  # Percentage
            "co2_level": (800, 1500),  # ppm
            "light_intensity": (400, 700),  # lumens
            "ph_level": (6.0, 7.0),
        }
    
    def record_conditions(self, pod_id: str, conditions: EnvironmentalCondition) -> Dict:
        """Record environmental conditions and analyze"""
        if pod_id not in self.condition_history:
            self.condition_history[pod_id] = []
        
        self.condition_history[pod_id].append(conditions)
        
        # Analyze conditions
        analysis = self._analyze_conditions(conditions)
        
        return {
            "recorded": True,
            "timestamp": conditions.timestamp.isoformat(),
            "analysis": analysis,
            "alerts": self._generate_alerts(conditions)
        }
    
    def _analyze_conditions(self, conditions: EnvironmentalCondition) -> Dict:
        """Analyze if conditions are within optimal ranges"""
        analysis = {}
        
        for param, value in conditions.model_dump().items():
            if param == "timestamp":
                continue
            
            if param in self.optimal_ranges:
                min_val, max_val = self.optimal_ranges[param]
                
                if min_val <= value <= max_val:
                    status = "optimal"
                elif min_val * 0.9 <= value <= max_val * 1.1:
                    status = "acceptable"
                else:
                    status = "critical"
                
                analysis[param] = {
                    "value": value,
                    "status": status,
                    "optimal_range": f"{min_val}-{max_val}"
                }
        
        return analysis
    
    def _generate_alerts(self, conditions: EnvironmentalCondition) -> List[str]:
        """Generate alerts for critical conditions"""
        alerts = []
        
        temp_min, temp_max = self.optimal_ranges["temperature"]
        if conditions.temperature < temp_min * 0.9:
            alerts.append(f"Temperature too low: {conditions.temperature}°C")
        elif conditions.temperature > temp_max * 1.1:
            alerts.append(f"Temperature too high: {conditions.temperature}°C")
        
        hum_min, hum_max = self.optimal_ranges["humidity"]
        if conditions.humidity < hum_min * 0.9:
            alerts.append(f"Humidity too low: {conditions.humidity}%")
        elif conditions.humidity > hum_max * 1.1:
            alerts.append(f"Humidity too high: {conditions.humidity}%")
        
        ph_min, ph_max = self.optimal_ranges["ph_level"]
        if conditions.ph_level < ph_min or conditions.ph_level > ph_max:
            alerts.append(f"pH level out of range: {conditions.ph_level}")
        
        return alerts
    
    def get_environment_analytics(self, pod_id: str, hours: int = 24) -> Dict:
        """Get environmental analytics for a pod over specified time period"""
        history = self.condition_history.get(pod_id, [])
        
        if not history:
            return {"error": "No environmental data available"}
        
        # Filter by time period
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_history = [c for c in history if c.timestamp >= cutoff_time]
        
        if not recent_history:
            recent_history = history[-10:] if len(history) > 10 else history
        
        # Calculate statistics
        temps = [c.temperature for c in recent_history]
        humidities = [c.humidity for c in recent_history]
        co2_levels = [c.co2_level for c in recent_history]
        
        analytics = {
            "period_hours": hours,
            "measurements": len(recent_history),
            "temperature": {
                "average": float(np.mean(temps)),
                "min": float(np.min(temps)),
                "max": float(np.max(temps)),
                "std_dev": float(np.std(temps))
            },
            "humidity": {
                "average": float(np.mean(humidities)),
                "min": float(np.min(humidities)),
                "max": float(np.max(humidities)),
                "std_dev": float(np.std(humidities))
            },
            "co2": {
                "average": float(np.mean(co2_levels)),
                "min": float(np.min(co2_levels)),
                "max": float(np.max(co2_levels)),
            },
            "overall_status": self._get_overall_status(recent_history[-1] if recent_history else None)
        }
        
        return analytics
    
    def _get_overall_status(self, latest_condition: Optional[EnvironmentalCondition]) -> str:
        """Determine overall environmental status"""
        if not latest_condition:
            return "unknown"
        
        analysis = self._analyze_conditions(latest_condition)
        
        critical_count = sum(1 for v in analysis.values() if v["status"] == "critical")
        
        if critical_count > 0:
            return "critical"
        
        acceptable_count = sum(1 for v in analysis.values() if v["status"] == "acceptable")
        if acceptable_count > 2:
            return "acceptable"
        
        return "optimal"
