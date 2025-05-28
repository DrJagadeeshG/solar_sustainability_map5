import streamlit as st

def get_category_colors(category):
    """
    Returns the color mapping for map styling based on category
    Updated to work with the new ranking system: Very High, High, Moderate, Low, Very Low, No Data
    Color scheme: Red (Very Low) -> Orange (Low) -> Yellow (Moderate) -> Light Blue (High) -> Dark Blue (Very High)
    """
    color_mappings = {
        "Adapt": {
            "Very High": "#0D47A1",     # Blue 900
            "High": "#2196F3",          # Blue 500
            "Moderate": "#FF9800",      # Orange 500
            "Low": "#FF5722",           # Deep Orange 500
            "Very Low": "#FF1744",      # Red A400
            "No Data": "#757575",       # Grey 600
        },
        
        "Mitigate": {
            "Very High": "#0D47A1",     # Blue 900
            "High": "#2196F3",          # Blue 500
            "Moderate": "#FF9800",      # Orange 500
            "Low": "#FF5722",           # Deep Orange 500
            "Very Low": "#FF1744",      # Red A400
            "No Data": "#757575",       # Grey 600
        },
        
        "Replace": {
            "Very High": "#0D47A1",     # Blue 900
            "High": "#2196F3",          # Blue 500
            "Moderate": "#FF9800",      # Orange 500
            "Low": "#FF5722",           # Deep Orange 500
            "Very Low": "#FF1744",      # Red A400
            "No Data": "#757575",       # Grey 600
        },
        
        "General_SI": {
            "Adaptation": "#1E88E5",                                     # Blue 600
            "Mitigation": "#8E24AA",                                     # Purple 600
            "GW Sustainability": "#43A047",                              # Green 600
            "Adaptation + Mitigation": "#FF6F00",                        # Orange A700
            "Adaptation + GW Sustainability": "#D32F2F",                 # Red 700
            "Mitigation + GW Sustainability": "#8D6E63",                 # Brown 400 (distinct from orange)
            "Combined": "#6A1B9A",                                       # Purple 800
            "All": "#00BCD4",                                            # Cyan 500 (bright and distinct)
            "No Data": "#757575",                                        # Grey 600
        }
    }
    
    return color_mappings.get(category, {})

def get_ranking_order():
    """
    Returns the order of rankings from best to worst for sorting (Very High to Very Low)
    """
    return ["Very High", "High", "Moderate", "Low", "Very Low", "No Data"]

def get_combined_order():
    """
    Returns the preferred order for Combined category items
    """
    return [
        "Adaptation", 
        "Mitigation", 
        "GW Sustainability", 
        "Adaptation + Mitigation", 
        "Adaptation + GW Sustainability", 
        "Mitigation + GW Sustainability", 
        "Combined",
        "All",
        "No Data"
    ]

def get_ranking_color_gradient():
    """
    Returns a color gradient that can be used for consistent coloring across the app
    """
    return {
        "Very High": "#0D47A1",     # Blue 900
        "High": "#2196F3",          # Blue 500
        "Moderate": "#FF9800",      # Orange 500
        "Low": "#FF5722",           # Deep Orange 500
        "Very Low": "#FF1744",      # Red A400
        "No Data": "#757575",       # Grey 600
    }