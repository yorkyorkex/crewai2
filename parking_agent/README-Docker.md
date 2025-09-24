# 🐳 Melbourne Parking Agent - Docker Version

Docker containerized version of the Melbourne Parking Agent with full English UI.

## 🚀 Quick Start

### Method 1: Using Docker Compose (Recommended)

```bash
# Build and start the container
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

### Method 2: Using Docker Commands

```bash
# Build the image
docker build -t melbourne-parking-agent:latest .

# Run the container
docker run -d -p 8000:8000 --name parking-agent melbourne-parking-agent:latest

# Check status
docker ps

# View logs
docker logs -f parking-agent

# Stop and remove
docker stop parking-agent && docker rm parking-agent
```

## 🌐 Access the Application

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Popular Locations**: http://localhost:8000/locations

## ✨ Features

- **Full English Interface** - No Chinese text
- **10 Popular Locations** - Melbourne CBD, Federation Square, etc.
- **GPS Auto-Location** - Click button to get current location
- **Modern UI Design** - Responsive with animations
- **Real-time Data** - Live parking sensor data from Melbourne
- **Health Monitoring** - Built-in health checks
- **Auto-restart** - Container restarts if it fails

## 🔧 Configuration

### Environment Variables

You can customize the container with environment variables:

```bash
docker run -d \
  -p 8000:8000 \
  -e PYTHONPATH=/app \
  -e PYTHONUNBUFFERED=1 \
  --name parking-agent \
  melbourne-parking-agent:latest
```

### Custom Port

To run on a different port (e.g., 8080):

```bash
# Docker command
docker run -d -p 8080:8000 --name parking-agent melbourne-parking-agent:latest

# Or modify docker-compose.yml
ports:
  - "8080:8000"
```

## 📊 Monitoring

### Health Check

The container includes automated health checks:

```bash
# Check health status
curl http://localhost:8000/health

# Expected response
{
  "status": "healthy",
  "mode": "english_user_friendly", 
  "locations": 10,
  "version": "2.0.0"
}
```

### Container Logs

```bash
# Follow logs
docker-compose logs -f parking-agent

# Or with docker command
docker logs -f parking-agent
```

## 🛠️ Development

### Local Development with Docker

```bash
# Build development version
docker build -t melbourne-parking-agent:dev .

# Run with volume mount for development
docker run -d \
  -p 8000:8000 \
  -v $(pwd):/app \
  --name parking-agent-dev \
  melbourne-parking-agent:dev
```

### Rebuild After Changes

```bash
# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

## 📝 API Usage Examples

### Find Parking Spots

```bash
# Using coordinates
curl -X POST "http://localhost:8000/parking" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": -37.8136,
    "longitude": 144.9631,
    "radius": 500,
    "location_name": "Melbourne CBD"
  }'

# Get popular locations
curl http://localhost:8000/locations
```

## 🔍 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs parking-agent

# Check if port is in use
netstat -tulpn | grep :8000

# Restart container
docker-compose restart parking-agent
```

### API Not Responding

```bash
# Check health endpoint
curl http://localhost:8000/health

# Check container status
docker-compose ps

# Restart if needed
docker-compose restart parking-agent
```

### Port Already in Use

```bash
# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use port 8001 instead

# Or stop conflicting service
docker ps | grep :8000
docker stop <container-id>
```

## 📦 Image Details

- **Base Image**: python:3.11-slim
- **Size**: ~1.8GB
- **Architecture**: x86_64
- **Health Check**: Every 30s
- **Restart Policy**: unless-stopped

## 🏷️ Version Information

- **Version**: 2.0.0
- **Features**: English UI, GPS, Popular Locations
- **API**: FastAPI with real-time Melbourne data
- **UI**: Modern responsive design with animations

