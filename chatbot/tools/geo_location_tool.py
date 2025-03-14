# tools/geo_location_tool.py
from langchain.tools import BaseTool
from geopy.geocoders import Photon
from models.hotel_models import UserPreferences
from typing import Optional, Tuple

class GeoLocationTool(BaseTool):
    name: str = "geo_location_tool"
    description: str = "Convert city names to coordinates. Input: city name"
    user_prefs: UserPreferences

    def _run(self, city: str) -> str:
        try:
            geolocator = Photon(user_agent="hotel_agent")
            location = geolocator.geocode(city)
            if not location:
                return f"Could not find coordinates for {city}"
            
            self.user_prefs.city = city
            self.user_prefs.coordinates = (location.latitude, location.longitude)
            return f"Coordinates for {city}: {location.latitude}, {location.longitude}"
        except Exception as e:
            return f"Geocoding error: {str(e)}"