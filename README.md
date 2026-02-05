# GrowPodEmpire v1.0

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A professional cannabis cultivation management platform with intelligent growth tracking, environmental monitoring, and blockchain data integrity.

## 🌿 Features

### Intelligent Growth Tracking
- **Real-time Growth Monitoring**: Track plant height, leaf count, and health metrics
- **Growth Rate Analysis**: Automatic calculation of growth rates and trends
- **Predictive Analytics**: AI-powered harvest date predictions based on growth patterns
- **Health Scoring**: Continuous health assessment based on growth performance
- **Stage Management**: Track plants through complete lifecycle (seed → harvest)

### Environmental Monitoring
- **Comprehensive Sensors**: Temperature, humidity, CO2, light intensity, pH monitoring
- **Optimal Range Detection**: Automatic analysis against ideal growing conditions
- **Alert System**: Real-time alerts for critical environmental conditions
- **Historical Analytics**: Trend analysis and statistical reporting
- **Multi-Pod Support**: Monitor multiple growing chambers independently

### Blockchain Integration
- **Immutable Records**: All cultivation data recorded on blockchain
- **Data Integrity**: Cryptographic verification of all transactions
- **Complete Audit Trail**: Full historical record for compliance and quality assurance
- **Harvest Verification**: Secure recording of harvest yields and quality scores
- **Chain Validation**: Built-in blockchain integrity verification

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/KudbeeZero/GROWv2.git
cd GROWv2

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Run Demo

```bash
python demo.py
```

This will demonstrate all key features including:
- Creating growing pods
- Adding and tracking plants
- Recording growth measurements
- Environmental monitoring
- Blockchain verification
- Harvest recording

### Run API Server

```bash
# Start the Flask API server
python -m growpodempire.api.flask_api
```

The API will be available at `http://localhost:5000`

### Run Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=growpodempire --cov-report=html
```

## 📖 Usage

### Basic Example

```python
from growpodempire.app import GrowPodEmpire
from growpodempire.models import EnvironmentalCondition, GrowthStage

# Initialize platform
empire = GrowPodEmpire()

# Create a growing pod
pod = empire.create_pod("pod-001", "Vegetative Chamber", capacity=10)

# Add a plant
plant = empire.add_plant("plant-001", "OG Kush", "pod-001")

# Update growth stage
empire.update_plant_stage("plant-001", GrowthStage.VEGETATIVE)

# Record growth measurement
metrics = empire.record_growth("plant-001", height=25.5, leaf_count=8)
print(f"Health Score: {metrics['health_score']}")
print(f"Predicted Harvest: {metrics['predicted_harvest_date']}")

# Record environmental conditions
conditions = EnvironmentalCondition(
    temperature=24.5,
    humidity=55.0,
    co2_level=1200,
    light_intensity=600,
    ph_level=6.5
)
result = empire.record_environment("pod-001", conditions)

# Get analytics
growth_analytics = empire.get_growth_analytics("plant-001")
env_analytics = empire.get_environment_analytics("pod-001")

# Verify blockchain integrity
is_valid = empire.verify_data_integrity()
print(f"Blockchain Valid: {is_valid}")
```

## 🔌 API Endpoints

### Pods
- `GET /api/pods` - List all pods
- `POST /api/pods` - Create a new pod
- `GET /api/pods/<pod_id>` - Get pod details

### Plants
- `GET /api/plants` - List all plants
- `POST /api/plants` - Add a new plant
- `GET /api/plants/<plant_id>` - Get plant details
- `PUT /api/plants/<plant_id>/stage` - Update growth stage

### Growth Tracking
- `POST /api/plants/<plant_id>/growth` - Record growth measurement
- `GET /api/plants/<plant_id>/analytics` - Get growth analytics

### Environmental Monitoring
- `POST /api/environment/<pod_id>` - Record environmental conditions
- `GET /api/environment/<pod_id>/analytics` - Get environmental analytics

### Harvest
- `POST /api/plants/<plant_id>/harvest` - Record harvest

### Blockchain
- `GET /api/blockchain/info` - Get blockchain information
- `GET /api/blockchain/plant/<plant_id>` - Get plant blockchain history
- `GET /api/blockchain/verify` - Verify blockchain integrity

### System
- `GET /api/stats` - Get system statistics

## 🏗️ Architecture

```
GrowPodEmpire/
├── src/growpodempire/
│   ├── models/           # Data models (Plant, Pod, Environment, etc.)
│   ├── services/         # Business logic (GrowthTracker, EnvironmentalMonitor)
│   ├── blockchain/       # Blockchain implementation (CultivationBlockchain)
│   ├── api/              # REST API (Flask)
│   └── app.py            # Main application manager
├── tests/                # Test suite
├── demo.py               # Demo script
└── requirements.txt      # Dependencies
```

## 🔬 Growth Tracking Algorithm

The intelligent growth tracking system uses:
- **Growth Rate Analysis**: Calculates cm/day based on historical measurements
- **Stage-Based Predictions**: Different growth rates for each lifecycle stage
- **Health Scoring**: Dynamic health assessment based on growth performance
- **Harvest Prediction**: Combines stage duration with actual growth patterns

## 🌡️ Environmental Monitoring

Optimal ranges for cannabis cultivation:
- **Temperature**: 20-28°C
- **Humidity**: 40-60%
- **CO2 Level**: 800-1500 ppm
- **Light Intensity**: 400-700 lumens
- **pH Level**: 6.0-7.0

## 🔐 Blockchain Security

Each block contains:
- Timestamp
- Data payload (plant/environmental/harvest data)
- SHA-256 hash
- Previous block hash
- Block number

The blockchain provides:
- Immutable record keeping
- Complete audit trail
- Data integrity verification
- Tamper detection

## 🧪 Testing

The platform includes comprehensive tests:
- Unit tests for all core components
- Integration tests for system workflows
- Blockchain verification tests
- API endpoint tests

Test coverage: Comprehensive coverage of all major features

## 📊 Data Models

### Plant
- ID, strain, growth stage
- Height, health score
- Pod assignment
- Metadata

### GrowPod
- ID, name, capacity
- Current plants
- Environmental conditions
- Active status

### EnvironmentalCondition
- Temperature, humidity, CO2
- Light intensity, pH level
- Timestamp

### GrowthMetrics
- Height, leaf count
- Health score, growth rate
- Predicted harvest date

### BlockchainRecord
- Record type and ID
- Data hash, previous hash
- Timestamp, block number

## 🔮 Future Enhancements

- Machine learning for advanced growth predictions
- IoT sensor integration
- Mobile app
- Multi-user support with role-based access
- Automated nutrient scheduling
- Image-based health analysis
- Integration with smart grow lights and HVAC
- Advanced reporting and analytics dashboard

## 📝 License

MIT License - see LICENSE file for details

## 👥 Contributors

GrowPodEmpire Team

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions and support, please open an issue on GitHub.

---

**GrowPodEmpire v1.0** - Professional Cannabis Cultivation Management Platform