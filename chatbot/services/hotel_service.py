# services/hotel_service.py
import httpx
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from geopy.distance import geodesic

class HotelService:
    """Service for searching and booking hotels."""
    
    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        self.api_host = "booking-com15.p.rapidapi.com"
        self.search_results = []
        
    async def search_hotels(self, 
                     latitude: float, 
                     longitude: float, 
                     arrival_date: str, 
                     departure_date: str, 
                     adults: int, 
                     room_qty: int, 
                     max_distance_km: float = 10.0,
                     children_age: str = None,
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
        
        # Add children_age parameter if provided
        if children_age:
            query_params["children_age"] = children_age

        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.api_host
        }

        try:
            # Using AsyncClient to match the FastAPI async implementation
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=query_params)
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
                    # Calculate distance between search coordinates and hotel coordinates
                    search_coords = (float(latitude), float(longitude))
                    hotel_coords = (float(hotel.get("latitude")), float(hotel.get("longitude")))
                    distance = geodesic(search_coords, hotel_coords).kilometers
                    
                    # Skip hotels beyond the max distance
                    if distance > max_distance_km:
                        continue
                    
                    # Create price breakdown dictionary
                    price_breakdown = None
                    if "composite_price_breakdown" in hotel:
                        price_breakdown = hotel.get("composite_price_breakdown")
                    
                    # Create badges list
                    badges = []
                    if "badges" in hotel and hotel.get("badges"):
                        for badge in hotel.get("badges"):
                            badges.append({
                                "badge_variant": badge.get("badge_variant"),
                                "text": badge.get("text", ""),
                                "explanation": badge.get("explanation", "")
                            })
                    
                    formatted_hotel = {
                        "hotel_id": hotel.get("hotel_id"),
                        "name": hotel.get("hotel_name"),
                        "address": f"{hotel.get('city')}, {hotel.get('countrycode')}",
                        "city": hotel.get("city"),
                        "country_code": hotel.get("countrycode", "").upper() if hotel.get("countrycode") else "",
                        "price": float(hotel.get("min_total_price", 0)),
                        "currency": hotel.get("currencycode"),
                        "latitude": hotel.get("latitude"),
                        "longitude": hotel.get("longitude"),
                        "rating": hotel.get("review_score"),
                        "rating_description": hotel.get("review_score_word"),
                        "review_count": hotel.get("review_nr"),
                        "photo_url": hotel.get("main_photo_url"),
                        "free_cancellation": hotel.get("is_free_cancellable", False),
                        "distance_km": round(distance, 2),
                        "price_breakdown": price_breakdown,
                        "badges": badges,
                        "accommodation_type": hotel.get("accommodation_type"),
                        "timezone": hotel.get("timezone")
                    }
                    formatted_hotels.append(formatted_hotel)
                
                # Sort by distance
                formatted_hotels.sort(key=lambda x: x["distance_km"])
                
                # Store the search results
                self.search_results = formatted_hotels
                return formatted_hotels
                
        except httpx.HTTPStatusError as e:
            print(f"API Error: {e.response.text}")
            return None
        except Exception as e:
            print(f"Error: {str(e)}")
            return None
    
    # For backwards compatibility, provide a synchronous version
    def search_hotels_sync(self, **kwargs):
        """Synchronous version of search_hotels for compatibility."""
        import asyncio
        return asyncio.run(self.search_hotels(**kwargs))
    
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
    
    def get_hotel_by_id(self, hotel_id: str) -> Optional[Dict[str, Any]]:
        """Find a hotel in search results by ID."""
        for hotel in self.search_results:
            if hotel.get('hotel_id') == hotel_id:
                return hotel
        return None
        
    def format_search_results_for_display(self) -> str:
        """Format search results for displaying to the user."""
        if not self.search_results:
            return "No hotels found matching your criteria."
            
        result = "Here are the hotels that match your criteria:\n"
        
        for i, hotel in enumerate(self.search_results[:10], 1):  # Show top 10 results
            # Include distance in the display
            result += (f"{i}. **{hotel['name']}:** Price: {hotel['price']} {hotel['currency']}, "
                      f"Rating: {hotel['rating']}, Distance: {hotel['distance_km']} km\n")
            
        result += "\nWould you like to book one of these hotels? Just let me know which one."
        return result