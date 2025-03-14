from langchain.tools import BaseTool
from models.hotel_models import UserPreferences
from services.hotel_service import HotelService
from typing import Optional
import asyncio
from pydantic import Field

class HotelSearchTool(BaseTool):
    name: str = "hotel_search_tool"
    description: str = "Search hotels using collected preferences. No input needed."
    user_prefs: UserPreferences
    hotel_service: HotelService = Field(default_factory=HotelService, exclude=True)

    def _run(self, query: Optional[str] = None) -> str:
        """Search for hotels based on user preferences."""
        if not self.user_prefs.is_ready_for_search():
            missing = []
            if not self.user_prefs.latitude or not self.user_prefs.longitude:
                missing.append("location coordinates")
            if not self.user_prefs.check_in:
                missing.append("check-in date")
            if not self.user_prefs.check_out:
                missing.append("check-out date")
            
            return f"Cannot search yet. Missing information: {', '.join(missing)}."
        
        try:
            # Format dates correctly for the API
            arrival_date = self.user_prefs.check_in.strftime("%Y-%m-%d")
            departure_date = self.user_prefs.check_out.strftime("%Y-%m-%d")
            
            # Create search parameters
            search_params = {
                "latitude": self.user_prefs.latitude,
                "longitude": self.user_prefs.longitude,
                "arrival_date": arrival_date,
                "departure_date": departure_date,
                "adults": self.user_prefs.adults,
                "room_qty": self.user_prefs.room_qty,
                "currency_code": self.user_prefs.currency_code
            }
            
            # Add children ages if provided
            if self.user_prefs.children_age:
                search_params["children_age"] = self.user_prefs.children_age
            
            # Run the search asynchronously
            results = asyncio.run(self.hotel_service.search_hotels(**search_params))
            
            if not results or len(results) == 0:
                return "No hotels found matching your criteria. Try adjusting your search parameters."
            
            # Format the results for display
            response = f"I found {len(results)} hotels in {self.user_prefs.city or 'the area'}:\n\n"
            
            for i, hotel in enumerate(results[:5], 1):  # Show top 5 results
                response += (f"{i}. **{hotel['name']}**\n"
                            f"   Price: {hotel['price']} {hotel['currency']}\n"
                            f"   Rating: {hotel.get('rating', 'N/A')}/10\n"
                            f"   Distance: {hotel['distance_km']} km from center\n\n")
                
            response += "Would you like to book one of these hotels or see more options?"
            return response
            
        except Exception as e:
            return f"Error searching for hotels: {str(e)}"
