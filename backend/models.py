from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class HotelSearchParams(BaseModel):
    latitude: float
    longitude: float
    arrival_date: str
    departure_date: str
    adults: int
    children_age: Optional[str] = None
    room_qty: int = 1
    currency_code: str = "USD"

class Badge(BaseModel):
    id: str
    text: str
    badge_variant: str

class PriceBreakdown(BaseModel):
    gross_amount: Optional[Dict[str, Any]] = None
    net_amount: Optional[Dict[str, Any]] = None
    excluded_amount: Optional[Dict[str, Any]] = None
    all_inclusive_amount: Optional[Dict[str, Any]] = None
    items: Optional[List[Dict[str, Any]]] = None
    benefits: Optional[List[Dict[str, Any]]] = None
    discounted_amount: Optional[Dict[str, Any]] = None
    strikethrough_amount: Optional[Dict[str, Any]] = None

class Hotel(BaseModel):
    hotel_id: int
    hotel_name: str
    hotel_name_trans: Optional[str] = None
    city: str
    city_in_trans: Optional[str] = None
    countrycode: str
    latitude: float
    longitude: float
    review_score: Optional[float] = None
    review_score_word: Optional[str] = None
    review_nr: Optional[int] = None
    main_photo_url: str
    min_total_price: float
    currencycode: str
    is_free_cancellable: bool
    composite_price_breakdown: Optional[PriceBreakdown] = None
    badges: Optional[List[Badge]] = None
    accommodation_type: Optional[int] = None
    timezone: Optional[str] = None

class SearchResult(BaseModel):
    result: List[Hotel]
    filters: Optional[List[Dict[str, Any]]] = None
    unfiltered_count: Optional[int] = None
    count: Optional[int] = None

class HotelSearchResponse(BaseModel):
    status: bool
    message: str
    timestamp: Optional[int] = None
    data: SearchResult

class HotelResponse(BaseModel):
    hotel_id: int
    hotel_name: str
    price: float = Field(..., alias="min_total_price")
    currency: str = Field(..., alias="currencycode")
    rating: Optional[float] = Field(None, alias="review_score")
    rating_description: Optional[str] = Field(None, alias="review_score_word")
    review_count: Optional[int] = Field(None, alias="review_nr")
    city: str
    country_code: str = Field(..., alias="countrycode")
    latitude: float
    longitude: float
    photo_url: str = Field(..., alias="main_photo_url")
    booking_url: str = Field("")
    free_cancellation: bool = Field(False, alias="is_free_cancellable")
    badges: List[Dict[str, str]] = []
    price_breakdown: Optional[Dict[str, Any]] = Field(None, alias="composite_price_breakdown")
    accommodation_type: Optional[int] = None
    timezone: Optional[str] = None

    class Config:
        populate_by_name = True