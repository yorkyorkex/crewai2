#!/usr/bin/env python
"""
Melbourne Parking Agent - Main API
User-friendly parking spot finder with popular locations and GPS features
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
from .tools.parking_tool import MelbourneParkingTool

app = FastAPI(
    title="Melbourne Parking Agent",
    description="Find available parking spots in Melbourne using real-time sensor data",
    version="2.0.0"
)

# Popular Melbourne locations with coordinates
POPULAR_LOCATIONS = {
    "melbourne_cbd": {
        "name": "Melbourne CBD",
        "latitude": -37.8136,
        "longitude": 144.9631
    },
    "federation_square": {
        "name": "Federation Square",
        "latitude": -37.8179,
        "longitude": 144.9690
    },
    "queen_victoria_market": {
        "name": "Queen Victoria Market",
        "latitude": -37.8076,
        "longitude": 144.9568
    },
    "flinders_street": {
        "name": "Flinders Street Station",
        "latitude": -37.8183,
        "longitude": 144.9671
    },
    "melbourne_central": {
        "name": "Melbourne Central",
        "latitude": -37.8103,
        "longitude": 144.9633
    },
    "southbank": {
        "name": "Southbank",
        "latitude": -37.8226,
        "longitude": 144.9648
    },
    "docklands": {
        "name": "Docklands",
        "latitude": -37.8161,
        "longitude": 144.9472
    },
    "chapel_street": {
        "name": "Chapel Street",
        "latitude": -37.8467,
        "longitude": 144.9906
    },
    "st_kilda": {
        "name": "St Kilda",
        "latitude": -37.8675,
        "longitude": 144.9733
    },
    "richmond": {
        "name": "Richmond",
        "latitude": -37.8197,
        "longitude": 145.0040
    }
}

class ParkingRequest(BaseModel):
    latitude: float
    longitude: float
    radius: int = 500
    location_name: str = ""

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
    search_location: str = ""

@app.get("/", response_class=HTMLResponse)
async def home():
    # Generate options for the dropdown
    location_options = ""
    for key, loc in POPULAR_LOCATIONS.items():
        location_options += f'<option value="{key}">{loc["name"]}</option>\n'

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Melbourne Parking Finder</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E🚗%3C/text%3E%3C/svg%3E">
        <style>
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}

            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}

            .container {{
                max-width: 1000px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }}

            .header {{
                background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
                color: white;
                text-align: center;
                padding: 40px 30px;
            }}

            .header h1 {{
                font-size: 2.5rem;
                margin-bottom: 10px;
                font-weight: 700;
            }}

            .header p {{
                font-size: 1.1rem;
                opacity: 0.9;
            }}

            .content {{
                padding: 40px 30px;
            }}

            .info-banner {{
                background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
                color: white;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 30px;
                text-align: center;
                font-weight: 500;
            }}

            .search-section {{
                background: #f8fafc;
                padding: 30px;
                border-radius: 16px;
                margin-bottom: 30px;
                border: 2px solid #e2e8f0;
            }}

            .form-group {{
                margin-bottom: 25px;
            }}

            .form-row {{
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 20px;
                align-items: end;
            }}

            label {{
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #2d3748;
                font-size: 0.95rem;
            }}

            input, select {{
                width: 100%;
                padding: 14px 16px;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                font-size: 16px;
                transition: all 0.3s ease;
                background: white;
            }}

            input:focus, select:focus {{
                border-color: #3498db;
                outline: none;
                box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
                transform: translateY(-2px);
            }}

            .btn-group {{
                display: grid;
                grid-template-columns: 2fr 1fr;
                gap: 15px;
                margin-top: 25px;
            }}

            .btn-primary {{
                background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
                color: white;
                border: none;
                padding: 16px 24px;
                border-radius: 12px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}

            .btn-primary:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(52, 152, 219, 0.3);
            }}

            .btn-secondary {{
                background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
                color: white;
                border: none;
                padding: 16px 24px;
                border-radius: 12px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }}

            .btn-secondary:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 16px rgba(127, 140, 141, 0.3);
            }}

            .loading {{
                display: none;
                text-align: center;
                padding: 40px;
                color: #3498db;
                font-size: 1.2rem;
                font-weight: 500;
            }}

            .spinner {{
                border: 3px solid #f3f3f3;
                border-top: 3px solid #3498db;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 15px;
            }}

            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}

            .result {{
                display: none;
                background: #f8fafc;
                padding: 30px;
                border-radius: 16px;
                border-left: 6px solid #3498db;
            }}

            .result h3 {{
                color: #2d3748;
                margin-bottom: 15px;
                font-size: 1.4rem;
            }}

            .result p {{
                color: #4a5568;
                margin-bottom: 20px;
                font-weight: 500;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            }}

            th {{
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                padding: 18px 15px;
                text-align: left;
                font-weight: 600;
                font-size: 0.95rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}

            td {{
                padding: 16px 15px;
                border-bottom: 1px solid #e2e8f0;
                color: #4a5568;
                font-weight: 500;
            }}

            tr:hover {{
                background-color: #f7fafc;
            }}

            tr:last-child td {{
                border-bottom: none;
            }}

            .maps-link {{
                display: inline-flex;
                align-items: center;
                padding: 8px 12px;
                background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-size: 0.9rem;
                font-weight: 600;
                transition: all 0.3s ease;
            }}

            .maps-link:hover {{
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(231, 76, 60, 0.3);
            }}

            .distance-badge {{
                display: inline-block;
                background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
                color: white;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 0.85rem;
                font-weight: 600;
            }}

            .status-badge {{
                display: inline-block;
                background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
                color: white;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 0.85rem;
                font-weight: 600;
            }}

            @media (max-width: 768px) {{
                body {{
                    padding: 10px;
                }}

                .header {{
                    padding: 30px 20px;
                }}

                .header h1 {{
                    font-size: 2rem;
                }}

                .content {{
                    padding: 30px 20px;
                }}

                .search-section {{
                    padding: 25px 20px;
                }}

                .form-row {{
                    grid-template-columns: 1fr;
                }}

                .btn-group {{
                    grid-template-columns: 1fr;
                }}

                table {{
                    font-size: 0.9rem;
                }}

                th, td {{
                    padding: 12px 10px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚗 Melbourne Parking Finder</h1>
                <p>Find available parking spots using real-time sensor data</p>
            </div>

            <div class="content">
                <div class="info-banner">
                    🎉 Now with popular locations and GPS! No need to enter coordinates manually.
                </div>

                <div class="search-section">
                    <form id="parkingForm">
                        <div class="form-group">
                            <label for="location">🎯 Choose Popular Location:</label>
                            <select id="location">
                                <option value="">-- Select a location or enter coordinates manually --</option>
                                {location_options}
                            </select>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label for="latitude">📍 Latitude:</label>
                                <input type="number" id="latitude" step="any" value="" placeholder="e.g., -37.8136">
                            </div>
                            <div class="form-group">
                                <label for="longitude">📍 Longitude:</label>
                                <input type="number" id="longitude" step="any" value="" placeholder="e.g., 144.9631">
                            </div>
                            <div class="form-group">
                                <label for="radius">📏 Search Radius (meters):</label>
                                <input type="number" id="radius" value="500" placeholder="500" min="100" max="2000">
                            </div>
                        </div>

                        <div class="btn-group">
                            <button type="submit" class="btn-primary">🔍 Find Parking Spots</button>
                            <button type="button" class="btn-secondary" onclick="getCurrentLocation()">📱 Use GPS</button>
                        </div>
                    </form>
                </div>

                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    Searching for available parking spots...
                </div>

                <div id="result" class="result"></div>
            </div>
        </div>

        <script>
            const locations = {json.dumps(POPULAR_LOCATIONS)};

            // Handle location dropdown change
            document.getElementById('location').addEventListener('change', function(e) {{
                const selectedLocation = e.target.value;
                if (selectedLocation && locations[selectedLocation]) {{
                    document.getElementById('latitude').value = locations[selectedLocation].latitude;
                    document.getElementById('longitude').value = locations[selectedLocation].longitude;
                }}
            }});

            // Get user's current location
            function getCurrentLocation() {{
                if (navigator.geolocation) {{
                    document.getElementById('loading').style.display = 'block';
                    document.getElementById('result').style.display = 'none';

                    navigator.geolocation.getCurrentPosition(
                        function(position) {{
                            document.getElementById('latitude').value = position.coords.latitude;
                            document.getElementById('longitude').value = position.coords.longitude;
                            document.getElementById('loading').style.display = 'none';

                            // Show success notification
                            const notification = document.createElement('div');
                            notification.style.cssText = 'position:fixed;top:20px;right:20px;background:#00b894;color:white;padding:15px 20px;border-radius:8px;font-weight:600;z-index:1000;';
                            notification.textContent = '✅ Location obtained successfully!';
                            document.body.appendChild(notification);
                            setTimeout(() => notification.remove(), 3000);
                        }},
                        function(error) {{
                            document.getElementById('loading').style.display = 'none';

                            let errorMsg = 'Location access denied or unavailable';
                            switch(error.code) {{
                                case error.PERMISSION_DENIED:
                                    errorMsg = 'Location access denied by user';
                                    break;
                                case error.POSITION_UNAVAILABLE:
                                    errorMsg = 'Location information unavailable';
                                    break;
                                case error.TIMEOUT:
                                    errorMsg = 'Location request timed out';
                                    break;
                            }}

                            // Show error notification
                            const notification = document.createElement('div');
                            notification.style.cssText = 'position:fixed;top:20px;right:20px;background:#e74c3c;color:white;padding:15px 20px;border-radius:8px;font-weight:600;z-index:1000;';
                            notification.textContent = '❌ ' + errorMsg;
                            document.body.appendChild(notification);
                            setTimeout(() => notification.remove(), 5000);
                        }},
                        {{
                            enableHighAccuracy: true,
                            timeout: 10000,
                            maximumAge: 300000
                        }}
                    );
                }} else {{
                    // Show error notification
                    const notification = document.createElement('div');
                    notification.style.cssText = 'position:fixed;top:20px;right:20px;background:#e74c3c;color:white;padding:15px 20px;border-radius:8px;font-weight:600;z-index:1000;';
                    notification.textContent = '❌ Geolocation not supported by browser';
                    document.body.appendChild(notification);
                    setTimeout(() => notification.remove(), 5000);
                }}
            }}

            // Handle form submission
            document.getElementById('parkingForm').addEventListener('submit', async function(e) {{
                e.preventDefault();

                const latitude = parseFloat(document.getElementById('latitude').value);
                const longitude = parseFloat(document.getElementById('longitude').value);
                const radius = parseInt(document.getElementById('radius').value);
                const locationSelect = document.getElementById('location');
                const locationName = locationSelect.options[locationSelect.selectedIndex].text;

                if (!latitude || !longitude) {{
                    // Show error notification
                    const notification = document.createElement('div');
                    notification.style.cssText = 'position:fixed;top:20px;right:20px;background:#e74c3c;color:white;padding:15px 20px;border-radius:8px;font-weight:600;z-index:1000;';
                    notification.textContent = '❌ Please select a location or enter valid coordinates';
                    document.body.appendChild(notification);
                    setTimeout(() => notification.remove(), 5000);
                    return;
                }}

                document.getElementById('loading').style.display = 'block';
                document.getElementById('result').style.display = 'none';

                try {{
                    const response = await fetch('/parking', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{
                            latitude: latitude,
                            longitude: longitude,
                            radius: radius,
                            location_name: locationName.includes('--') ? '' : locationName
                        }})
                    }});

                    const data = await response.json();

                    if (data.status === 'success') {{
                        // Enhanced table with styling
                        const styledTable = data.html_table.replace(
                            /<td>([^<]+m)<\/td>/g,
                            '<td><span class="distance-badge">$1</span></td>'
                        ).replace(
                            /<td>(Unoccupied)<\/td>/g,
                            '<td><span class="status-badge">$1</span></td>'
                        ).replace(
                            /<a href="([^"]+)" target="_blank">🗺️ Maps<\/a>/g,
                            '<a href="$1" target="_blank" class="maps-link">🗺️ View on Maps</a>'
                        );

                        document.getElementById('result').innerHTML =
                            `<h3>✅ Found ${{data.found_spots}} available parking spots!</h3>` +
                            `<p><strong>Search Location:</strong> ${{data.search_location}}</p>` +
                            styledTable;
                    }} else {{
                        document.getElementById('result').innerHTML =
                            `<h3>❌ ${{data.message}}</h3>`;
                    }}
                }} catch (error) {{
                    document.getElementById('result').innerHTML =
                        `<h3>❌ Error: ${{error.message}}</h3>`;
                }}

                document.getElementById('loading').style.display = 'none';
                document.getElementById('result').style.display = 'block';

                // Scroll to results
                document.getElementById('result').scrollIntoView({{ behavior: 'smooth' }});
            }});
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
        if not (50 <= request.radius <= 5000):
            raise HTTPException(status_code=400, detail="Search radius must be between 50 and 5000 meters")

        # Determine location name for display
        search_location = request.location_name if request.location_name else f"Coordinates ({request.latitude:.4f}, {request.longitude:.4f})"

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
                message="No available spots within the search radius. Try expanding your search area.",
                search_location=search_location
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
            message=f"Successfully found {len(formatted_spots)} parking spots",
            search_location=search_location
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mode": "english_user_friendly",
        "locations": len(POPULAR_LOCATIONS),
        "version": "2.0.0"
    }

@app.get("/locations")
async def get_locations():
    """Get all popular locations"""
    return {"locations": POPULAR_LOCATIONS}

if __name__ == "__main__":
    import uvicorn
    print("Starting Melbourne Parking Agent - Main API...")
    print("Web Interface: http://localhost:8000")
    print("Features: Popular locations, GPS, modern UI")
    uvicorn.run(app, host="0.0.0.0", port=8000)