from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date, timedelta

class Coordinates(BaseModel):
    latitude: Optional[float] = Field(None, description="Latitude coordinate of the location")
    longitude: Optional[float] = Field(None, description="Longitude coordinate of the location")

class UserPreferences(BaseModel):
    # Core fields needed for HotelService.search_hotels
    latitude: Optional[float] = Field(None, description="Latitude coordinate of the location")
    longitude: Optional[float] = Field(None, description="Longitude coordinate of the location")
    check_in: Optional[date] = Field(None, description="Arrival date")
    check_out: Optional[date] = Field(None, description="Departure date")
    adults: int = Field(1, description="Number of adults", ge=1)
    room_qty: int = Field(1, description="Number of rooms", ge=1)
    coordinates:  Optional[Coordinates] = Field(None, description="Contains latitude and longitude")
    # Additional fields for context
    city: Optional[str] = Field(None, description="City name for location context")
    nights: Optional[int] = Field(None, description="Number of nights to stay")
    children_age: Optional[str] = Field(None, description="Ages of children, comma-separated")
    currency_code: str = Field("EUR", description="Currency code for pricing")
    
    def is_ready_for_search(self) -> bool:
        """Check if all required fields are set for a hotel search."""
        return (
            self.latitude is not None and
            self.longitude is not None and
            self.check_in is not None and
            self.check_out is not None and
            self.adults is not None and
            self.room_qty is not None
        )
    
    def update(self, field: str, value: str) -> str:
        """Update a preference field with the given value."""
        try:
            if field == "city":
                self.city = value
            elif field in ["latitude", "longitude"]:
                setattr(self, field, float(value))
            elif field == "check_in":
                self.check_in = datetime.strptime(value, "%Y-%m-%d").date()
                # Update check_out if nights is set
                if self.nights is not None:
                    self.check_out = self.check_in + timedelta(days=self.nights)
            elif field == "check_out":
                self.check_out = datetime.strptime(value, "%Y-%m-%d").date()
                # Update nights if check_in is set
                if self.check_in is not None:
                    self.nights = (self.check_out - self.check_in).days
            elif field == "nights":
                nights_value = int(value)
                if nights_value <= 0:
                    return f"Invalid {field} value: {value}. Must be a positive number."
                self.nights = nights_value
                # Update check_out if check_in is set
                if self.check_in is not None:
                    self.check_out = self.check_in + timedelta(days=nights_value)
            elif field == "adults":
                adults_value = int(value)
                if adults_value <= 0:
                    return f"Invalid {field} value: {value}. Must be a positive number."
                self.adults = adults_value
            elif field == "rooms" or field == "room_qty":
                room_value = int(value)
                if room_value <= 0:
                    return f"Invalid {field} value: {value}. Must be a positive number."
                # Set both fields to ensure compatibility
                self.room_qty = room_value
            elif field == "children_age":
                self.children_age = value
            elif field == "currency_code":
                self.currency_code = value.upper()
            else:
                return f"Invalid field: {field}"
            
            return f"Updated {field} to {value}"
        except ValueError as e:
            return f"Error updating {field}: {str(e)}"