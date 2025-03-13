import streamlit as st
from components.map_component import create_map
from streamlit_folium import folium_static

def display_hotel_details(hotel):
    """Display detailed information for a selected hotel with enhanced UI"""
    # Create a tabbed interface for better organization of details
    tabs = st.tabs(["Overview", "Amenities", "Price Details", "Location"])
    
    # Tab 1: Overview
    with tabs[0]:
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Main image with enhanced styling
            if hotel.get('main_photo_url'):
                st.image(
                    hotel.get('main_photo_url'), 
                    use_container_width=True,
                    caption=f"{hotel['hotel_name']} - {hotel.get('city', '')}"
                )
            else:
                st.info("No image available for this property")
            
            # Hotel description with better formatting
            st.markdown("### About this property")
            description = hotel.get('description', 'No description available for this hotel.')
            st.markdown(f"""
            <div style="background-color: #f8fafc; padding: 15px; border-radius: 8px; 
            border-left: 4px solid #1d4ed8; margin: 10px 0;">
                {description}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Key details card with enhanced styling
            st.markdown("""
            <h3 style="margin-top: 0; border-bottom: 2px solid #e5e7eb; 
            padding-bottom: 8px; color: #1e3a8a;">Property Details</h3>
            """, unsafe_allow_html=True)
            
            details_html = f"""
            <div style="background-color: #f8fafc; border-radius: 10px; 
            padding: 15px; margin-bottom: 15px;">
                <div style="margin-bottom: 12px; display: flex; align-items: center;">
                    <span style="width: 24px; margin-right: 10px; color: #1d4ed8;">📍</span>
                    <div>
                        <div style="font-weight: 600; color: #1e293b;">Location</div>
                        <div style="color: #475569;">{hotel.get('city', 'N/A')}, {hotel.get('countrycode', 'N/A')}</div>
                    </div>
                </div>
                
                <div style="margin-bottom: 12px; display: flex; align-items: center;">
                    <span style="width: 24px; margin-right: 10px; color: #1d4ed8;">🏢</span>
                    <div>
                        <div style="font-weight: 600; color: #1e293b;">Property Type</div>
                        <div style="color: #475569;">{hotel.get('accommodation_type', 'Hotel')}</div>
                    </div>
                </div>
                
                <div style="margin-bottom: 12px; display: flex; align-items: center;">
                    <span style="width: 24px; margin-right: 10px; color: #1d4ed8;">⭐</span>
                    <div>
                        <div style="font-weight: 600; color: #1e293b;">Rating</div>
                        <div style="color: #475569;">{hotel.get('review_score', 'N/A')}/10 from {hotel.get('review_nr', '0')} reviews</div>
                    </div>
                </div>
                
                <div style="display: flex; align-items: center;">
                    <span style="width: 24px; margin-right: 10px; color: #1d4ed8;">🕒</span>
                    <div>
                        <div style="font-weight: 600; color: #1e293b;">Timezone</div>
                        <div style="color: #475569;">{hotel.get('timezone', 'N/A')}</div>
                    </div>
                </div>
            </div>
            """
            st.markdown(details_html, unsafe_allow_html=True)
            
            # Call to action - book now
            if hotel.get('booking_url'):
                st.markdown(f"""
                <a href="{hotel.get('booking_url')}" target="_blank" style="display: block; 
                text-decoration: none; text-align: center; background-color: #1d4ed8; 
                color: white; padding: 12px; border-radius: 8px; font-weight: 600; 
                margin: 15px 0; transition: all 0.2s ease;">
                    🔖 Book This Room Now
                </a>
                """, unsafe_allow_html=True)
    
    # Tab 2: Amenities
    with tabs[1]:
        st.markdown("""
        <h3 style="margin-top: 0; border-bottom: 2px solid #e5e7eb; 
        padding-bottom: 8px; color: #1e3a8a;">🛎️ Property Amenities</h3>
        """, unsafe_allow_html=True)
        
        # Group amenities by category for better organization
        amenity_categories = {
            "Essential": [
                ("WiFi", True, "✓ Free WiFi available throughout the property"),
                ("Breakfast", hotel.get('includes_breakfast', False), "✓ Breakfast included in room rate"),
                ("Air Conditioning", hotel.get('has_ac', True), "✓ Air conditioning in all rooms")
            ],
            "Facilities": [
                ("Swimming Pool", hotel.get('has_pool', False), "✓ Swimming pool available"),
                ("Parking", hotel.get('free_parking', False), "✓ Free parking on premises"),
                ("Fitness Center", hotel.get('has_gym', False), "✓ Fitness center access included")
            ],
            "Policies": [
                ("Free Cancellation", hotel.get('is_free_cancellable', False), "✓ Free cancellation available"),
                ("Pets", hotel.get('allows_pets', False), "✓ Pet friendly accommodation"),
                ("Children", hotel.get('children_allowed', True), "✓ Children welcome")
            ]
        }
        
        # Display amenities in a more organized, visual way
        col1, col2 = st.columns(2)
        
        for i, (category, amenities) in enumerate(amenity_categories.items()):
            with col1 if i % 2 == 0 else col2:
                st.markdown(f"""
                <div style="background-color: #f8fafc; border-radius: 10px; 
                padding: 15px; margin-bottom: 15px;">
                    <div style="font-weight: 600; font-size: 1.1rem; 
                    color: #1e3a8a; margin-bottom: 10px; border-bottom: 1px solid #e5e7eb; 
                    padding-bottom: 5px;">
                        {category}
                    </div>
                """, unsafe_allow_html=True)
                
                for name, available, description in amenities:
                    if available:
                        st.markdown(f"""
                        <div style="margin-bottom: 8px; display: flex; align-items: center;">
                            <span style="min-width: 24px; display: inline-block; 
                            color: #059669; margin-right: 8px;">✓</span>
                            <span style="color: #1e293b;">{description.replace("✓ ", "")}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="margin-bottom: 8px; display: flex; align-items: center; opacity: 0.5;">
                            <span style="min-width: 24px; display: inline-block; 
                            color: #6b7280; margin-right: 8px;">✗</span>
                            <span style="color: #6b7280;">{name} not available</span>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
    
    # Tab 3: Price Details
    with tabs[2]:
        st.markdown("""
        <h3 style="margin-top: 0; border-bottom: 2px solid #e5e7eb; 
        padding-bottom: 8px; color: #1e3a8a;">💰 Price Breakdown</h3>
        """, unsafe_allow_html=True)
        
        # Enhanced price breakdown display
        if 'composite_price_breakdown' in hotel:
            breakdown = hotel['composite_price_breakdown']
            
            # Calculate savings if available
            savings = None
            savings_percent = None
            
            if (breakdown.get('strikethrough_amount') and 
                breakdown.get('gross_amount') and
                'value' in breakdown['strikethrough_amount'] and
                'value' in breakdown['gross_amount']):
                
                original = breakdown['strikethrough_amount']['value']
                current = breakdown['gross_amount']['value']
                savings = original - current
                if original > 0:
                    savings_percent = (savings / original) * 100
            
            # Create a visual price breakdown card
            st.markdown(f"""
            <div style="background-color: #f8fafc; border-radius: 10px; 
            padding: 20px; margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; 
                align-items: center; margin-bottom: 15px;">
                    <div style="font-weight: 600; font-size: 1.1rem; color: #1e293b;">
                        Room Price
                    </div>
                    <div>
            """, unsafe_allow_html=True)
            
            # Price display with potential discounts
            if savings and savings > 0:
                st.markdown(f"""
                        <div style="text-align: right;">
                            <div style="text-decoration: line-through; color: #6b7280;">
                                {breakdown['strikethrough_amount'].get('amount_rounded', 'N/A')}
                            </div>
                            <div style="font-weight: 700; font-size: 1.4rem; color: #059669;">
                                {breakdown['gross_amount'].get('amount_rounded', 'N/A')}
                            </div>
                            <div style="color: #be123c; font-weight: 600; font-size: 0.9rem;">
                                Save {savings_percent:.0f}% ({breakdown['strikethrough_amount']['currency']} {savings:.2f})
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                        <div style="text-align: right;">
                            <div style="font-weight: 700; font-size: 1.4rem; color: #1e3a8a;">
                                {breakdown.get('gross_amount', {}).get('amount_rounded', 'N/A')}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Show detailed breakdown of costs
            st.markdown(f"""
                <div style="margin-top: 15px;">
                    <div style="border-top: 1px solid #e5e7eb; padding-top: 15px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <div style="color: #475569;">Room rate</div>
                            <div style="font-weight: 500; color: #1e293b;">
                                {breakdown.get('base_amount', {}).get('amount_rounded', 'N/A')}
                            </div>
                        </div>
            """, unsafe_allow_html=True)
            
            # Show taxes and fees if available
            if breakdown.get('excluded_amount'):
                st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <div style="color: #475569;">Taxes & fees</div>
                            <div style="font-weight: 500; color: #1e293b;">
                                {breakdown.get('excluded_amount', {}).get('amount_rounded', 'N/A')}
                            </div>
                        </div>
                """, unsafe_allow_html=True)
            
            # Show any discounts if applicable
            if breakdown.get('benefit'):
                for benefit in breakdown.get('benefit', []):
                    if benefit.get('name') and benefit.get('amount'):
                        st.markdown(f"""
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <div style="color: #059669;">
                                    {benefit.get('name')}
                                </div>
                                <div style="font-weight: 500; color: #059669;">
                                    - {benefit.get('amount', {}).get('amount_rounded', 'N/A')}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
            
            st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; 
                        border-top: 1px solid #e5e7eb; padding-top: 10px; margin-top: 10px;">
                            <div style="font-weight: 600; color: #1e293b;">Total price</div>
                            <div style="font-weight: 700; color: #1e3a8a;">
                                {breakdown.get('all_inclusive_amount', {}).get('amount_rounded', 'N/A')}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Payment options and info
            st.markdown("""
            <div style="background-color: #ecfdf5; border-radius: 8px; padding: 15px;">
                <div style="font-weight: 600; color: #059669; margin-bottom: 8px;">
                    💳 Payment Information
                </div>
                <ul style="margin: 0; padding-left: 20px; color: #065f46;">
                    <li>Pay now or at the property</li>
                    <li>Major credit cards accepted</li>
                    <li>Secure payment processing</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Detailed price information is not available for this property.")
    
    # Tab 4: Location
    with tabs[3]:
        st.markdown("""
        <h3 style="margin-top: 0; border-bottom: 2px solid #e5e7eb; 
        padding-bottom: 8px; color: #1e3a8a;">📍 Location</h3>
        """, unsafe_allow_html=True)
        
        # Location details
        loc_col1, loc_col2 = st.columns([2, 1])
        
        with loc_col1:
            # Map display
            m = create_map(hotel)
            if m:
                folium_static(m, height=300)
            else:
                st.info("Map location not available for this hotel.")
        
        with loc_col2:
            # Location highlights
            st.markdown("""
            <div style="background-color: #f8fafc; border-radius: 10px; 
            padding: 15px; height: 100%;">
                <div style="font-weight: 600; font-size: 1.1rem; 
                color: #1e3a8a; margin-bottom: 10px; border-bottom: 1px solid #e5e7eb; 
                padding-bottom: 5px;">
                    Nearby Attractions
                </div>
            """, unsafe_allow_html=True)
            
            # We can add some dummy nearby attractions or use real data if available
            attractions = [
                ("City Center", "1.2 km"),
                ("Main Station", "0.8 km"),
                ("Shopping District", "1.5 km"),
                ("Airport", f"{hotel.get('distance_to_airport', 15)} km")
            ]
            
            for attraction, distance in attractions:
                st.markdown(f"""
                <div style="margin-bottom: 8px; display: flex; justify-content: space-between;">
                    <div style="color: #1e293b;">{attraction}</div>
                    <div style="color: #6b7280; font-weight: 500;">{distance}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Bottom action buttons
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    action_cols = st.columns([1, 1, 1])
    
    with action_cols[0]:
        if hotel.get('booking_url'):
            st.link_button("📖 Book Now", hotel['booking_url'], use_container_width=True, type="primary")
        else:
            st.button("📖 Book Now", key=f"book_detail_{hotel.get('hotel_id', 'unknown')}", use_container_width=True, type="primary")
    
    with action_cols[1]:
        st.button("📱 Contact Hotel", key=f"call_detail_{hotel.get('hotel_id', 'unknown')}", use_container_width=True)
    
    with action_cols[2]:
        st.button("❤️ Save to Favorites", key=f"save_detail_{hotel.get('hotel_id', 'unknown')}", use_container_width=True)