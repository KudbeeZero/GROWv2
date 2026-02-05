# API Documentation

## GrowPodEmpire REST API v1.0

Base URL: `http://localhost:5000`

### Authentication
Currently, no authentication is required. Future versions will implement JWT-based authentication.

---

## Endpoints

### Root

#### GET /
Get API information

**Response:**
```json
{
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
}
```

---

## Pods

### GET /api/pods
List all pods

**Response:**
```json
[
  {
    "id": "pod-001",
    "name": "Vegetative Chamber A",
    "capacity": 10,
    "current_plants": ["plant-001", "plant-002"],
    "active": true,
    "current_conditions": null
  }
]
```

### POST /api/pods
Create a new pod

**Request Body:**
```json
{
  "id": "pod-001",
  "name": "Vegetative Chamber A",
  "capacity": 10
}
```

**Response:** `201 Created`
```json
{
  "id": "pod-001",
  "name": "Vegetative Chamber A",
  "capacity": 10,
  "current_plants": [],
  "active": true,
  "current_conditions": null
}
```

### GET /api/pods/{pod_id}
Get pod details

**Response:**
```json
{
  "id": "pod-001",
  "name": "Vegetative Chamber A",
  "capacity": 10,
  "current_plants": ["plant-001"],
  "active": true,
  "current_conditions": {
    "temperature": 24.5,
    "humidity": 55.0,
    "co2_level": 1200,
    "light_intensity": 600,
    "ph_level": 6.5,
    "timestamp": "2026-02-05T01:57:00"
  }
}
```

---

## Plants

### GET /api/plants
List all plants

**Query Parameters:**
- `pod_id` (optional): Filter by pod ID

**Response:**
```json
[
  {
    "id": "plant-001",
    "strain": "OG Kush",
    "growth_stage": "vegetative",
    "planted_date": "2026-02-01T10:00:00",
    "pod_id": "pod-001",
    "height": 25.5,
    "health_score": 95.0,
    "notes": null,
    "metadata": {}
  }
]
```

### POST /api/plants
Add a new plant

**Request Body:**
```json
{
  "id": "plant-001",
  "strain": "OG Kush",
  "pod_id": "pod-001"
}
```

**Response:** `201 Created`

### GET /api/plants/{plant_id}
Get plant details

### PUT /api/plants/{plant_id}/stage
Update plant growth stage

**Request Body:**
```json
{
  "stage": "vegetative"
}
```

**Valid stages:** `seed`, `germination`, `seedling`, `vegetative`, `flowering`, `harvest`

---

## Growth Tracking

### POST /api/plants/{plant_id}/growth
Record growth measurement

**Request Body:**
```json
{
  "height": 25.5,
  "leaf_count": 8
}
```

**Response:** `201 Created`
```json
{
  "plant_id": "plant-001",
  "timestamp": "2026-02-05T01:57:00",
  "height": 25.5,
  "leaf_count": 8,
  "health_score": 95.0,
  "growth_rate": 2.5,
  "predicted_harvest_date": "2026-04-15T01:57:00"
}
```

### GET /api/plants/{plant_id}/analytics
Get growth analytics

**Response:**
```json
{
  "total_measurements": 10,
  "current_height": 32.5,
  "height_gained": 22.5,
  "average_growth_rate": 2.25,
  "current_health_score": 95.0,
  "predicted_harvest": "2026-04-15T01:57:00"
}
```

---

## Environmental Monitoring

### POST /api/environment/{pod_id}
Record environmental conditions

**Request Body:**
```json
{
  "temperature": 24.5,
  "humidity": 55.0,
  "co2_level": 1200,
  "light_intensity": 600,
  "ph_level": 6.5
}
```

**Response:** `201 Created`
```json
{
  "recorded": true,
  "timestamp": "2026-02-05T01:57:00",
  "analysis": {
    "temperature": {
      "value": 24.5,
      "status": "optimal",
      "optimal_range": "20-28"
    },
    "humidity": {
      "value": 55.0,
      "status": "optimal",
      "optimal_range": "40-60"
    }
  },
  "alerts": []
}
```

### GET /api/environment/{pod_id}/analytics
Get environmental analytics

**Query Parameters:**
- `hours` (optional, default: 24): Time period in hours

**Response:**
```json
{
  "period_hours": 24,
  "measurements": 48,
  "temperature": {
    "average": 24.2,
    "min": 22.5,
    "max": 26.0,
    "std_dev": 0.8
  },
  "humidity": {
    "average": 54.5,
    "min": 50.0,
    "max": 60.0,
    "std_dev": 2.3
  },
  "co2": {
    "average": 1250,
    "min": 1100,
    "max": 1400
  },
  "overall_status": "optimal"
}
```

---

## Harvest

### POST /api/plants/{plant_id}/harvest
Record harvest

**Request Body:**
```json
{
  "yield_amount": 150.5,
  "quality_score": 9.2
}
```

**Response:** `201 Created`
```json
{
  "plant_id": "plant-001",
  "strain": "OG Kush",
  "harvest_date": "2026-04-15T10:00:00",
  "yield_amount": 150.5,
  "quality_score": 9.2,
  "days_to_harvest": 74,
  "blockchain_record": {
    "record_id": "plant-001",
    "record_type": "harvest",
    "data_hash": "abc123...",
    "previous_hash": "def456...",
    "timestamp": "2026-04-15T10:00:00",
    "block_number": 42
  }
}
```

---

## Blockchain

### GET /api/blockchain/info
Get blockchain information

**Response:**
```json
{
  "total_blocks": 42,
  "is_valid": true,
  "latest_block": {
    "number": 41,
    "hash": "abc123...",
    "timestamp": "2026-02-05T01:57:00"
  }
}
```

### GET /api/blockchain/plant/{plant_id}
Get plant blockchain history

**Response:**
```json
[
  {
    "block_number": 5,
    "timestamp": "2026-02-01T10:00:00",
    "hash": "abc123...",
    "data": {
      "type": "plant_data",
      "id": "plant-001",
      "data": {
        "action": "planted",
        "strain": "OG Kush",
        "pod_id": "pod-001"
      }
    }
  }
]
```

### GET /api/blockchain/verify
Verify blockchain integrity

**Response:**
```json
{
  "valid": true
}
```

---

## System Statistics

### GET /api/stats
Get system statistics

**Response:**
```json
{
  "total_pods": 2,
  "active_pods": 2,
  "total_plants": 5,
  "active_plants": 4,
  "plants_by_stage": {
    "seedling": 1,
    "vegetative": 2,
    "flowering": 1,
    "harvest": 1
  },
  "blockchain": {
    "total_blocks": 42,
    "is_valid": true
  },
  "data_integrity": true
}
```

---

## Error Responses

All endpoints may return error responses:

### 400 Bad Request
```json
{
  "error": "Pod pod-001 not found"
}
```

### 404 Not Found
```json
{
  "error": "Plant not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```
