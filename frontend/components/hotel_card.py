import streamlit as st
from components.hotel_details import display_hotel_details

def hotel_card(hotel: dict):
    """Display a modern card for a hotel with expandable details."""
    # Initialize session state for expanded hotels if not present
    if 'expanded_hotels' not in st.session_state:
        st.session_state.expanded_hotels = []

    # Generate a unique card ID
    card_id = f"hotel_{hotel['hotel_id']}"
    
    with st.container():
        with st.container(border=True):
            # Main content area with image and summary
            cols = st.columns([1, 2])
            
            # Left column - Image
            with cols[0]:
                if hotel.get('main_photo_url'):
                    st.image(
                        hotel.get('main_photo_url', 'https://via.placeholder.com/300x200'),
                        use_container_width=True,
                        output_format="JPEG",
                        caption=None
                    )
                else:
                    st.image(
                        "https://via.placeholder.com/300x200?text=No+Image",
                        use_container_width=True
                    )
            
            # Right column - Hotel info
            with cols[1]:
                # Hotel name and rating
                name_rating_col1, name_rating_col2 = st.columns([3, 1])
                with name_rating_col1:
                    st.markdown(f"### {hotel['hotel_name']}")
                with name_rating_col2:
                    if hotel.get('review_score'):
                        rating_color = ""
                        score = float(hotel.get('review_score', 0))
                        if score >= 9.0:
                            rating_color = "background-color: #10b981; color: white;"
                        elif score >= 8.0:
                            rating_color = "background-color: #3b82f6; color: white;"
                        elif score >= 7.0:
                            rating_color = "background-color: #6366f1; color: white;"
                        else:
                            rating_color = "background-color: #f59e0b; color: white;"
                            
                        st.markdown(
                            f"""<div style="text-align: right;">
                                <span style="display: inline-block; {rating_color} padding: 5px 10px; 
                                border-radius: 20px; font-weight: bold; text-align: center;">
                                {hotel.get('review_score', 'N/A')}/10
                                </span>
                            </div>""", 
                            unsafe_allow_html=True
                        )
                
                # Location and reviews
                st.markdown(
                    f"""<span style="color: #6b7280;">
                        <i class="fas fa-map-marker-alt"></i> {hotel.get('city', 'N/A')}, {hotel.get('countrycode', 'N/A')} 
                        | {hotel.get('review_nr', 0)} reviews
                    </span>""", 
                    unsafe_allow_html=True
                )
                
                # Badges if any
                if hotel.get('badges'):
                    badges_html = ""
                    for badge in hotel['badges'][:2]:  # Limit to 2 badges for cleaner UI
                        badges_html += f"""<span class="hotel-badge" style="background-color: #ecf4ff; color: #3b82f6; padding: 5px 10px; border-radius: 20px; margin: 2px;">{badge['text']}</span>"""
                    st.markdown(badges_html, unsafe_allow_html=True)
                
                # Free cancellation badge if applicable
                if hotel.get('is_free_cancellable'):
                    st.markdown(
                        """<span style="display: inline-block; background-color: #ecfdf5; 
                        color: #10b981; padding: 5px 10px; border-radius: 20px; 
                        font-size: 0.8rem; font-weight: 600; margin-top: 5px;">
                        ✓ Free Cancellation
                        </span>""", 
                        unsafe_allow_html=True
                    )
                
                # Price information
                price_col1, price_col2 = st.columns([3, 1])
                with price_col2:
                    st.markdown(
                        f"""<div style="text-align: right; margin-top: 5px;">
                            <div class="price-tag" style="font-weight: bold; font-size: 1.2rem;">
                                {hotel['currencycode']} {hotel['min_total_price']:.2f}
                            </div>
                        </div>""", 
                        unsafe_allow_html=True
                    )
                
                # Action buttons
                action_col1, action_col2, action_col3 = st.columns(3)
                
                with action_col1:
                    # Booking button (HTML with JavaScript, no rerun)
                    st.markdown(
                        f"""
                        <button onclick="window.open('{hotel.get('booking_url', '#')}', '_blank')" 
                        style="width:100%; padding:8px; background-color:#1E88E5; color:white; 
                        border:none; border-radius:4px; cursor:pointer;">
                            📖 Book Now
                        </button>
                        """,
                        unsafe_allow_html=True
                    )
                
                with action_col2:
                    # Share button (HTML with JavaScript, no rerun)
                    st.markdown(
                        f"""
                        <button onclick="navigator.clipboard.writeText(window.location.href); 
                        const toast = document.createElement('div'); 
                        toast.innerHTML = '🔗 Link copied to clipboard!'; 
                        toast.style.position = 'fixed'; 
                        toast.style.bottom = '20px'; 
                        toast.style.left = '50%'; 
                        toast.style.transform = 'translateX(-50%)'; 
                        toast.style.backgroundColor = '#333'; 
                        toast.style.color = 'white'; 
                        toast.style.padding = '10px 20px'; 
                        toast.style.borderRadius = '5px'; 
                        toast.style.zIndex = '1000'; 
                        document.body.appendChild(toast); 
                        setTimeout(() => toast.remove(), 3000);" 
                        style="width:100%; padding:8px; background-color:#4CAF50; color:white; 
                        border:none; border-radius:4px; cursor:pointer;">
                            🔗 Share
                        </button>
                        """,
                        unsafe_allow_html=True
                    )
                
                with action_col3:
                    # Details toggle button using Streamlit with state management
                    is_expanded = hotel['hotel_id'] in st.session_state.expanded_hotels
                    button_label = "🔼 Hide Details" if is_expanded else "🔽 View Details"
                    if st.button(button_label, key=f"details_{card_id}"):
                        if is_expanded:
                            st.session_state.expanded_hotels = [h for h in st.session_state.expanded_hotels if h != hotel['hotel_id']]
                        else:
                            st.session_state.expanded_hotels.append(hotel['hotel_id'])
        
        # Display details if expanded
        if hotel['hotel_id'] in st.session_state.expanded_hotels:
            with st.container(border=True):
                display_hotel_details(hotel)