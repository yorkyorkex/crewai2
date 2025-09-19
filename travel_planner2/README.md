# 🌍 Travel Planner API

An AI-powered travel planning service that combines **CrewAI**, **FastAPI**, **Serper**, and **Google Maps** to create comprehensive travel itineraries. The system uses multiple AI agents to research destinations, plan optimal routes, and generate detailed travel guides.

## ✨ Features

- **🤖 Multi-Agent AI System**: Three specialized agents working together
  - **Searcher Agent**: Finds attractions and activities using Serper API and Google Maps
  - **Planner Agent**: Creates optimized itineraries considering travel times and logistics
  - **Reporter Agent**: Generates beautiful Markdown travel guides

- **🚀 Dual Interface**:
  - **REST API**: FastAPI-based web service for integration
  - **CLI**: Command-line interface for direct usage

- **🐳 Docker Ready**: Containerized for easy deployment to any cloud platform

- **📊 Real-time Progress**: Track travel plan generation with task IDs

## 🛠️ Tech Stack

- **CrewAI**: Multi-agent AI framework
- **FastAPI**: High-performance web API framework
- **OpenAI GPT-4o Mini**: AI language model
- **Serper API**: Web search capabilities
- **Google Maps API**: Location data and routing
- **Docker**: Containerization for deployment

## 📋 Prerequisites

- Python 3.10-3.13
- API Keys (already configured in `.env`):
  - OpenAI API Key
  - Serper API Key
  - Google Maps API Key

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -e .
```

### 2. Run the API Server

```bash
# Method 1: Using the script
api

# Method 2: Using Python module
python -m travel_planner2.main api

# Method 3: Direct FastAPI
python -m uvicorn travel_planner2.api:app --host 0.0.0.0 --port 8000
```

### 3. Run CLI Mode

```bash
# Default example (Tokyo, 3 days)
travel_planner2

# Custom destination and duration
travel_planner2 --destination "Paris, France" --duration 5 --preferences "museums and cafes"
```

## 🌐 API Usage

### Start a Travel Plan

```bash
curl -X POST "http://localhost:8000/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Tokyo, Japan",
    "duration": 5,
    "preferences": "temples, sushi, technology"
  }'
```

Response:
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "processing",
  "message": "Travel plan creation started for Tokyo, Japan. Use the task_id to check progress."
}
```

### Check Progress

```bash
curl "http://localhost:8000/plan/123e4567-e89b-12d3-a456-426614174000"
```

Response:
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "result": "# 5-Day Tokyo Travel Guide\n\n## Day 1: Traditional Tokyo...",
  "created_at": "2024-01-15T10:30:00",
  "completed_at": "2024-01-15T10:35:00"
}
```

## 🐳 Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t travel-planner .

# Run with docker-compose
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Environment Variables

The app requires these environment variables (already set in `.env`):

```env
MODEL=gpt-4o-mini
OPENAI_API_KEY=your_openai_key
SERPER_API_KEY=your_serper_key
GOOGLE_MAPS_API_KEY=your_google_maps_key
```

## 📖 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API documentation homepage |
| GET | `/health` | Health check |
| POST | `/plan` | Create new travel plan |
| GET | `/plan/{task_id}` | Get plan status and result |
| DELETE | `/plan/{task_id}` | Delete a plan |
| GET | `/plans` | List all plans |
| GET | `/docs` | Swagger UI documentation |
| GET | `/redoc` | ReDoc documentation |

## 🏗️ Architecture

### Agent Workflow

```
🔍 Searcher Agent
├── Searches for attractions using Serper API
├── Finds restaurants and activities
└── Gathers location data with Google Maps

📅 Planner Agent
├── Creates day-by-day itineraries
├── Optimizes routes using Google Maps
└── Considers timing and logistics

📝 Reporter Agent
├── Generates comprehensive travel guides
├── Formats in beautiful Markdown
└── Includes practical travel information
```

### File Structure

```
travel_planner2/
├── src/travel_planner2/
│   ├── api.py              # FastAPI application
│   ├── crew.py             # CrewAI agents and tasks
│   ├── main.py             # CLI and API entry points
│   ├── tools/
│   │   ├── serper_tool.py  # Serper API integration
│   │   └── maps_tool.py    # Google Maps integration
│   └── config/
│       ├── agents.yaml     # Agent configurations
│       └── tasks.yaml      # Task definitions
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Docker Compose setup
└── pyproject.toml          # Project dependencies
```

## 🔧 Development

### CLI Commands

```bash
# Run crew directly
python -m travel_planner2.main

# Run with custom parameters
python -m travel_planner2.main --destination "London" --duration 3

# Start API server
python -m travel_planner2.main api

# Training mode
python -m travel_planner2.main train <iterations> <filename>
```

### Customization

- **Agents**: Modify `src/travel_planner2/config/agents.yaml`
- **Tasks**: Modify `src/travel_planner2/config/tasks.yaml`
- **Tools**: Add new tools in `src/travel_planner2/tools/`
- **API**: Extend `src/travel_planner2/api.py`

## 🚀 Cloud Deployment

### Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Deploy to Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly deploy
```

### Deploy to Google Cloud Run

```bash
# Build and push to registry
docker build -t gcr.io/PROJECT_ID/travel-planner .
docker push gcr.io/PROJECT_ID/travel-planner

# Deploy to Cloud Run
gcloud run deploy travel-planner \
  --image gcr.io/PROJECT_ID/travel-planner \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 📊 Sample Output

The system generates detailed travel guides like this:

```markdown
# 5-Day Tokyo Travel Guide

## Trip Overview
Experience the perfect blend of traditional and modern Japan...

## Day 1: Traditional Tokyo
### Morning (9:00 AM - 12:00 PM)
- **Senso-ji Temple** (2 hours)
  - Address: 2-3-1 Asakusa, Taito City, Tokyo
  - Best time: Early morning to avoid crowds

### Lunch (12:00 PM - 1:30 PM)
- **Daikokuya Tempura** (Traditional tempura since 1887)
  - Price range: ¥2,000-3,000
  - Speciality: Edo-style tempura

### Afternoon (2:00 PM - 6:00 PM)
- **Tokyo National Museum** (3 hours)
  - Travel time from lunch: 15 minutes by subway
  - Highlights: Samurai swords, Buddhist art
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- **Documentation**: Check the `/docs` endpoint when running the API
- **Issues**: Create issues for bug reports or feature requests
- **Discord**: Join the CrewAI community for support

---

Built with ❤️ using [CrewAI](https://crewai.com), [FastAPI](https://fastapi.tiangolo.com), and modern AI tools.