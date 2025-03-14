from langchain.tools import BaseTool
from models.hotel_models import UserPreferences
from services.hotel_service import HotelService
from typing import Optional
from pydantic import Field
import csv

class HotelBookingTool(BaseTool):
    name: str = "hotel_booking_tool"
    description: str = "Books a hotel from search results. Input should be the hotel name."
    user_prefs: UserPreferences
    hotel_service: HotelService = Field(default_factory=HotelService, exclude=True)
    
    def _run(self, hotel_name: str) -> str:
        if not hotel_name:
            return "Please provide a hotel name to book."
        
        context = {
            "arrival_date": self.user_prefs.check_in.strftime("%Y-%m-%d") if self.user_prefs.check_in else None,
            "departure_date": self.user_prefs.check_out.strftime("%Y-%m-%d") if self.user_prefs.check_out else None,
            "adults": self.user_prefs.adults,
            "rooms": self.user_prefs.room_qty,
            "room_types": ["Standard"]
        }
        
        booking_result = self.hotel_service.book_hotel(hotel_name, context)
        if "confirmed" in booking_result.lower():
            self._save_booking_details(hotel_name, context)
            return f"Booking confirmed for {hotel_name}."
        else:
            return "Hotel booking failed. Please try again later."
    
    def _save_booking_details(self, hotel_name: str, context: dict):
        with open("hotel_bookings.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([hotel_name, context["arrival_date"], context["departure_date"], context["adults"], context["rooms"]])
