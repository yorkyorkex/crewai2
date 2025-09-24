#!/usr/bin/env python
"""
User-friendly Melbourne Parking Agent with popular locations and better UX
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
    title="Melbourne Parking Agent - 用戶友好版",
    description="用戶友好的墨爾本停車位搜尋工具",
    version="2.0.0"
)

# Popular Melbourne locations with coordinates
POPULAR_LOCATIONS = {
    "melbourne_cbd": {
        "name": "Melbourne CBD / 墨爾本市中心",
        "latitude": -37.8136,
        "longitude": 144.9631
    },
    "federation_square": {
        "name": "Federation Square / 聯邦廣場",
        "latitude": -37.8179,
        "longitude": 144.9690
    },
    "queen_victoria_market": {
        "name": "Queen Victoria Market / 維多利亞女王市場",
        "latitude": -37.8076,
        "longitude": 144.9568
    },
    "flinders_street": {
        "name": "Flinders Street Station / 弗林德斯街車站",
        "latitude": -37.8183,
        "longitude": 144.9671
    },
    "melbourne_central": {
        "name": "Melbourne Central / 墨爾本中央",
        "latitude": -37.8103,
        "longitude": 144.9633
    },
    "southbank": {
        "name": "Southbank / 南岸",
        "latitude": -37.8226,
        "longitude": 144.9648
    },
    "docklands": {
        "name": "Docklands / 碼頭區",
        "latitude": -37.8161,
        "longitude": 144.9472
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
        <title>墨爾本停車助手 Melbourne Parking Finder</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                color: #2c3e50;
            }}
            .search-section {{
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            .form-group {{
                margin-bottom: 20px;
            }}
            .form-row {{
                display: flex;
                gap: 15px;
                align-items: end;
            }}
            .form-row .form-group {{
                flex: 1;
            }}
            label {{
                display: block;
                margin-bottom: 8px;
                font-weight: bold;
                color: #34495e;
            }}
            input, select {{
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 16px;
                box-sizing: border-box;
            }}
            input:focus, select:focus {{
                border-color: #3498db;
                outline: none;
            }}
            .btn-group {{
                display: flex;
                gap: 10px;
                margin-top: 15px;
            }}
            button {{
                background-color: #3498db;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 16px;
                font-weight: bold;
                flex: 1;
                transition: background-color 0.3s;
            }}
            button:hover {{
                background-color: #2980b9;
            }}
            .btn-secondary {{
                background-color: #95a5a6;
            }}
            .btn-secondary:hover {{
                background-color: #7f8c8d;
            }}
            .result {{
                margin-top: 25px;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid #3498db;
            }}
            .loading {{
                display: none;
                color: #3498db;
                text-align: center;
                font-size: 18px;
                margin: 20px 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
                background-color: white;
                border-radius: 6px;
                overflow: hidden;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            th, td {{
                border: none;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #34495e;
                color: white;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background-color: #f8f9fa;
            }}
            .info-box {{
                background-color: #e8f5e8;
                border: 1px solid #27ae60;
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 20px;
            }}
            .search-mode {{
                background-color: #fff3cd;
                border: 1px solid #ffc107;
                padding: 10px;
                border-radius: 4px;
                margin-bottom: 20px;
                text-align: center;
            }}
            @media (max-width: 768px) {{
                .form-row {{
                    flex-direction: column;
                }}
                .btn-group {{
                    flex-direction: column;
                }}
                body {{
                    padding: 10px;
                }}
                .container {{
                    padding: 20px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚗 墨爾本停車助手</h1>
                <h2>Melbourne Parking Finder</h2>
                <p>找到離你最近的停車位 Find nearby parking spots</p>
            </div>

            <div class="info-box">
                <strong>🎉 全新升級！</strong> 現在可以選擇熱門地點，無需手動輸入座標！<br>
                <strong>Now with popular locations!</strong> No need to manually enter coordinates.
            </div>

            <div class="search-section">
                <form id="parkingForm">
                    <div class="form-group">
                        <label for="location">選擇熱門地點 Select Popular Location:</label>
                        <select id="location">
                            <option value="">-- 選擇地點或手動輸入座標 Select location or enter coordinates manually --</option>
                            {location_options}
                        </select>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="latitude">緯度 Latitude:</label>
                            <input type="number" id="latitude" step="any" value="" placeholder="例如 -37.8136">
                        </div>
                        <div class="form-group">
                            <label for="longitude">經度 Longitude:</label>
                            <input type="number" id="longitude" step="any" value="" placeholder="例如 144.9631">
                        </div>
                        <div class="form-group">
                            <label for="radius">搜尋半徑 Radius (公尺/meters):</label>
                            <input type="number" id="radius" value="500" placeholder="500" min="100" max="2000">
                        </div>
                    </div>

                    <div class="btn-group">
                        <button type="submit">🔍 搜尋停車位 Find Parking</button>
                        <button type="button" class="btn-secondary" onclick="getCurrentLocation()">📍 使用我的位置 Use My Location</button>
                    </div>
                </form>
            </div>

            <div class="loading" id="loading">
                🔄 正在搜尋停車位... Searching for parking spots...
            </div>
            <div id="result" class="result" style="display: none;"></div>
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
                            alert('✅ 位置已獲取！Location obtained!');
                        }},
                        function(error) {{
                            document.getElementById('loading').style.display = 'none';
                            alert('❌ 無法獲取位置：' + error.message + '\\nCannot get location: ' + error.message);
                        }}
                    );
                }} else {{
                    alert('❌ 您的瀏覽器不支援定位功能\\nGeolocation is not supported by this browser');
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
                    alert('❌ 請選擇地點或輸入有效的座標\\nPlease select a location or enter valid coordinates');
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
                            location_name: locationName
                        }})
                    }});

                    const data = await response.json();

                    if (data.status === 'success') {{
                        document.getElementById('result').innerHTML =
                            `<h3>✅ 找到 ${{data.found_spots}} 個停車位！Found ${{data.found_spots}} parking spots!</h3>` +
                            `<p><strong>搜尋地點 Search Location:</strong> ${{data.search_location}}</p>` +
                            data.html_table;
                    }} else {{
                        document.getElementById('result').innerHTML =
                            `<h3>❌ ${{data.message}}</h3>`;
                    }}
                }} catch (error) {{
                    document.getElementById('result').innerHTML =
                        `<h3>❌ 錯誤 Error: ${{error.message}}</h3>`;
                }}

                document.getElementById('loading').style.display = 'none';
                document.getElementById('result').style.display = 'block';
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
            raise HTTPException(status_code=400, detail="緯度必須在 -90 到 90 之間 / Latitude must be between -90 and 90")
        if not (-180 <= request.longitude <= 180):
            raise HTTPException(status_code=400, detail="經度必須在 -180 到 180 之間 / Longitude must be between -180 and 180")
        if not (50 <= request.radius <= 5000):
            raise HTTPException(status_code=400, detail="搜尋半徑必須在 50 到 5000 公尺之間 / Radius must be between 50 and 5000 meters")

        # Determine location name for display
        search_location = request.location_name if request.location_name else f"座標 ({request.latitude:.4f}, {request.longitude:.4f})"

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
                message="目前半徑內沒有空位，建議擴大搜尋範圍。No available spots within radius, try expanding search area.",
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
            message=f"成功找到 {len(formatted_spots)} 個停車位 / Found {len(formatted_spots)} parking spots",
            search_location=search_location
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"系統錯誤 Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "mode": "user_friendly", "locations": len(POPULAR_LOCATIONS)}

@app.get("/locations")
async def get_locations():
    """返回所有熱門地點列表"""
    return {"locations": POPULAR_LOCATIONS}

if __name__ == "__main__":
    import uvicorn
    print("Starting Melbourne Parking Agent User-Friendly Version...")
    print("Web Interface: http://localhost:8002")
    print("With popular locations and GPS features")
    uvicorn.run(app, host="0.0.0.0", port=8002)