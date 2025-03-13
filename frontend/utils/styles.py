# utils/styles.py
def load_styles():
    """Load custom CSS styles for a modern, sleek hotel booking platform"""
    return """
    <style>
    /* Global Styles */
    .main {
        padding: 0rem 1rem;
        background-color: #f8f9fa;
    }
    
    /* Hotel Card Styling */
    .hotel-card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 24px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
    }
    .hotel-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    }
    
    /* Hotel Image */
    .hotel-image {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .hotel-image:hover {
        transform: scale(1.02);
    }
    
    /* Hotel Details */
    .hotel-name {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1e3a8a;
        margin: 0;
        padding: 0;
    }
    
    /* Rating Style */
    .rating-badge {
        display: inline-flex;
        align-items: center;
        background-color: #fff8e1;
        color: #f59e0b;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 600;
        margin-right: 8px;
    }
    
    /* Price Styling */
    .price-tag {
        background-color: #ecfdf5;
        color: #10b981;
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.2rem;
        display: inline-block;
        margin-top: 10px;
    }
    
    /* Badge Styling */
    .hotel-badge {
        display: inline-block;
        background-color: #e0f2fe;
        color: #0ea5e9;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 8px;
    }
    
    /* Details Section */
    .details-section {
        background-color: #f9fafb;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Price Breakdown */
    .price-breakdown {
        font-size: 1.2rem;
        color: #10b981;
        font-weight: 600;
    }
    .discount-price {
        text-decoration: line-through;
        color: #9ca3af;
        margin-right: 10px;
    }
    .original-price {
        color: #10b981;
        font-weight: 700;
    }
    .taxes {
        font-size: 0.9rem;
        color: #6b7280;
    }
    
    /* Action Buttons */
    .action-button {
        width: 100%;
        padding: 10px 15px;
        border-radius: 8px;
        font-weight: 600;
        text-align: center;
        border: none;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        cursor: pointer;
    }

    .book-button {
        background-color: #1E88E5 !important;
        color: white !important;
    }

    .book-button:hover {
        background-color: #1565C0 !important;
        transform: translateY(-2px);
    }

    .share-button {
        background-color: #4CAF50 !important;
        color: white !important;
    }

    .share-button:hover {
        background-color: #388E3C !important;
        transform: translateY(-2px);
    }

    .details-button {
        background-color: #FF9800 !important;
        color: white !important;
    }

    .details-button:hover {
        background-color: #F57C00 !important;
        transform: translateY(-2px);
    }

    .book-button {
        background-color: #3b82f6 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 8px 20px !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3) !important;
    }
    .book-button:hover {
        background-color: #2563eb !important;
        box-shadow: 0 6px 8px rgba(59, 130, 246, 0.4) !important;
    }
    
    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background-color: white;
        padding: 20px 10px;
    }
    .sidebar h1 {
        color: #1e3a8a;
        font-size: 1.5rem;
        font-weight: 700;
    }
    .sidebar .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #3b82f6;
        color: white;
        font-weight: 600;
        padding: 10px 0;
        border: none;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3);
    }
    .sidebar .stButton>button:hover {
        background-color: #2563eb;
    }
    
    /* Search Results Header */
    .results-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        padding: 15px;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }
    </style>
    """