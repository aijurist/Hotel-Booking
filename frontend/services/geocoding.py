from geopy.geocoders import Nominatim

def get_coordinates(location_name: str) -> tuple:
    """Get precise coordinates for a location name"""
    try:
        geolocator = Nominatim(user_agent="hotel_search_app", timeout=10)
        location = geolocator.geocode(
            location_name, 
            exactly_one=True,
            addressdetails=True
        )
        if location:
            return (location.latitude, location.longitude)
        return None
    except Exception as e:
        print(f"Geocoding error: {str(e)}")
        return None