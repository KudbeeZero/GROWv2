"""
Simple test runner without pytest to avoid web3 dependency issues
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from growpodempire.app import GrowPodEmpire
from growpodempire.models import EnvironmentalCondition, GrowthStage


def test_create_pod():
    """Test pod creation"""
    empire = GrowPodEmpire()
    pod = empire.create_pod("test-pod-1", "Test Pod", capacity=5)
    assert pod.id == "test-pod-1"
    assert pod.name == "Test Pod"
    assert pod.capacity == 5
    print("✓ test_create_pod passed")


def test_add_plant():
    """Test adding a plant"""
    empire = GrowPodEmpire()
    empire.create_pod("pod-1", "Test Pod", 5)
    plant = empire.add_plant("plant-1", "OG Kush", "pod-1")
    assert plant.id == "plant-1"
    assert plant.strain == "OG Kush"
    assert plant.pod_id == "pod-1"
    assert plant.growth_stage == GrowthStage.SEED
    print("✓ test_add_plant passed")


def test_update_plant_stage():
    """Test updating plant growth stage"""
    empire = GrowPodEmpire()
    empire.create_pod("pod-1", "Test Pod", 5)
    empire.add_plant("plant-1", "OG Kush", "pod-1")
    plant = empire.update_plant_stage("plant-1", GrowthStage.VEGETATIVE)
    assert plant.growth_stage == GrowthStage.VEGETATIVE
    print("✓ test_update_plant_stage passed")


def test_record_growth():
    """Test recording plant growth"""
    empire = GrowPodEmpire()
    empire.create_pod("pod-1", "Test Pod", 5)
    empire.add_plant("plant-1", "OG Kush", "pod-1")
    metrics = empire.record_growth("plant-1", height=25.5, leaf_count=8)
    assert metrics['height'] == 25.5
    assert 'health_score' in metrics
    print("✓ test_record_growth passed")


def test_growth_analytics():
    """Test growth analytics"""
    empire = GrowPodEmpire()
    empire.create_pod("pod-1", "Test Pod", 5)
    empire.add_plant("plant-1", "OG Kush", "pod-1")
    
    empire.record_growth("plant-1", height=10.0)
    empire.record_growth("plant-1", height=15.0)
    empire.record_growth("plant-1", height=20.0)
    
    analytics = empire.get_growth_analytics("plant-1")
    assert analytics['total_measurements'] == 3
    assert analytics['current_height'] == 20.0
    assert analytics['height_gained'] == 10.0
    print("✓ test_growth_analytics passed")


def test_record_environment():
    """Test recording environmental conditions"""
    empire = GrowPodEmpire()
    empire.create_pod("pod-1", "Test Pod", 5)
    
    conditions = EnvironmentalCondition(
        temperature=24.5,
        humidity=55.0,
        co2_level=1200,
        light_intensity=600,
        ph_level=6.5
    )
    
    result = empire.record_environment("pod-1", conditions)
    assert result['recorded'] is True
    assert 'analysis' in result
    print("✓ test_record_environment passed")


def test_environmental_analytics():
    """Test environmental analytics"""
    empire = GrowPodEmpire()
    empire.create_pod("pod-1", "Test Pod", 5)
    
    for i in range(3):
        conditions = EnvironmentalCondition(
            temperature=24.0 + i,
            humidity=55.0,
            co2_level=1200,
            light_intensity=600,
            ph_level=6.5
        )
        empire.record_environment("pod-1", conditions)
    
    analytics = empire.get_environment_analytics("pod-1")
    assert analytics['measurements'] >= 3
    assert 'temperature' in analytics
    assert 'humidity' in analytics
    print("✓ test_environmental_analytics passed")


def test_record_harvest():
    """Test recording harvest"""
    empire = GrowPodEmpire()
    empire.create_pod("pod-1", "Test Pod", 5)
    empire.add_plant("plant-1", "OG Kush", "pod-1")
    
    harvest = empire.record_harvest("plant-1", yield_amount=150.0, quality_score=9.0)
    assert harvest['yield_amount'] == 150.0
    assert harvest['quality_score'] == 9.0
    assert 'blockchain_record' in harvest
    
    # Verify plant removed from pod
    pod = empire.get_pod("pod-1")
    assert "plant-1" not in pod.current_plants
    print("✓ test_record_harvest passed")


def test_blockchain_integrity():
    """Test blockchain data integrity"""
    empire = GrowPodEmpire()
    empire.create_pod("pod-1", "Test Pod", 5)
    empire.add_plant("plant-1", "OG Kush", "pod-1")
    
    # Verify blockchain is valid
    assert empire.verify_data_integrity() is True
    
    # Check blockchain info
    info = empire.get_blockchain_info()
    assert info['total_blocks'] > 1  # Genesis + plant records
    assert info['is_valid'] is True
    print("✓ test_blockchain_integrity passed")


def test_plant_history():
    """Test retrieving plant history from blockchain"""
    empire = GrowPodEmpire()
    empire.create_pod("pod-1", "Test Pod", 5)
    empire.add_plant("plant-1", "OG Kush", "pod-1")
    empire.update_plant_stage("plant-1", GrowthStage.VEGETATIVE)
    
    history = empire.get_plant_history("plant-1")
    assert len(history) >= 2  # At least planted + stage change
    print("✓ test_plant_history passed")


def test_system_stats():
    """Test system statistics"""
    empire = GrowPodEmpire()
    empire.create_pod("pod-1", "Test Pod", 5)
    empire.add_plant("plant-1", "OG Kush", "pod-1")
    
    stats = empire.get_system_stats()
    assert stats['total_pods'] == 1
    assert stats['total_plants'] == 1
    assert stats['active_plants'] == 1
    assert 'blockchain' in stats
    assert stats['data_integrity'] is True
    print("✓ test_system_stats passed")


def run_all_tests():
    """Run all tests"""
    print("\nRunning GrowPodEmpire Tests...\n")
    print("=" * 60)
    
    tests = [
        test_create_pod,
        test_add_plant,
        test_update_plant_stage,
        test_record_growth,
        test_growth_analytics,
        test_record_environment,
        test_environmental_analytics,
        test_record_harvest,
        test_blockchain_integrity,
        test_plant_history,
        test_system_stats,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
    
    print("=" * 60)
    print(f"\nTest Results: {passed} passed, {failed} failed")
    print(f"Total: {passed + failed} tests\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
