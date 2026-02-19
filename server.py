from flask import Flask, request, jsonify
import os

from growpodempire.app import GrowPodEmpire
from growpodempire.models import GrowthStage, EnvironmentalCondition

app = Flask(__name__)
engine = GrowPodEmpire()

@app.get("/")
def health_check():
    return jsonify({"status": "GROWv2 API running"})

@app.post("/pods")
def create_pod():
    data = request.json
    pod = engine.create_pod(
        pod_id=data["id"],
        name=data["name"],
        capacity=data["capacity"]
    )
    return jsonify({"pod": pod.__dict__})

@app.get("/pods")
def list_pods():
    pods = engine.list_pods()
    return jsonify([p.__dict__ for p in pods])

@app.post("/plants")
def add_plant():
    data = request.json
    plant = engine.add_plant(
        plant_id=data["id"],
        strain=data["strain"],
        pod_id=data["pod_id"]
    )
    return jsonify({"plant": plant.__dict__})

@app.post("/growth")
def record_growth():
    data = request.json
    result = engine.record_growth(
        plant_id=data["plant_id"],
        height=data["height"],
        leaf_count=data.get("leaf_count")
    )
    return jsonify(result)

@app.get("/analytics/plant/<plant_id>")
def get_analytics(plant_id):
    stats = engine.get_growth_analytics(plant_id)
    return jsonify(stats)

# More endpoints can be added similarly

# Start server using Render’s dynamic PORT
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)