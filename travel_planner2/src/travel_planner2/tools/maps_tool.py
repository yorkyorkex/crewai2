import os
import googlemaps
from typing import List, Dict, Any, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel


class GoogleMapsTool(BaseTool):
    name: str = "Google Maps Tool"
    description: str = "A tool to search for places, get directions, and calculate distances using Google Maps API."

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._gmaps = None

    @property
    def gmaps(self):
        if self._gmaps is None:
            api_key = os.getenv("GOOGLE_MAPS_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_MAPS_API_KEY not found in environment variables")
            self._gmaps = googlemaps.Client(key=api_key)
        return self._gmaps

    def _run(self, operation: str, **kwargs) -> str:
        """
        Perform various Google Maps operations

        Args:
            operation (str): The operation to perform ("places_search", "directions", "distance_matrix")
            **kwargs: Additional parameters for the operation

        Returns:
            str: Formatted results
        """
        try:
            if operation == "places_search":
                return self._places_search(**kwargs)
            elif operation == "directions":
                return self._get_directions(**kwargs)
            elif operation == "distance_matrix":
                return self._distance_matrix(**kwargs)
            else:
                return f"Unknown operation: {operation}. Available operations: places_search, directions, distance_matrix"

        except Exception as e:
            return f"Error performing {operation}: {str(e)}"

    def _places_search(self, query: str, location: Optional[str] = None, radius: int = 5000, place_type: Optional[str] = None) -> str:
        """Search for places using Google Maps Places API"""
        try:
            # If location is specified, search nearby
            if location:
                # First geocode the location
                geocode_result = self.gmaps.geocode(location)
                if not geocode_result:
                    return f"Could not find location: {location}"

                location_coords = geocode_result[0]['geometry']['location']

                # Search for places nearby
                places_result = self.gmaps.places_nearby(
                    location=location_coords,
                    radius=radius,
                    keyword=query,
                    type=place_type
                )
            else:
                # Text search
                places_result = self.gmaps.places(
                    query=query,
                    type=place_type
                )

            results = []
            results.append(f"Places search results for '{query}':")
            results.append("")

            places = places_result.get('results', [])

            for i, place in enumerate(places[:10], 1):
                name = place.get('name', 'Unknown')
                rating = place.get('rating', 'No rating')
                address = place.get('formatted_address', place.get('vicinity', 'No address'))
                types = ', '.join(place.get('types', [])[:3])

                results.append(f"{i}. {name}")
                results.append(f"   Rating: {rating}")
                results.append(f"   Address: {address}")
                results.append(f"   Types: {types}")

                if 'geometry' in place:
                    location = place['geometry']['location']
                    results.append(f"   Coordinates: {location['lat']:.6f}, {location['lng']:.6f}")

                results.append("")

            return "\n".join(results) if results else "No places found"

        except Exception as e:
            return f"Error searching places: {str(e)}"

    def _get_directions(self, origin: str, destination: str, mode: str = "driving", waypoints: Optional[List[str]] = None) -> str:
        """Get directions between two points"""
        try:
            directions_result = self.gmaps.directions(
                origin=origin,
                destination=destination,
                mode=mode,
                waypoints=waypoints
            )

            if not directions_result:
                return f"No directions found from {origin} to {destination}"

            route = directions_result[0]
            leg = route['legs'][0]

            results = []
            results.append(f"Directions from {origin} to {destination}:")
            results.append(f"Distance: {leg['distance']['text']}")
            results.append(f"Duration: {leg['duration']['text']}")
            results.append("")

            results.append("Steps:")
            for i, step in enumerate(leg['steps'], 1):
                instruction = step['html_instructions'].replace('<b>', '').replace('</b>', '').replace('<div>', ' ').replace('</div>', '')
                distance = step['distance']['text']
                duration = step['duration']['text']
                results.append(f"{i}. {instruction}")
                results.append(f"   ({distance}, {duration})")

            return "\n".join(results)

        except Exception as e:
            return f"Error getting directions: {str(e)}"

    def _distance_matrix(self, origins: List[str], destinations: List[str], mode: str = "driving") -> str:
        """Calculate distance matrix between multiple origins and destinations"""
        try:
            matrix_result = self.gmaps.distance_matrix(
                origins=origins,
                destinations=destinations,
                mode=mode
            )

            results = []
            results.append("Distance Matrix:")
            results.append("")

            origin_addresses = matrix_result['origin_addresses']
            destination_addresses = matrix_result['destination_addresses']

            for i, origin in enumerate(origin_addresses):
                results.append(f"From: {origin}")

                for j, destination in enumerate(destination_addresses):
                    element = matrix_result['rows'][i]['elements'][j]

                    if element['status'] == 'OK':
                        distance = element['distance']['text']
                        duration = element['duration']['text']
                        results.append(f"  To {destination}: {distance} ({duration})")
                    else:
                        results.append(f"  To {destination}: No route found")

                results.append("")

            return "\n".join(results)

        except Exception as e:
            return f"Error calculating distance matrix: {str(e)}"