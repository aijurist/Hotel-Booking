# services/geo_service.py
from geopy.geocoders import Photon
from typing import Optional, Tuple

class GeoService:
    """Service for handling geolocation requests."""
    
    def __init__(self):
        self.geolocator = Photon(user_agent="hotel_search_app", timeout=10)
    
    def get_coordinates(self, location_name: str) -> Optional[Tuple[float, float]]:
        """Get coordinates for a location name."""
        try:
            location = self.geolocator.geocode(
                location_name,
                exactly_one=True,
                language="en",
                limit=1
            )
            if location:
                print(f"Found location: {location.address}")
                print(f"Coordinates: {location.latitude}, {location.longitude}")
                return (location.latitude, location.longitude)
            print(f"No location found for: {location_name}")
            return None
        except Exception as e:
            print(f"Geocoding error: {str(e)}")
            return None
