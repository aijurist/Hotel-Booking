import streamlit as st
from streamlit_folium import folium_static
from components.map_component import create_map
import pandas as pd
from datetime import datetime
import pytz

def hotel_card(hotel):
    """
    Display a hotel card with tabbed information sections
    
    Args:
        hotel (dict): Hotel information dictionary from API
    """
    # Extract key information
    hotel_name = hotel.get('hotel_name', 'Hotel Name Not Available')
    price = hotel.get('min_total_price', 0)
    currency = hotel.get('currencycode', 'USD')
    review_score = hotel.get('review_score')
    review_score = 'N/A' if review_score is None else review_score
    review_count = hotel.get('review_nr', 0)
    review_word = hotel.get('review_score_word', '')
    city = hotel.get('city', 'Unknown City')
    country = hotel.get('countrycode', '')
    is_free_cancellable = hotel.get('is_free_cancellable', False)
    timezone = hotel.get('timezone', 'UTC')
    tz = pytz.timezone(timezone)
    current_time = datetime.now(tz).strftime("%H:%M")
    
    price_details = {}
    if 'composite_price_breakdown' in hotel and hotel['composite_price_breakdown'] is not None:
        breakdown = hotel['composite_price_breakdown']
        price_details = {
            'base_price': breakdown.get('net_amount', {}).get('amount_rounded', f"{currency} {price}"),
            'taxes_fees': breakdown.get('excluded_amount', {}).get('amount_rounded', f"{currency} 0"),
            'total_price': breakdown.get('all_inclusive_amount', {}).get('amount_rounded', f"{currency} {price}"),
            'items': breakdown.get('items', []),
        }
        
        strikethrough = breakdown.get('strikethrough_amount')
        if strikethrough is not None and isinstance(strikethrough, dict):
            price_details['original_price'] = strikethrough.get('amount_rounded', '')
        else:
            price_details['original_price'] = ''
    
    with st.container():
        st.markdown("""
        <div style="border-bottom: 1px solid #e5e7eb; margin: 30px 0;"></div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 2])
        
        with col1:
            if 'main_photo_url' in hotel:
                st.image(hotel['main_photo_url'], use_container_width=True)
            else:
                st.markdown("""
                <div style="background-color: #e5e7eb; height: 180px; border-radius: 8px; 
                display: flex; align-items: center; justify-content: center;">
                    <div style="color: #9ca3af; font-weight: 500;">No Image Available</div>
                </div>
                """, unsafe_allow_html=True)
                
        with col2:
            st.markdown(f"### {hotel_name}")
            
            # Location and rating in one line
            st.markdown(f"📍 {city}, {country} | {'⭐' * (int(review_score)//2 if isinstance(review_score, (int, float)) else 0)}")
            
            # Review score
            if review_score != 'N/A':
                score_color = "#166534" if float(review_score) >= 8 else "#ca8a04" if float(review_score) >= 6 else "#b91c1c"
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="background-color: {score_color}; color: white; padding: 4px 8px; 
                    border-radius: 4px; font-weight: 600; margin-right: 8px;">
                        {review_score}
                    </div>
                    <div>
                        <span style="font-weight: 500;">{review_word}</span>
                        <span style="color: #6b7280; margin-left: 5px;">({review_count} reviews)</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            # Price display with possible discount
            if price_details.get('original_price'):
                st.markdown(f"""
                <div style="margin-top: 15px;">
                    <div style="display: flex; align-items: baseline;">
                        <span style="text-decoration: line-through; color: #6b7280; margin-right: 8px;">
                            {price_details['original_price']}
                        </span>
                        <span style="font-size: 1.4rem; font-weight: 700; color: #1e3a8a;">
                            {price_details['base_price']}
                        </span>
                    </div>
                    <div style="color: #6b7280; font-size: 0.9rem;">
                        excludes taxes & fees
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="margin-top: 15px;">
                    <div style="font-size: 1.4rem; font-weight: 700; color: #1e3a8a;">
                        {currency} {price:.2f}
                    </div>
                    <div style="color: #6b7280; font-size: 0.9rem;">
                        excludes taxes & fees
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Badges section
            if hotel.get('badges'):
                st.markdown("<div style='margin-top: 10px; display: flex; gap: 8px; flex-wrap: wrap;'>", unsafe_allow_html=True)
                for badge in hotel['badges']:
                    badge_color = "#059669" if badge.get('badge_variant') == "constructive" else "#2563eb"
                    st.markdown(f"""
                    <div style="background-color: {badge_color}; color: white; font-size: 0.8rem;
                    padding: 2px 8px; border-radius: 4px; display: inline-block;">
                        {badge.get('text', '')}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Add free cancellation badge if available
                if is_free_cancellable:
                    st.markdown(f"""
                    <div style="background-color: #16a34a; color: white; font-size: 0.8rem;
                    padding: 2px 8px; border-radius: 4px; display: inline-block;">
                        Free Cancellation
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
        # Create tabs for hotel details
        tabs = st.tabs(["Overview", "Amenities", "Price Details", "Location"])
        
        # Overview tab
        with tabs[0]:
            # Create a function to map accommodation type IDs to labels
            def accommodation_type_label(type_id):
                mapping = {
                    201: "Apartment",
                    204: "Hotel",
                    203: "Resort",
                    202: "Guesthouse",
                    205: "Hostel",
                    208: "Villa",
                    211: "Vacation Home"
                }
                return mapping.get(type_id, "Accommodation")
            
            st.markdown(f"""
            <div style="background-color: #f9fafb; padding: 15px; border-radius: 8px;">
                <h4 style="margin-bottom: 10px;">Hotel Overview</h4>
                <p>
                    This modern accommodation offers comfortable rooms in a convenient location.
                    Perfect for both business and leisure travelers looking for quality accommodations.
                </p>
                <div style="margin-top: 15px;">
                    <div style="font-weight: 600; margin-bottom: 8px;">Quick Facts</div>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                        <div style="background-color: white; padding: 8px 12px; border-radius: 6px; font-size: 0.9rem;">
                            <span style="color: #4b5563;">Check-in:</span> After 2:00 PM
                        </div>
                        <div style="background-color: white; padding: 8px 12px; border-radius: 6px; font-size: 0.9rem;">
                            <span style="color: #4b5563;">Check-out:</span> Before 11:00 AM
                        </div>
                        <div style="background-color: white; padding: 8px 12px; border-radius: 6px; font-size: 0.9rem;">
                            <span style="color: #4b5563;">Type:</span> {accommodation_type_label(hotel.get('accommodation_type', 0))}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Amenities tab
        with tabs[1]:
            amenities = [
                {"icon": "wifi", "name": "Free WiFi", "category": "Connectivity"},
                {"icon": "car", "name": "Parking", "category": "Services"},
                {"icon": "snowflake", "name": "Air Conditioning", "category": "Comfort"},
                {"icon": "concierge-bell", "name": "24/7 Reception", "category": "Services"},
                {"icon": "wifi", "name": "Business Center", "category": "Services"},
            ]
            
            amenities_by_category = {}
            for amenity in amenities:
                category = amenity["category"]
                if category not in amenities_by_category:
                    amenities_by_category[category] = []
                amenities_by_category[category].append(amenity)
            
            st.markdown("""
                        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
            <style>
            .amenity-card {
                display: flex;
                align-items: center;
                padding: 12px;
                background-color: white;
                border-radius: 8px;
                margin-bottom: 8px;
                transition: all 0.2s ease;
                border: 1px solid #e5e7eb;
            }
            .amenity-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                border-color: #3b82f6;
            }
            .amenity-icon {
                background-color: #f0f9ff;
                color: #3b82f6;
                width: 36px;
                height: 36px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 12px;
                flex-shrink: 0;
            }
            .amenity-name {
                font-weight: 500;
                color: #1f2937;
            }
            .category-title {
                font-size: 1.1rem;
                font-weight: 600;
                color: #1e3a8a;
                margin: 16px 0 12px 0;
                border-bottom: 2px solid #e5e7eb;
                padding-bottom: 6px;
            }
            </style>
            """, unsafe_allow_html=True)
            
            for category, items in amenities_by_category.items():
                st.markdown(f"<div class='category-title'>{category}</div>", unsafe_allow_html=True)
                col_count = 2 
                rows = [items[i:i+col_count] for i in range(0, len(items), col_count)]
                
                for row in rows:
                    cols = st.columns(col_count)
                    for i, amenity in enumerate(row):
                        with cols[i]:
                            st.markdown(f"""
                            <div class="amenity-card">
                                <div class="amenity-icon">
                                    <i class="fas fa-{amenity['icon']}"></i>
                                </div>
                                <div class="amenity-name">{amenity['name']}</div>
                            </div>
                            """, unsafe_allow_html=True)
            
            # Add a note about amenities
            st.markdown("""
            <div style="margin-top: 20px; padding: 15px; background-color: #f3f4f6; border-radius: 8px; border-left: 4px solid #3b82f6;">
                <div style="font-weight: 600; margin-bottom: 5px; color: #1e3a8a;">Note about amenities</div>
                <p style="margin: 0; font-size: 0.9rem; color: #4b5563;">
                    Some amenities may be available for additional charges and subject to availability. 
                    Please contact the property directly for specific details.
                </p>
            </div>
            """, unsafe_allow_html=True)
        # Price Details tab
        with tabs[2]:
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.markdown("### Price Breakdown")
                
                price_items = []
                
                price_items.append({
                    "description": "Base rate",
                    "amount": price_details.get('base_price', f"{currency} {price:.2f}"),
                    "type": "base"
                })
                
                if price_details.get('items'):
                    for item in price_details['items']:
                        if item.get('kind') == 'charge' and item.get('inclusion_type') == 'excluded':
                            price_items.append({
                                "description": item.get('name', 'Fee'),
                                "amount": item.get('item_amount', {}).get('amount_rounded', f"{currency} 0"),
                                "type": "fee" 
                            })
                        elif item.get('kind') == 'discount':
                            price_items.append({
                                "description": item.get('name', 'Discount'),
                                "amount": f"-{item.get('item_amount', {}).get('amount_rounded', f'{currency} 0')}",
                                "type": "discount"
                            })
                
                price_items.append({
                    "description": "Total price",
                    "amount": price_details.get('total_price', f"{currency} {price:.2f}"),
                    "type": "total"
                })
                
                df = pd.DataFrame(price_items)
                
                st.markdown("""
                <style>
                .price-table th {
                    font-weight: 600;
                    text-align: left;
                    padding: 10px;
                    border-bottom: 1px solid #e5e7eb;
                }
                .price-table td {
                    padding: 10px;
                    border-bottom: 1px solid #e5e7eb;
                }
                .price-table tr:last-child {
                    font-weight: 700;
                    background-color: #f3f4f6;
                }
                .discount {
                    color: #16a34a;
                }
                </style>
                """, unsafe_allow_html=True)
                
                html_table = "<table class='price-table' style='width:100%;'>"
                html_table += "<tr><th>Description</th><th style='text-align:right;'>Amount</th></tr>"
                
                for _, row in df.iterrows():
                    class_name = "total" if row["type"] == "total" else "discount" if row["type"] == "discount" else ""
                    html_table += f"<tr class='{class_name}'><td>{row['description']}</td><td style='text-align:right;' class='{class_name}'>{row['amount']}</td></tr>"
                
                html_table += "</table>"
                
                st.markdown(html_table, unsafe_allow_html=True)
                
                # Payment policy
                st.markdown("""
                <div style="margin-top: 20px; padding: 15px; background-color: #f9fafb; border-radius: 8px;">
                    <div style="font-weight: 600; margin-bottom: 8px;">Payment Policy</div>
                    <ul style="margin: 0; padding-left: 20px; color: #4b5563;">
                        <li>Pay now or at the property depending on the rate selected</li>
                        <li>Taxes and fees are collected separately</li>
                        <li>Some rates require full prepayment</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style="margin-bottom: 15px; padding: 15px; background-color: #f0f9ff; border-left: 4px solid #3b82f6; border-radius: 0 8px 8px 0;">
                    <div style="font-weight: 600; margin-bottom: 8px;">Price Guarantee</div>
                    <p style="color: #4b5563; font-size: 0.9rem; margin: 0;">
                        If you find a lower price elsewhere, we'll match it and give you an additional 10% discount.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                if is_free_cancellable:
                    st.markdown("""
                    <div style="padding: 15px; background-color: #ecfdf5; border-left: 4px solid #10b981; border-radius: 0 8px 8px 0;">
                        <div style="font-weight: 600; margin-bottom: 8px; color: #065f46;">Free Cancellation</div>
                        <p style="color: #065f46; font-size: 0.9rem; margin: 0;">
                            You can cancel this booking free of charge up to 24 hours before check-in.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="padding: 15px; background-color: #fef2f2; border-left: 4px solid #ef4444; border-radius: 0 8px 8px 0;">
                        <div style="font-weight: 600; margin-bottom: 8px; color: #b91c1c;">Non-Refundable</div>
                        <p style="color: #b91c1c; font-size: 0.9rem; margin: 0;">
                            This booking cannot be cancelled or modified without charges.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

        # Location tab
        with tabs[3]:
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.markdown("### Hotel Location")
                
                if 'latitude' in hotel and 'longitude' in hotel:
                    m = create_map(hotel)
                    if m:
                        folium_static(m, width=450, height=300)
                else:
                    st.warning("Map location not available for this hotel.")
            
            with col2:
                st.markdown("### Nearby Attractions")
                
                # Sample nearby attractions
                attractions = [
                    {"name": "City Center", "distance": "1.2 km", "icon": "city"},
                    {"name": "Public Transport", "distance": "0.3 km", "icon": "bus"},
                    {"name": "Shopping Mall", "distance": "2.1 km", "icon": "shopping-bag"},
                    {"name": "Airport", "distance": "15.5 km", "icon": "plane"}
                ]
                
                for attraction in attractions:
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; padding: 10px; margin-bottom: 8px; 
                    background-color: #f9fafb; border-radius: 6px;">
                        <i class="fas fa-{attraction['icon']}" style="margin-right: 10px; color: #3b82f6;"></i>
                        <div>
                            <div style="font-weight: 500;">{attraction['name']}</div>
                            <div style="color: #6b7280; font-size: 0.8rem;">{attraction['distance']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Timezone information
                if 'timezone' in hotel:
                    st.markdown(f"""
                        <div style="margin-top: 20px; padding: 15px; background-color: #f0f9ff; border-radius: 8px;">
                            <div style="font-weight: 600; margin-bottom: 8px;">Local Time</div>
                            <div style="font-size: 1.2rem; font-weight: 500;">{current_time}</div>
                            <div style="color: #6b7280; font-size: 0.9rem;">{timezone}</div>
                        </div>
                        """, unsafe_allow_html=True)


        # Booking button at the bottom
        st.markdown("""
        <div style="margin-top: 20px; text-align: center;">
            <a href="#" style="display: inline-block; background-color: #1e40af; color: white; 
            padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; 
            font-size: 1.1rem;">
                Book Now
            </a>
        </div>
        """, unsafe_allow_html=True)
