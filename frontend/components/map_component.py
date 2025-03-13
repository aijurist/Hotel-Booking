import folium

def create_map(hotel):
    """Create an interactive map with the hotel location"""
    if 'longitude' in hotel and 'latitude' in hotel:
        # Create a map centered on the hotel
        m = folium.Map(
            location=[hotel['latitude'], hotel['longitude']], 
            zoom_start=15,
            tiles='CartoDB positron'
        )
        
        # Add a marker for the hotel
        tooltip = f"{hotel['hotel_name']} ({hotel.get('review_score', 'N/A')}/10)"
        folium.Marker(
            [hotel['latitude'], hotel['longitude']],
            popup=f"<strong>{hotel['hotel_name']}</strong><br>{hotel.get('address', '')}",
            tooltip=tooltip,
            icon=folium.Icon(color='blue', icon='hotel', prefix='fa')
        ).add_to(m)
        
        # Add a circle to highlight the area
        folium.Circle(
            radius=300,
            location=[hotel['latitude'], hotel['longitude']],
            color='#3b82f6',
            fill=True,
            fill_color='#3b82f6',
            fill_opacity=0.1
        ).add_to(m)
        
        return m
    return None