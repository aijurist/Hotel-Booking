# services/hotel_service.py
import httpx
import os
from typing import Optional, List, Dict, Any
from datetime import datetime

class HotelService:
    """Service for searching and booking hotels."""
    
    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        self.api_host = "booking-com15.p.rapidapi.com"
        self.search_results = []
        
    def search_hotels(self, 
                     latitude: float, 
                     longitude: float, 
                     arrival_date: str, 
                     departure_date: str, 
                     adults: int, 
                     room_qty: int, 
                     currency_code: str = "EUR") -> Optional[List[Dict[str, Any]]]:
        """Search for hotels using coordinates and booking details."""
        url = f"https://{self.api_host}/api/v1/hotels/searchHotelsByCoordinates"
        
        query_params = {
            "latitude": latitude,
            "longitude": longitude,
            "arrival_date": arrival_date,
            "departure_date": departure_date,
            "adults": adults,
            "room_qty": room_qty,
            "currency_code": currency_code,
            "units": "metric",
            "page_number": "1",
            "temperature_unit": "c",
            "languagecode": "en-us",
        }

        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.api_host
        }

        try:
            with httpx.Client() as client:
                response = client.get(url, headers=headers, params=query_params)
                response.raise_for_status()
                raw_data = response.json()
                
                # Extract relevant hotel data
                hotels = raw_data.get("data", {}).get("result", [])
                if not hotels:
                    print("No hotels found.")
                    return None

                # Format hotel data
                formatted_hotels = []
                for hotel in hotels:
                    formatted_hotel = {
                        "name": hotel.get("hotel_name"),
                        "address": f"{hotel.get('city')}, {hotel.get('countrycode')}",
                        "price": hotel.get("min_total_price"),
                        "currency": hotel.get("currencycode"),
                        "rating": hotel.get("review_score"),
                        "photo_url": hotel.get("main_photo_url"),
                        "free_cancellation": hotel.get("is_free_cancellable", False)
                    }
                    formatted_hotels.append(formatted_hotel)
                
                # Store the search results
                self.search_results = formatted_hotels
                return formatted_hotels
        except httpx.HTTPStatusError as e:
            print(f"API Error: {e.response.text}")
            return None
        except Exception as e:
            print(f"Error: {str(e)}")
            return None
    
    def book_hotel(self, hotel_name: str, context: Dict[str, Any]) -> str:
        """Create a booking for a specific hotel."""
        # Find the hotel in the search results
        selected_hotel = None
        for hotel in self.search_results:
            if hotel_name.lower() in hotel['name'].lower():
                selected_hotel = hotel
                break
        
        if not selected_hotel:
            return "Hotel not found in search results."
        
        # Create booking confirmation
        booking_details = f"""
--- Booking Confirmation ---
Hotel: {selected_hotel['name']}
Address: {selected_hotel['address']}
Price: {selected_hotel['price']} {selected_hotel['currency']}
Check-in: {context.get('arrival_date')}
Check-out: {context.get('departure_date')}
Guests: {context.get('adults')}
Rooms: {context.get('rooms')}
Room types: {', '.join(context.get('room_types', ['Standard']))}
Booking reference: BOK{datetime.now().strftime('%Y%m%d%H%M%S')}
        """
        
        return booking_details
        
    def get_hotel_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find a hotel in search results by name."""
        for hotel in self.search_results:
            if name.lower() in hotel['name'].lower():
                return hotel
        return None
        
    def format_search_results_for_display(self) -> str:
        """Format search results for displaying to the user."""
        if not self.search_results:
            return "No hotels found matching your criteria."
            
        result = "Here are the hotels that match your criteria:\n"
        
        for i, hotel in enumerate(self.search_results[:10], 1):  # Show top 10 results
            result += f"{i}. **{hotel['name']}:** Price: {hotel['price']} {hotel['currency']}, Rating: {hotel['rating']}\n"
            
        result += "\nWould you like to book one of these hotels? Just let me know which one."
        return result