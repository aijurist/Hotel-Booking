# Main app.py file
import streamlit as st
from datetime import datetime, timedelta
from services.api_client import search_hotels
from services.geocoding import get_coordinates
from components.hotel_card import hotel_card
from utils.styles import load_styles

# Set page config
st.set_page_config(
    page_title="Hotel Booking Platform",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom styles
st.markdown(load_styles(), unsafe_allow_html=True)

# Initialize session state
if 'search' not in st.session_state:
    st.session_state.search = False
if 'expanded_hotels' not in st.session_state:
    st.session_state.expanded_hotels = []
if 'search_params' not in st.session_state:
    st.session_state.search_params = {}

def main():
    # Header with logo and tagline
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 20px;">
        <div style="font-size: 2.5rem; margin-right: 10px;">🏨</div>
        <div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #1e3a8a;">Hotel Booking Platform</div>
            <div style="color: #6b7280; font-size: 1rem;">Find your perfect stay anywhere in the world</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for search filters with modern styling
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 15px;">
            <h2 style="color: #1e3a8a; font-weight: 700;">🔍 Find Your Stay</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Search form with improved layout
        with st.form("search_form"):
            location = st.text_input("Destination", "Paris, France")
            
            col_dates = st.columns(2)
            with col_dates[0]:
                check_in = st.date_input("Check-in", datetime.now() + timedelta(days=1))
            with col_dates[1]:
                check_out = st.date_input("Check-out", datetime.now() + timedelta(days=4))
            
            st.markdown("##### 👥 Travelers")
            travelers_col1, travelers_col2 = st.columns(2)
            with travelers_col1:
                adults = st.number_input("Adults", 1, 10, 2)
            with travelers_col2:
                rooms = st.number_input("Rooms", 1, 5, 1)
            
            currency = st.selectbox(
                "Currency", 
                options=["USD", "EUR", "GBP", "JPY"], 
                format_func=lambda x: f"{x} ({get_currency_symbol(x)})"
            )
            
            submitted = st.form_submit_button("Search Hotels", use_container_width=True)
            if submitted:
                st.session_state.search = True
                st.session_state.search_params = {
                    "location": location,
                    "check_in": check_in,
                    "check_out": check_out,
                    "adults": adults,
                    "rooms": rooms,
                    "currency": currency
                }
        
        # Additional sidebar info
        st.markdown("""
        <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; margin-top: 20px;">
            <div style="font-weight: 600; margin-bottom: 10px; color: #4b5563;">✨ Why Book With Us</div>
            <ul style="margin: 0; padding-left: 20px; color: #6b7280;">
                <li>No hidden fees</li>
                <li>Free cancellation options</li>
                <li>24/7 customer support</li>
                <li>Best price guarantee</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Handle search if triggered
    if st.session_state.get('search'):
        handle_search(
            st.session_state.search_params["location"],
            st.session_state.search_params["check_in"],
            st.session_state.search_params["check_out"],
            st.session_state.search_params["adults"],
            st.session_state.search_params["rooms"],
            st.session_state.search_params["currency"]
        )
    else:
        # Welcome message with featured destinations when no search performed
        display_welcome()

def get_currency_symbol(currency_code):
    """Return currency symbol for display purposes"""
    symbols = {
        "USD": "$", 
        "EUR": "€", 
        "GBP": "£", 
        "JPY": "¥"
    }
    return symbols.get(currency_code, currency_code)

def handle_search(location, check_in, check_out, adults, rooms, currency):
    """Handle search logic with location resolution and better UX"""
    # Show search summary
    nights = (check_out - check_in).days
    st.markdown(f"""
    <div style="background-color: white; padding: 15px; border-radius: 10px; 
    margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
        <div style="font-size: 1.2rem; font-weight: 600; color: #1e3a8a; margin-bottom: 5px;">
            Your Search
        </div>
        <div style="color: #4b5563;">
            <span style="font-weight: 500;">{location}</span> • 
            {check_in.strftime('%b %d')} - {check_out.strftime('%b %d')} • 
            {nights} night{'s' if nights > 1 else ''} • 
            {adults} adult{'s' if adults > 1 else ''} • 
            {rooms} room{'s' if rooms > 1 else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    coords = get_coordinates(location)
    if not coords:
        st.error("🚫 We couldn't find that location. Please try another destination.")
        return
    
    lat, lon = coords
    params = {
        "latitude": lat,
        "longitude": lon,
        "arrival_date": check_in.strftime("%Y-%m-%d"),
        "departure_date": check_out.strftime("%Y-%m-%d"),
        "adults": adults,
        "room_qty": rooms,
        "currency_code": currency,
        "radius": 10
    }
    
    with st.status("Searching for the best hotels...", expanded=True) as status:
        st.write("Finding available properties...")
        hotels = search_hotels(params)
        if hotels:
            status.update(label="✅ Search complete!", state="complete", expanded=False)
            display_results(hotels)
        else:
            status.update(label="No hotels found", state="error", expanded=True)
            st.warning("😔 We couldn't find any hotels matching your criteria. Try adjusting your search parameters.")

def display_results(hotels):
    """Display search results with modern UI"""
    # Results header with count and sorting options
    st.markdown(f"""
    <div class="results-header">
        <div style="font-size: 1.2rem; font-weight: 600; color: #1e3a8a;">
            Found {len(hotels)} Properties
        </div>
        <div>
            <span style="color: #6b7280; margin-right: 10px;">Sort by:</span>
            <select style="padding: 5px 10px; border-radius: 6px; border: 1px solid #d1d5db;">
                <option>Recommended</option>
                <option>Price: Low to High</option>
                <option>Price: High to Low</option>
                <option>Rating: High to Low</option>
            </select>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display each hotel card
    for hotel in hotels:
        hotel_card(hotel)

def display_welcome():
    """Display welcome screen with featured destinations"""
    st.markdown("""
    <div style="text-align: center; padding: 30px 0; margin-bottom: 20px;">
        <h1 style="font-size: 2.5rem; color: #1e3a8a; margin-bottom: 15px;">
            Find Your Perfect Stay
        </h1>
        <p style="font-size: 1.2rem; color: #6b7280; margin-bottom: 30px; max-width: 700px; margin-left: auto; margin-right: auto;">
            Search hotels worldwide. Compare prices and find the best deals on top-rated accommodations.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Featured destinations section
    st.markdown("<h2 style='font-size: 1.5rem; margin-bottom: 20px;'>✨ Popular Destinations</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    destinations = [
        {"name": "Paris", "image": "https://media-cdn.tripadvisor.com/media/photo-c/1280x250/17/15/6d/d6/paris.jpg", "hotels": "2,500+"},
        {"name": "New York", "image": "https://fullsuitcase.com/wp-content/uploads/2022/05/One-day-in-New-York-USA-NYC-day-trip-itinerary.jpg", "hotels": "3,200+"},
        {"name": "Tokyo", "image": "https://img.static-kl.com/images/media/216337E7-BFE5-4AA6-9C9E180C3E5AC6A2", "hotels": "1,800+"},
    ]
    
    cols = [col1, col2, col3]
    
    for i, dest in enumerate(destinations):
        with cols[i]:
            st.markdown(f"""
            <div style="background-color: white; border-radius: 12px; overflow: hidden; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.1); transition: transform 0.2s;">
                <img src="{dest['image']}" style="width: 100%; height: 150px; object-fit: cover;">
                <div style="padding: 15px;">
                    <div style="font-weight: 700; font-size: 1.2rem; margin-bottom: 5px;">
                        {dest['name']}
                    </div>
                    <div style="color: #6b7280; font-size: 0.9rem;">
                        {dest['hotels']} hotels
                    </div>
                </div>v
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()