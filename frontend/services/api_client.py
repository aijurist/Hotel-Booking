import requests
from typing import Optional
import streamlit as st

def search_hotels(params: dict) -> Optional[list]:
    """Fetch hotels from backend API with precise coordinates"""
    try:
        # Ensure float precision
        params['latitude'] = f"{params['latitude']:.8f}"
        params['longitude'] = f"{params['longitude']:.8f}"
        
        response = requests.get(
            "http://localhost:8000/api/hotels/search",
            params=params
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None