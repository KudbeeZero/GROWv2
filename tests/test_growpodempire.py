"""
Tests for GrowPodEmpire Core Functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from datetime import datetime
from growpodempire.app import GrowPodEmpire
from growpodempire.models import EnvironmentalCondition, GrowthStage


class TestGrowPodEmpire:
    """Test suite for GrowPodEmpire platform"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.empire = GrowPodEmpire()
    
    def test_create_pod(self):
        """Test pod creation"""
        pod = self.empire.create_pod("test-pod-1", "Test Pod", capacity=5)
        assert pod.id == "test-pod-1"
        assert pod.name == "Test Pod"
        assert pod.capacity == 5
        assert pod.active is True
    
    def test_list_pods(self):
        """Test listing pods"""
        self.empire.create_pod("pod-1", "Pod 1", 5)
        self.empire.create_pod("pod-2", "Pod 2", 10)
        pods = self.empire.list_pods()
        assert len(pods) == 2
    
    def test_add_plant(self):
        """Test adding a plant"""
        self.empire.create_pod("pod-1", "Test Pod", 5)
        plant = self.empire.add_plant("plant-1", "OG Kush", "pod-1")
        assert plant.id == "plant-1"
        assert plant.strain == "OG Kush"
        assert plant.pod_id == "pod-1"
        assert plant.growth_stage == GrowthStage.SEED
    
    def test_add_plant_to_nonexistent_pod(self):
        """Test adding plant to non-existent pod raises error"""
        with pytest.raises(ValueError):
            self.empire.add_plant("plant-1", "OG Kush", "nonexistent-pod")
    
    def test_add_plant_to_full_pod(self):
        """Test adding plant to full pod raises error"""
        self.empire.create_pod("pod-1", "Test Pod", capacity=1)
        self.empire.add_plant("plant-1", "Strain 1", "pod-1")
        
        with pytest.raises(ValueError):
            self.empire.add_plant("plant-2", "Strain 2", "pod-1")
    
    def test_update_plant_stage(self):
        """Test updating plant growth stage"""
        self.empire.create_pod("pod-1", "Test Pod", 5)
        self.empire.add_plant("plant-1", "OG Kush", "pod-1")
        
        plant = self.empire.update_plant_stage("plant-1", GrowthStage.VEGETATIVE)
        assert plant.growth_stage == GrowthStage.VEGETATIVE
    
    def test_record_growth(self):
        """Test recording plant growth"""
        self.empire.create_pod("pod-1", "Test Pod", 5)
        self.empire.add_plant("plant-1", "OG Kush", "pod-1")
        
        metrics = self.empire.record_growth("plant-1", height=25.5, leaf_count=8)
        assert metrics['height'] == 25.5
        assert 'health_score' in metrics
    
    def test_growth_analytics(self):
        """Test growth analytics"""
        self.empire.create_pod("pod-1", "Test Pod", 5)
        self.empire.add_plant("plant-1", "OG Kush", "pod-1")
        
        self.empire.record_growth("plant-1", height=10.0)
        self.empire.record_growth("plant-1", height=15.0)
        self.empire.record_growth("plant-1", height=20.0)
        
        analytics = self.empire.get_growth_analytics("plant-1")
        assert analytics['total_measurements'] == 3
        assert analytics['current_height'] == 20.0
        assert analytics['height_gained'] == 10.0
    
    def test_record_environment(self):
        """Test recording environmental conditions"""
        self.empire.create_pod("pod-1", "Test Pod", 5)
        
        conditions = EnvironmentalCondition(
            temperature=24.5,
            humidity=55.0,
            co2_level=1200,
            light_intensity=600,
            ph_level=6.5
        )
        
        result = self.empire.record_environment("pod-1", conditions)
        assert result['recorded'] is True
        assert 'analysis' in result
    
    def test_environmental_analytics(self):
        """Test environmental analytics"""
        self.empire.create_pod("pod-1", "Test Pod", 5)
        
        for i in range(3):
            conditions = EnvironmentalCondition(
                temperature=24.0 + i,
                humidity=55.0,
                co2_level=1200,
                light_intensity=600,
                ph_level=6.5
            )
            self.empire.record_environment("pod-1", conditions)
        
        analytics = self.empire.get_environment_analytics("pod-1")
        assert analytics['measurements'] >= 3
        assert 'temperature' in analytics
        assert 'humidity' in analytics
    
    def test_record_harvest(self):
        """Test recording harvest"""
        self.empire.create_pod("pod-1", "Test Pod", 5)
        self.empire.add_plant("plant-1", "OG Kush", "pod-1")
        
        harvest = self.empire.record_harvest("plant-1", yield_amount=150.0, quality_score=9.0)
        assert harvest['yield_amount'] == 150.0
        assert harvest['quality_score'] == 9.0
        assert 'blockchain_record' in harvest
        
        # Verify plant removed from pod
        pod = self.empire.get_pod("pod-1")
        assert "plant-1" not in pod.current_plants
    
    def test_blockchain_integrity(self):
        """Test blockchain data integrity"""
        self.empire.create_pod("pod-1", "Test Pod", 5)
        self.empire.add_plant("plant-1", "OG Kush", "pod-1")
        
        # Verify blockchain is valid
        assert self.empire.verify_data_integrity() is True
        
        # Check blockchain info
        info = self.empire.get_blockchain_info()
        assert info['total_blocks'] > 1  # Genesis + plant records
        assert info['is_valid'] is True
    
    def test_plant_history(self):
        """Test retrieving plant history from blockchain"""
        self.empire.create_pod("pod-1", "Test Pod", 5)
        self.empire.add_plant("plant-1", "OG Kush", "pod-1")
        self.empire.update_plant_stage("plant-1", GrowthStage.VEGETATIVE)
        
        history = self.empire.get_plant_history("plant-1")
        assert len(history) >= 2  # At least planted + stage change
    
    def test_system_stats(self):
        """Test system statistics"""
        self.empire.create_pod("pod-1", "Test Pod", 5)
        self.empire.add_plant("plant-1", "OG Kush", "pod-1")
        
        stats = self.empire.get_system_stats()
        assert stats['total_pods'] == 1
        assert stats['total_plants'] == 1
        assert stats['active_plants'] == 1
        assert 'blockchain' in stats
        assert stats['data_integrity'] is True


class TestGrowthTracker:
    """Test suite for growth tracking system"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.empire = GrowPodEmpire()
        self.empire.create_pod("pod-1", "Test Pod", 5)
        self.empire.add_plant("plant-1", "Test Strain", "pod-1")
    
    def test_growth_rate_calculation(self):
        """Test growth rate calculation"""
        self.empire.record_growth("plant-1", height=10.0)
        metrics = self.empire.record_growth("plant-1", height=15.0)
        
        assert metrics['growth_rate'] is not None
        assert metrics['growth_rate'] > 0
    
    def test_health_score_adjustment(self):
        """Test health score adjustment based on growth"""
        plant = self.empire.get_plant("plant-1")
        initial_health = plant.health_score
        
        # Record multiple measurements
        for height in [10, 15, 20, 25]:
            self.empire.record_growth("plant-1", height=height)
        
        plant = self.empire.get_plant("plant-1")
        # Health score should be updated
        assert plant.health_score is not None


class TestEnvironmentalMonitor:
    """Test suite for environmental monitoring"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.empire = GrowPodEmpire()
        self.empire.create_pod("pod-1", "Test Pod", 5)
    
    def test_optimal_conditions(self):
        """Test detection of optimal conditions"""
        conditions = EnvironmentalCondition(
            temperature=24.0,
            humidity=50.0,
            co2_level=1200,
            light_intensity=600,
            ph_level=6.5
        )
        
        result = self.empire.record_environment("pod-1", conditions)
        analysis = result['analysis']
        
        assert analysis['temperature']['status'] == 'optimal'
        assert analysis['humidity']['status'] == 'optimal'
    
    def test_critical_conditions_alert(self):
        """Test alerts for critical conditions"""
        conditions = EnvironmentalCondition(
            temperature=35.0,  # Too high
            humidity=80.0,     # Too high
            co2_level=1200,
            light_intensity=600,
            ph_level=8.0       # Too high
        )
        
        result = self.empire.record_environment("pod-1", conditions)
        assert len(result['alerts']) > 0


class TestBlockchain:
    """Test suite for blockchain functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.empire = GrowPodEmpire()
    
    def test_genesis_block(self):
        """Test genesis block creation"""
        info = self.empire.get_blockchain_info()
        assert info['total_blocks'] >= 1  # At least genesis block
    
    def test_blockchain_records_plant_data(self):
        """Test blockchain records plant data"""
        self.empire.create_pod("pod-1", "Test Pod", 5)
        self.empire.add_plant("plant-1", "Test Strain", "pod-1")
        
        history = self.empire.get_plant_history("plant-1")
        assert len(history) > 0
        assert history[0]['data']['type'] == 'plant_data'
    
    def test_blockchain_verification(self):
        """Test blockchain verification"""
        self.empire.create_pod("pod-1", "Test Pod", 5)
        self.empire.add_plant("plant-1", "Test Strain", "pod-1")
        
        # Blockchain should be valid
        assert self.empire.blockchain.verify_chain() is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
