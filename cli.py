"""
Command Line Interface for GrowPodEmpire
"""

import sys
import os
import argparse
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from growpodempire.app import GrowPodEmpire
from growpodempire.models import EnvironmentalCondition, GrowthStage
from growpodempire.api.flask_api import create_app


def create_pod_cmd(args, empire):
    """Create a new pod"""
    pod = empire.create_pod(args.id, args.name, args.capacity)
    print(f"✓ Created pod '{pod.name}' (ID: {pod.id}, Capacity: {pod.capacity})")


def list_pods_cmd(args, empire):
    """List all pods"""
    pods = empire.list_pods()
    if not pods:
        print("No pods found.")
        return
    
    print(f"\n{'ID':<15} {'Name':<30} {'Capacity':<10} {'Current':<10} {'Status'}")
    print("-" * 80)
    for pod in pods:
        status = "Active" if pod.active else "Inactive"
        print(f"{pod.id:<15} {pod.name:<30} {pod.capacity:<10} {len(pod.current_plants):<10} {status}")
    print()


def add_plant_cmd(args, empire):
    """Add a new plant"""
    try:
        plant = empire.add_plant(args.id, args.strain, args.pod_id)
        print(f"✓ Added plant '{plant.strain}' (ID: {plant.id}) to pod {plant.pod_id}")
    except ValueError as e:
        print(f"Error: {e}")


def list_plants_cmd(args, empire):
    """List all plants"""
    plants = empire.list_plants(pod_id=args.pod_id if hasattr(args, 'pod_id') else None)
    if not plants:
        print("No plants found.")
        return
    
    print(f"\n{'ID':<15} {'Strain':<20} {'Stage':<15} {'Height':<10} {'Health':<10} {'Pod'}")
    print("-" * 95)
    for plant in plants:
        height = f"{plant.height:.1f}cm" if plant.height else "N/A"
        health = f"{plant.health_score:.1f}" if plant.health_score else "N/A"
        print(f"{plant.id:<15} {plant.strain:<20} {plant.growth_stage.value:<15} {height:<10} {health:<10} {plant.pod_id}")
    print()


def record_growth_cmd(args, empire):
    """Record plant growth"""
    try:
        metrics = empire.record_growth(args.plant_id, args.height, args.leaf_count)
        print(f"✓ Recorded growth for plant {args.plant_id}")
        print(f"  Height: {metrics['height']}cm")
        print(f"  Health Score: {metrics['health_score']:.1f}")
        if metrics['growth_rate']:
            print(f"  Growth Rate: {metrics['growth_rate']:.2f} cm/day")
    except ValueError as e:
        print(f"Error: {e}")


def show_stats_cmd(args, empire):
    """Show system statistics"""
    stats = empire.get_system_stats()
    
    print("\n" + "=" * 60)
    print("  GrowPodEmpire System Statistics")
    print("=" * 60)
    print(f"\nPods:")
    print(f"  Total: {stats['total_pods']}")
    print(f"  Active: {stats['active_pods']}")
    
    print(f"\nPlants:")
    print(f"  Total: {stats['total_plants']}")
    print(f"  Active: {stats['active_plants']}")
    
    print(f"\nPlants by Growth Stage:")
    for stage, count in stats['plants_by_stage'].items():
        if count > 0:
            print(f"  {stage}: {count}")
    
    print(f"\nBlockchain:")
    print(f"  Total Blocks: {stats['blockchain']['total_blocks']}")
    print(f"  Data Integrity: {'✓ Valid' if stats['data_integrity'] else '✗ Invalid'}")
    print()


def serve_api_cmd(args, empire):
    """Start API server"""
    print(f"Starting GrowPodEmpire API server on {args.host}:{args.port}...")
    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='GrowPodEmpire - Professional Cannabis Cultivation Management Platform',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create-pod --id pod-001 --name "Veg Chamber" --capacity 10
  %(prog)s list-pods
  %(prog)s add-plant --id plant-001 --strain "OG Kush" --pod-id pod-001
  %(prog)s list-plants
  %(prog)s record-growth --plant-id plant-001 --height 25.5
  %(prog)s stats
  %(prog)s serve --host 0.0.0.0 --port 5000
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create pod command
    create_pod_parser = subparsers.add_parser('create-pod', help='Create a new growing pod')
    create_pod_parser.add_argument('--id', required=True, help='Pod ID')
    create_pod_parser.add_argument('--name', required=True, help='Pod name')
    create_pod_parser.add_argument('--capacity', type=int, required=True, help='Pod capacity')
    
    # List pods command
    list_pods_parser = subparsers.add_parser('list-pods', help='List all pods')
    
    # Add plant command
    add_plant_parser = subparsers.add_parser('add-plant', help='Add a new plant')
    add_plant_parser.add_argument('--id', required=True, help='Plant ID')
    add_plant_parser.add_argument('--strain', required=True, help='Plant strain')
    add_plant_parser.add_argument('--pod-id', required=True, help='Pod ID')
    
    # List plants command
    list_plants_parser = subparsers.add_parser('list-plants', help='List all plants')
    list_plants_parser.add_argument('--pod-id', help='Filter by pod ID')
    
    # Record growth command
    record_growth_parser = subparsers.add_parser('record-growth', help='Record plant growth')
    record_growth_parser.add_argument('--plant-id', required=True, help='Plant ID')
    record_growth_parser.add_argument('--height', type=float, required=True, help='Height in cm')
    record_growth_parser.add_argument('--leaf-count', type=int, help='Number of leaves')
    
    # Show stats command
    stats_parser = subparsers.add_parser('stats', help='Show system statistics')
    
    # Serve API command
    serve_parser = subparsers.add_parser('serve', help='Start API server')
    serve_parser.add_argument('--host', default='0.0.0.0', help='Host address')
    serve_parser.add_argument('--port', type=int, default=5000, help='Port number')
    serve_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize empire
    empire = GrowPodEmpire()
    
    # Command dispatch
    commands = {
        'create-pod': create_pod_cmd,
        'list-pods': list_pods_cmd,
        'add-plant': add_plant_cmd,
        'list-plants': list_plants_cmd,
        'record-growth': record_growth_cmd,
        'stats': show_stats_cmd,
        'serve': serve_api_cmd,
    }
    
    if args.command in commands:
        commands[args.command](args, empire)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
