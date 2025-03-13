from fastapi import FastAPI, HTTPException, Depends
import httpx
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from models import HotelSearchParams, HotelResponse, HotelSearchResponse, Hotel, Badge
from typing import List, Optional
from pydantic import ValidationError, BaseModel
from geopy.distance import geodesic

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "booking-com15.p.rapidapi.com"

@app.get("/api/test")
async def test_endpoint():
    return {"status": 200, "message": "Server Working"}

def parse_badges(badges: List[Badge]) -> List[dict]:
    return [badge.dict() for badge in badges] if badges else []

# Update HotelResponse to include distance
class HotelResponseWithDistance(HotelResponse):
    distance_km: Optional[float] = None

@app.get("/api/hotels/search", response_model=List[HotelResponseWithDistance])
async def search_hotels(params: HotelSearchParams = Depends(), max_distance_km: float = 10.0):
    url = f"https://{RAPIDAPI_HOST}/api/v1/hotels/searchHotelsByCoordinates"
    
    query_params = {
        "latitude": params.latitude,
        "longitude": params.longitude,
        "arrival_date": params.arrival_date,
        "departure_date": params.departure_date,
        "adults": params.adults,
        "children_age": params.children_age if params.children_age else "",
        "room_qty": params.room_qty,
        "units": "metric",
        "page_number": "1",
        "temperature_unit": "c",
        "languagecode": "en-us",
        "currency_code": params.currency_code or "INR",
    }

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=query_params)
            response.raise_for_status()
            
            raw_data = response.json()
            
            try:
                search_response = HotelSearchResponse(**raw_data)
            except ValidationError as e:
                print(f"Validation error in API response: {e}")
                return []

            hotels = search_response.data.result
            if not hotels:
                return []

            hotel_responses = []
            for hotel_data in hotels:
                try:
                    hotel_response = HotelResponse(
                        hotel_id=hotel_data.hotel_id,
                        hotel_name=hotel_data.hotel_name,
                        price=float(hotel_data.min_total_price),
                        currency=hotel_data.currencycode,
                        city=hotel_data.city,
                        country_code=hotel_data.countrycode.upper(),
                        latitude=hotel_data.latitude,
                        longitude=hotel_data.longitude,
                        photo_url=hotel_data.main_photo_url,
                        rating=hotel_data.review_score,
                        rating_description=hotel_data.review_score_word,
                        review_count=hotel_data.review_nr,
                        free_cancellation=hotel_data.is_free_cancellable,
                        badges=parse_badges(hotel_data.badges),
                        price_breakdown=hotel_data.composite_price_breakdown.dict() if hotel_data.composite_price_breakdown else None,
                        accommodation_type=hotel_data.accommodation_type,
                        timezone=hotel_data.timezone
                    )
                    # Calculate distance between search coordinates and hotel coordinates
                    search_coords = (float(params.latitude), float(params.longitude))
                    hotel_coords = (hotel_response.latitude, hotel_response.longitude)
                    distance = geodesic(search_coords, hotel_coords).kilometers
                    
                    # Create a response with distance
                    hotel_dict = hotel_response.dict()
                    hotel_dict["distance_km"] = round(distance, 2)
                    hotel_responses.append(HotelResponseWithDistance(**hotel_dict))
                except (ValidationError, ValueError) as e:
                    print(f"Error processing hotel data: {e}")
                    continue

            # Filter hotels by distance
            filtered_hotel_responses = [hotel for hotel in hotel_responses if hotel.distance_km <= max_distance_km]
            
            # Sort by distance
            filtered_hotel_responses.sort(key=lambda x: x.distance_km)
            
            return filtered_hotel_responses

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error fetching hotel data: {e.response.text}")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)