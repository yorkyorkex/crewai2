#!/usr/bin/env python
"""
Simple test API that bypasses CrewAI and directly uses the parking tool.
This is for testing the core functionality without needing OpenAI API key.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from parking_agent.tools.parking_tool import MelbourneParkingTool

app = FastAPI(
    title="Melbourne Parking Agent (Test Mode)",
    description="Direct parking spot finder using Melbourne's open data (bypasses CrewAI for testing)",
    version="1.0.0"
)

class ParkingRequest(BaseModel):
    latitude: float
    longitude: float
    radius: int = 500

class ParkingSpot(BaseModel):
    bay_id: str
    status: str
    distance_meters: int
    status_time: str
    updated_time: str
    google_maps_link: str

class ParkingResponse(BaseModel):
    status: str
    found_spots: int
    parking_data: list[ParkingSpot]
    html_table: str
    message: str = ""

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Melbourne Parking Finder (Test Mode)</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
            button { background-color: #007bff; color: white; padding: 12px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background-color: #0056b3; }
            .result { margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 4px; }
            .loading { display: none; color: #007bff; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .test-mode { background-color: #fff3cd; border: 1px solid #ffc107; padding: 10px; border-radius: 4px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="test-mode">
            <strong>Test Mode:</strong> This version bypasses CrewAI and directly uses the parking tool for testing purposes.
        </div>

        <h1>Melbourne Parking Finder</h1>
        <p>Find available parking spots near your location using real-time sensor data from the City of Melbourne.</p>

        <form id="parkingForm">
            <div class="form-group">
                <label for="latitude">Latitude:</label>
                <input type="number" id="latitude" step="any" value="-37.8136" placeholder="e.g., -37.8136">
            </div>
            <div class="form-group">
                <label for="longitude">Longitude:</label>
                <input type="number" id="longitude" step="any" value="144.9631" placeholder="e.g., 144.9631">
            </div>
            <div class="form-group">
                <label for="radius">Search Radius (meters):</label>
                <input type="number" id="radius" value="1000" placeholder="e.g., 500">
            </div>
            <button type="submit">Find Parking Spots</button>
        </form>

        <div class="loading" id="loading">Searching for available parking spots...</div>
        <div id="result" class="result" style="display: none;"></div>

        <script>
            document.getElementById('parkingForm').addEventListener('submit', async function(e) {
                e.preventDefault();

                const latitude = parseFloat(document.getElementById('latitude').value);
                const longitude = parseFloat(document.getElementById('longitude').value);
                const radius = parseInt(document.getElementById('radius').value);

                document.getElementById('loading').style.display = 'block';
                document.getElementById('result').style.display = 'none';

                try {
                    const response = await fetch('/parking', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            latitude: latitude,
                            longitude: longitude,
                            radius: radius
                        })
                    });

                    const data = await response.json();

                    if (data.status === 'success') {
                        document.getElementById('result').innerHTML =
                            `<h3>Found ${data.found_spots} available parking spots</h3>` +
                            data.html_table;
                    } else {
                        document.getElementById('result').innerHTML =
                            `<h3>Error: ${data.message}</h3>`;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML =
                        `<h3>Error: ${error.message}</h3>`;
                }

                document.getElementById('loading').style.display = 'none';
                document.getElementById('result').style.display = 'block';
            });
        </script>
    </body>
    </html>
    """

@app.post("/parking", response_model=ParkingResponse)
async def find_parking(request: ParkingRequest):
    try:
        # Input validation
        if not (-90 <= request.latitude <= 90):
            raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
        if not (-180 <= request.longitude <= 180):
            raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
        if not (1 <= request.radius <= 5000):
            raise HTTPException(status_code=400, detail="Radius must be between 1 and 5000 meters")

        # Use the parking tool directly
        tool = MelbourneParkingTool()
        result = tool._run(request.latitude, request.longitude, request.radius)

        # Parse the result
        result_data = json.loads(result)

        # Extract parking data and HTML table
        parking_spots = result_data.get('parking_spots', [])
        html_table = result_data.get('html_table', '')

        if not parking_spots:
            return ParkingResponse(
                status="no_results",
                found_spots=0,
                parking_data=[],
                html_table="",
                message="目前半徑內沒有空位，建議擴大搜尋範圍。"
            )

        # Format response
        formatted_spots = []
        for spot in parking_spots:
            formatted_spots.append(ParkingSpot(
                bay_id=spot['bay_id'],
                status=spot['status'],
                distance_meters=spot['distance_meters'],
                status_time=spot['status_time'],
                updated_time=spot['updated_time'],
                google_maps_link=spot['google_maps_link']
            ))

        return ParkingResponse(
            status="success",
            found_spots=len(formatted_spots),
            parking_data=formatted_spots,
            html_table=html_table,
            message=f"Found {len(formatted_spots)} parking spots"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "mode": "test"}

if __name__ == "__main__":
    import uvicorn
    print("Starting Melbourne Parking Agent TEST API server...")
    print("Web Interface: http://localhost:8001")
    print("This bypasses CrewAI for testing purposes.")
    uvicorn.run(app, host="0.0.0.0", port=8001)