# Melbourne Parking Agent

A real-time parking spot finder using CrewAI and Melbourne's open data API. Find available parking spots near your location with distance calculation and Google Maps integration.

## Features

- 🚗 Real-time parking data from Melbourne City Council
- 📍 Distance calculation from your location
- 🗺️ Google Maps integration for each parking spot
- 🌐 Web interface with interactive form
- 🐳 Docker containerization for cloud deployment
- ⚡ FastAPI backend with automatic documentation

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -e .
   ```

2. **Run CLI mode (test):**
   ```bash
   python -m parking_agent.main --latitude -37.8136 --longitude 144.9631 --radius 1000
   ```

3. **Run Web API:**
   ```bash
   python -m parking_agent.main api
   ```

   Then open: http://localhost:8000

### Docker Deployment

1. **Build image:**
   ```bash
   docker build -t melbourne-parking-agent .
   ```

2. **Run container:**
   ```bash
   docker run -p 8000:8000 melbourne-parking-agent
   ```

3. **Using docker-compose:**
   ```bash
   docker-compose up
   ```

## API Endpoints

### GET `/`
Interactive web interface for parking search

### POST `/parking`
```json
{
  "latitude": -37.8136,
  "longitude": 144.9631,
  "radius": 500
}
```

**Response:**
```json
{
  "status": "success",
  "found_spots": 5,
  "parking_data": [
    {
      "bay_id": "123",
      "status": "Unoccupied",
      "distance_meters": 150,
      "status_time": "2024-09-24 14:30:00 AEST",
      "updated_time": "2024-09-24 14:32:15 AEST",
      "google_maps_link": "https://www.google.com/maps/?q=-37.8136,144.9631"
    }
  ],
  "html_table": "<table>...</table>"
}
```

### GET `/health`
Health check endpoint for monitoring

## Cloud Deployment

### Railway
1. Connect your GitHub repository to Railway
2. Set environment variables if needed
3. Deploy automatically

### Google Cloud Platform
1. Build and push to Container Registry:
   ```bash
   docker build -t gcr.io/PROJECT-ID/parking-agent .
   docker push gcr.io/PROJECT-ID/parking-agent
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy --image gcr.io/PROJECT-ID/parking-agent --port 8000
   ```

## Architecture

The system uses CrewAI with two specialized agents:

- **Parking Finder Agent**: Fetches real-time data from Melbourne's API, calculates distances, and filters by radius
- **Parking Reporter Agent**: Formats data into user-friendly tables and responses

### Components

- `api.py`: FastAPI web server with interactive interface
- `crew.py`: CrewAI orchestration and agent definitions
- `tools/parking_tool.py`: Melbourne parking API client with distance calculation
- `config/agents.yaml`: Agent roles and capabilities
- `config/tasks.yaml`: Task definitions and workflows

## Data Source

Uses Melbourne City Council's open data:
- **Dataset**: on-street-parking-bay-sensors
- **API**: https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/on-street-parking-bay-sensors/records
- **Update Frequency**: Real-time sensor data

## Example Usage

```bash
# Find parking spots within 500m of Melbourne CBD
curl -X POST "http://localhost:8000/parking" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": -37.8136,
    "longitude": 144.9631,
    "radius": 500
  }'
```

## Development

The project follows CrewAI patterns:
- Agent configuration via YAML files
- Tool-based architecture
- Sequential processing for fast responses
- Minimal verbosity for performance
