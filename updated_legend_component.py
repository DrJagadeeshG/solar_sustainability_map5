import streamlit as st

def get_category_colors(category):
    """
    Returns the color mapping for map styling based on category
    Updated to work with the new ranking system: Very High, High, Moderate, Low, Very Low, No Data
    Color scheme: Red (Very Low) -> Orange (Low) -> Yellow (Moderate) -> Light Blue (High) -> Dark Blue (Very High)
    """
    color_mappings = {
        "Adapt": {
            "Very Low": "#FF1744",      # Red A400
            "Low": "#FF5722",           # Deep Orange 500
            "Moderate": "#FF9800",      # Orange 500
            "High": "#2196F3",          # Blue 500
            "Very High": "#0D47A1",     # Blue 900
            "No Data": "#757575",       # Grey 600
        },
        
        "Mitigate": {
            "Very Low": "#FF1744",      # Red A400
            "Low": "#FF5722",           # Deep Orange 500
            "Moderate": "#FF9800",      # Orange 500
            "High": "#2196F3",          # Blue 500
            "Very High": "#0D47A1",     # Blue 900
            "No Data": "#757575",       # Grey 600
        },
        
        "Replace": {
            "Very Low": "#FF1744",      # Red A400
            "Low": "#FF5722",           # Deep Orange 500
            "Moderate": "#FF9800",      # Orange 500
            "High": "#2196F3",          # Blue 500
            "Very High": "#0D47A1",     # Blue 900
            "No Data": "#757575",       # Grey 600
        },
        
        "General_SI": {
            "Adaptation": "#00ADB5",                                     # Teal
            "Mitigation": "#845EC2",                                     # Purple
            "Replacement": "#F9B872",                                    # Orange
            "Adaptation + Mitigation": "#00BFA5",                        # Teal A700
            "Adaptation + Replacement": "#FF6D00",                       # Orange A700
            "Mitigation + Replacement": "#7C4DFF",                       # Deep Purple A200
            "Adaptation + Mitigation + Replacement": "#2E7D32",          # Green 800
            "No Data": "#757575",                                        # Grey 600
        }
    }
    
    return color_mappings.get(category, {})

def get_ranking_order():
    """
    Returns the order of rankings from worst to best for sorting
    """
    return ["Very Low", "Low", "Moderate", "High", "Very High", "No Data"]

def get_ranking_color_gradient():
    """
    Returns a color gradient that can be used for consistent coloring across the app
    """
    return {
        "Very Low": "#FF1744",      # Red A400
        "Low": "#FF5722",           # Deep Orange 500
        "Moderate": "#FF9800",      # Orange 500
        "High": "#2196F3",          # Blue 500
        "Very High": "#0D47A1",     # Blue 900
        "No Data": "#757575",       # Grey 600
    }