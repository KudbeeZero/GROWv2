"""
Demo script showing GrowPodEmpire v1.0 capabilities
"""

from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from growpodempire.app import GrowPodEmpire
from growpodempire.models import EnvironmentalCondition, GrowthStage


def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_growpod_empire():
    """Demonstrate GrowPodEmpire platform features"""
    
    print_section("GrowPodEmpire v1.0 - Professional Cannabis Cultivation Platform")
    
    # Initialize the platform
    empire = GrowPodEmpire()
    print("✓ Platform initialized")
    
    # Create growing pods
    print_section("1. Creating Growing Pods")
    pod1 = empire.create_pod("pod-001", "Vegetative Chamber A", capacity=10)
    pod2 = empire.create_pod("pod-002", "Flowering Chamber B", capacity=8)
    print(f"✓ Created pod: {pod1.name} (capacity: {pod1.capacity})")
    print(f"✓ Created pod: {pod2.name} (capacity: {pod2.capacity})")
    
    # Add plants
    print_section("2. Adding Plants")
    plant1 = empire.add_plant("plant-001", "OG Kush", "pod-001")
    plant2 = empire.add_plant("plant-002", "Blue Dream", "pod-001")
    plant3 = empire.add_plant("plant-003", "Girl Scout Cookies", "pod-002")
    print(f"✓ Planted: {plant1.strain} in {pod1.name}")
    print(f"✓ Planted: {plant2.strain} in {pod1.name}")
    print(f"✓ Planted: {plant3.strain} in {pod2.name}")
    
    # Update growth stages
    print_section("3. Tracking Growth Stages")
    empire.update_plant_stage("plant-001", GrowthStage.VEGETATIVE)
    empire.update_plant_stage("plant-002", GrowthStage.SEEDLING)
    empire.update_plant_stage("plant-003", GrowthStage.FLOWERING)
    print(f"✓ {plant1.strain}: {plant1.growth_stage.value}")
    print(f"✓ {plant2.strain}: {empire.get_plant('plant-002').growth_stage.value}")
    print(f"✓ {plant3.strain}: {empire.get_plant('plant-003').growth_stage.value}")
    
    # Record growth measurements
    print_section("4. Intelligent Growth Tracking")
    metrics1 = empire.record_growth("plant-001", height=25.5, leaf_count=8)
    metrics2 = empire.record_growth("plant-001", height=28.3, leaf_count=10)
    metrics3 = empire.record_growth("plant-001", height=32.1, leaf_count=12)
    
    print(f"✓ Measurement 1: Height {metrics1['height']}cm, Health {metrics1['health_score']:.1f}")
    print(f"✓ Measurement 2: Height {metrics2['height']}cm, Health {metrics2['health_score']:.1f}")
    print(f"✓ Measurement 3: Height {metrics3['height']}cm, Health {metrics3['health_score']:.1f}, Growth Rate {metrics3['growth_rate']:.2f}cm/day")
    
    # Get growth analytics
    analytics = empire.get_growth_analytics("plant-001")
    print(f"\n📊 Growth Analytics for {plant1.strain}:")
    print(f"   - Current Height: {analytics['current_height']}cm")
    print(f"   - Height Gained: {analytics['height_gained']}cm")
    print(f"   - Average Growth Rate: {analytics['average_growth_rate']:.2f}cm/day")
    print(f"   - Health Score: {analytics['current_health_score']:.1f}")
    
    # Environmental monitoring
    print_section("5. Environmental Monitoring")
    
    # Record optimal conditions
    conditions1 = EnvironmentalCondition(
        temperature=24.5,
        humidity=55.0,
        co2_level=1200,
        light_intensity=600,
        ph_level=6.5
    )
    result1 = empire.record_environment("pod-001", conditions1)
    print(f"✓ Recorded optimal conditions for {pod1.name}")
    print(f"   Temperature: {conditions1.temperature}°C - {result1['analysis']['temperature']['status']}")
    print(f"   Humidity: {conditions1.humidity}% - {result1['analysis']['humidity']['status']}")
    print(f"   CO2: {conditions1.co2_level}ppm - {result1['analysis']['co2_level']['status']}")
    
    # Record suboptimal conditions
    conditions2 = EnvironmentalCondition(
        temperature=32.0,  # Too high
        humidity=75.0,     # Too high
        co2_level=900,
        light_intensity=550,
        ph_level=7.2       # Too high
    )
    result2 = empire.record_environment("pod-002", conditions2)
    print(f"\n⚠ Recorded suboptimal conditions for {pod2.name}")
    if result2['alerts']:
        for alert in result2['alerts']:
            print(f"   ALERT: {alert}")
    
    # Get environmental analytics
    env_analytics = empire.get_environment_analytics("pod-001")
    print(f"\n📊 Environmental Analytics for {pod1.name}:")
    print(f"   - Average Temperature: {env_analytics['temperature']['average']:.1f}°C")
    print(f"   - Average Humidity: {env_analytics['humidity']['average']:.1f}%")
    print(f"   - Overall Status: {env_analytics['overall_status']}")
    
    # Blockchain verification
    print_section("6. Blockchain Data Integrity")
    blockchain_info = empire.get_blockchain_info()
    print(f"✓ Total Blocks: {blockchain_info['total_blocks']}")
    print(f"✓ Chain Valid: {blockchain_info['is_valid']}")
    print(f"✓ Latest Block: #{blockchain_info['latest_block']['number']}")
    print(f"✓ Latest Hash: {blockchain_info['latest_block']['hash'][:16]}...")
    
    # Get plant history from blockchain
    history = empire.get_plant_history("plant-001")
    print(f"\n📜 Blockchain History for {plant1.strain}:")
    for i, record in enumerate(history[:3], 1):  # Show first 3 records
        action = record['data'].get('action', record['data'].get('type', 'unknown'))
        print(f"   {i}. Block #{record['block_number']}: {action}")
    
    # Simulate harvest
    print_section("7. Harvest Recording")
    harvest_result = empire.record_harvest("plant-003", yield_amount=150.5, quality_score=9.2)
    print(f"✓ Harvested: {harvest_result['strain']}")
    print(f"   Yield: {harvest_result['yield_amount']}g")
    print(f"   Quality Score: {harvest_result['quality_score']}/10")
    print(f"   Days to Harvest: {harvest_result['days_to_harvest']}")
    print(f"   Recorded on Blockchain: Block #{harvest_result['blockchain_record']['block_number']}")
    
    # System statistics
    print_section("8. System Statistics")
    stats = empire.get_system_stats()
    print(f"📊 Platform Overview:")
    print(f"   - Total Pods: {stats['total_pods']}")
    print(f"   - Active Plants: {stats['active_plants']}")
    print(f"   - Total Blockchain Blocks: {stats['blockchain']['total_blocks']}")
    print(f"   - Data Integrity Verified: {stats['data_integrity']}")
    print(f"\n   Plants by Growth Stage:")
    for stage, count in stats['plants_by_stage'].items():
        if count > 0:
            print(f"   - {stage}: {count}")
    
    print_section("Demo Complete!")
    print("GrowPodEmpire v1.0 successfully demonstrates:")
    print("  ✓ Intelligent growth tracking")
    print("  ✓ Environmental monitoring")
    print("  ✓ Blockchain data integrity")
    print("\n")


if __name__ == "__main__":
    demo_growpod_empire()
