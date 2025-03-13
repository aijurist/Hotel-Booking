from geopy.geocoders import Photon
from geopy.distance import geodesic

def get_coordinates(location_name: str) -> tuple:
    """Get coordinates using Photon (OpenStreetMap-based)"""
    try:
        geolocator = Photon(user_agent="hotel_search_app", timeout=10)
        location = geolocator.geocode(
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