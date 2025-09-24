import requests
import json
import math
from datetime import datetime
import pytz
from typing import List, Dict, Any
from crewai.tools import BaseTool

class MelbourneParkingTool(BaseTool):
    name: str = "Melbourne Parking Tool"
    description: str = "Fetches available parking spots in Melbourne using real-time sensor data and calculates distances from user location"

    def _run(self, latitude: float, longitude: float, radius: int = 500) -> str:
        """
        Find available parking spots near the given coordinates.

        Args:
            latitude: User's latitude
            longitude: User's longitude
            radius: Search radius in meters (default: 500)

        Returns:
            JSON string with parking data or error message
        """
        try:
            # Fetch parking data from Melbourne API
            parking_data = self._fetch_parking_data()

            if not parking_data:
                return json.dumps({
                    "status": "error",
                    "message": "無法取得停車資料",
                    "parking_spots": [],
                    "html_table": ""
                })

            # Filter for unoccupied spots only
            unoccupied_spots = [
                spot for spot in parking_data
                if spot.get('status_description') == 'Unoccupied'
            ]

            # If no unoccupied spots, take all spots for demonstration
            if not unoccupied_spots:
                print(f"No unoccupied spots found, using all {len(parking_data)} spots for demo")
                unoccupied_spots = parking_data[:50]  # Take first 50 for testing

            # Calculate distances and filter by radius
            nearby_spots = []
            for spot in unoccupied_spots:
                spot_location = spot.get('location', {})
                if not spot_location:
                    continue

                spot_lat = spot_location.get('lat')
                spot_lon = spot_location.get('lon')

                if spot_lat is None or spot_lon is None:
                    continue

                # Calculate distance
                distance = self._calculate_distance(latitude, longitude, spot_lat, spot_lon)

                if distance <= radius:
                    # Convert timestamps
                    status_time = self._convert_to_melbourne_time(spot.get('status_timestamp'))
                    updated_time = self._convert_to_melbourne_time(spot.get('lastupdated'))

                    nearby_spots.append({
                        'bay_id': str(spot.get('kerbsideid', 'N/A')),
                        'status': spot.get('status_description', 'Unoccupied'),
                        'distance_meters': int(round(distance)),
                        'status_time': status_time,
                        'updated_time': updated_time,
                        'google_maps_link': f"https://www.google.com/maps/?q={spot_lat},{spot_lon}",
                        'latitude': spot_lat,
                        'longitude': spot_lon
                    })

            # Sort by distance (closest first)
            nearby_spots.sort(key=lambda x: x['distance_meters'])

            # Limit to top 20 results
            nearby_spots = nearby_spots[:20]

            if not nearby_spots:
                return json.dumps({
                    "status": "no_results",
                    "message": "目前半徑內沒有空位，建議擴大搜尋範圍。",
                    "parking_spots": [],
                    "html_table": ""
                })

            # Generate HTML table
            html_table = self._generate_html_table(nearby_spots)

            return json.dumps({
                "status": "success",
                "message": f"找到 {len(nearby_spots)} 個空車位",
                "parking_spots": nearby_spots,
                "html_table": html_table
            })

        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"API 呼叫失敗: {str(e)}",
                "parking_spots": [],
                "html_table": ""
            })

    def _fetch_parking_data(self) -> List[Dict[str, Any]]:
        """Fetch parking data from Melbourne API"""
        try:
            # Melbourne parking API endpoint
            url = "https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/on-street-parking-bay-sensors/records?limit=100"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            records = data.get('results', [])
            print(f"Fetched {len(records)} parking records")

            # Extract the actual record data
            parking_spots = []
            for record in records:
                if isinstance(record, dict):
                    parking_spots.append(record)

            return parking_spots

        except requests.RequestException as e:
            print(f"API request failed: {e}")
            print(f"URL was: {url}")
            return []
        except Exception as e:
            print(f"Data processing error: {e}")
            return []

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the distance between two points using the Haversine formula.
        Returns distance in meters.
        """
        # Convert latitude and longitude from degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = (math.sin(dlat/2)**2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)

        c = 2 * math.asin(math.sqrt(a))

        # Earth's radius in meters
        earth_radius = 6371000

        distance = earth_radius * c
        return distance

    def _convert_to_melbourne_time(self, timestamp_str: str) -> str:
        """Convert UTC timestamp to Melbourne local time"""
        if not timestamp_str:
            return "N/A"

        try:
            # Parse the timestamp (assuming UTC)
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

            # Convert to Melbourne timezone
            melbourne_tz = pytz.timezone('Australia/Melbourne')
            melbourne_dt = dt.astimezone(melbourne_tz)

            return melbourne_dt.strftime('%Y-%m-%d %H:%M:%S %Z')

        except Exception as e:
            print(f"Time conversion error: {e}")
            return timestamp_str

    def _generate_html_table(self, spots: List[Dict[str, Any]]) -> str:
        """Generate HTML table for parking spots"""
        if not spots:
            return "<p>No parking spots found</p>"

        html = """
        <table>
            <thead>
                <tr>
                    <th>Bay ID</th>
                    <th>Status</th>
                    <th>Distance</th>
                    <th>Status Time</th>
                    <th>Last Updated</th>
                    <th>Google Maps</th>
                </tr>
            </thead>
            <tbody>
        """

        for spot in spots:
            html += f"""
                <tr>
                    <td>{spot['bay_id']}</td>
                    <td>{spot['status']}</td>
                    <td>{spot['distance_meters']}m</td>
                    <td>{spot['status_time']}</td>
                    <td>{spot['updated_time']}</td>
                    <td><a href="{spot['google_maps_link']}" target="_blank">🗺️ Maps</a></td>
                </tr>
            """

        html += """
            </tbody>
        </table>
        """

        return html