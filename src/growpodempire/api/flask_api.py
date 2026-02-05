"""
Flask API for GrowPodEmpire
RESTful API endpoints for the cultivation platform
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from ..app import GrowPodEmpire
from ..models import EnvironmentalCondition, GrowthStage


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    CORS(app)
    
    # Initialize GrowPodEmpire
    empire = GrowPodEmpire()
    
    @app.route('/')
    def index():
        """API root endpoint"""
        return jsonify({
            "name": "GrowPodEmpire API",
            "version": "1.0.0",
            "description": "Professional Cannabis Cultivation Management Platform",
            "endpoints": {
                "pods": "/api/pods",
                "plants": "/api/plants",
                "environment": "/api/environment",
                "blockchain": "/api/blockchain",
                "stats": "/api/stats"
            }
        })
    
    # Pod Endpoints
    @app.route('/api/pods', methods=['GET', 'POST'])
    def pods():
        if request.method == 'POST':
            data = request.json
            pod = empire.create_pod(
                pod_id=data['id'],
                name=data['name'],
                capacity=data['capacity']
            )
            return jsonify(pod.model_dump()), 201
        else:
            pods_list = empire.list_pods()
            return jsonify([p.model_dump() for p in pods_list])
    
    @app.route('/api/pods/<pod_id>', methods=['GET'])
    def get_pod(pod_id):
        pod = empire.get_pod(pod_id)
        if pod:
            return jsonify(pod.model_dump())
        return jsonify({"error": "Pod not found"}), 404
    
    # Plant Endpoints
    @app.route('/api/plants', methods=['GET', 'POST'])
    def plants():
        if request.method == 'POST':
            data = request.json
            try:
                plant = empire.add_plant(
                    plant_id=data['id'],
                    strain=data['strain'],
                    pod_id=data['pod_id']
                )
                return jsonify(plant.model_dump()), 201
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
        else:
            pod_id = request.args.get('pod_id')
            plants_list = empire.list_plants(pod_id=pod_id)
            return jsonify([p.model_dump() for p in plants_list])
    
    @app.route('/api/plants/<plant_id>', methods=['GET'])
    def get_plant(plant_id):
        plant = empire.get_plant(plant_id)
        if plant:
            return jsonify(plant.model_dump())
        return jsonify({"error": "Plant not found"}), 404
    
    @app.route('/api/plants/<plant_id>/stage', methods=['PUT'])
    def update_plant_stage(plant_id):
        data = request.json
        try:
            stage = GrowthStage(data['stage'])
            plant = empire.update_plant_stage(plant_id, stage)
            return jsonify(plant.model_dump())
        except (ValueError, KeyError) as e:
            return jsonify({"error": str(e)}), 400
    
    # Growth Tracking Endpoints
    @app.route('/api/plants/<plant_id>/growth', methods=['POST'])
    def record_growth(plant_id):
        data = request.json
        try:
            metrics = empire.record_growth(
                plant_id=plant_id,
                height=data['height'],
                leaf_count=data.get('leaf_count')
            )
            return jsonify(metrics), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    
    @app.route('/api/plants/<plant_id>/analytics', methods=['GET'])
    def get_growth_analytics(plant_id):
        analytics = empire.get_growth_analytics(plant_id)
        return jsonify(analytics)
    
    # Environmental Monitoring Endpoints
    @app.route('/api/environment/<pod_id>', methods=['POST'])
    def record_environment(pod_id):
        data = request.json
        try:
            conditions = EnvironmentalCondition(**data)
            result = empire.record_environment(pod_id, conditions)
            return jsonify(result), 201
        except (ValueError, TypeError) as e:
            return jsonify({"error": str(e)}), 400
    
    @app.route('/api/environment/<pod_id>/analytics', methods=['GET'])
    def get_environment_analytics(pod_id):
        hours = int(request.args.get('hours', 24))
        analytics = empire.get_environment_analytics(pod_id, hours)
        return jsonify(analytics)
    
    # Harvest Endpoints
    @app.route('/api/plants/<plant_id>/harvest', methods=['POST'])
    def record_harvest(plant_id):
        data = request.json
        try:
            result = empire.record_harvest(
                plant_id=plant_id,
                yield_amount=data['yield_amount'],
                quality_score=data['quality_score']
            )
            return jsonify(result), 201
        except (ValueError, KeyError) as e:
            return jsonify({"error": str(e)}), 400
    
    # Blockchain Endpoints
    @app.route('/api/blockchain/info', methods=['GET'])
    def blockchain_info():
        info = empire.get_blockchain_info()
        return jsonify(info)
    
    @app.route('/api/blockchain/plant/<plant_id>', methods=['GET'])
    def plant_blockchain_history(plant_id):
        history = empire.get_plant_history(plant_id)
        return jsonify(history)
    
    @app.route('/api/blockchain/verify', methods=['GET'])
    def verify_blockchain():
        is_valid = empire.verify_data_integrity()
        return jsonify({"valid": is_valid})
    
    # System Stats
    @app.route('/api/stats', methods=['GET'])
    def system_stats():
        stats = empire.get_system_stats()
        return jsonify(stats)
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
