import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from streamlit_folium import folium_static
import os
import matplotlib.pyplot as plt
import numpy as np

# Helper for formatting values with units
def format_value_with_unit(value, unit):
    if (pd.isna(value) or 
        value is None or 
        str(value).strip() in ['', 'XX', 'N/A', 'nan', 'NaN', 'null', 'NULL', '#N/A', '-']):
        return "XX"
    
    try:
        if isinstance(value, (int, float)) and not pd.isna(value):
            return f"{value:.1f} {unit}".strip()
        else:
            str_val = str(value).strip()
            if str_val and str_val not in ['XX', 'N/A', 'nan', 'NaN', 'null', 'NULL', '#N/A', '-']:
                return f"{str_val} {unit}".strip() if unit else str_val
            else:
                return "XX"
    except:
        return "XX"

def is_valid_value(value):
    """Check if a value is valid (not N/A, blank, or other missing indicators)"""
    if pd.isna(value) or value is None:
        return False
    
    str_val = str(value).strip().lower()
    invalid_values = ['', 'xx', 'n/a', 'nan', 'null', '#n/a', '-', 'none', 'na']
    
    return str_val not in invalid_values

# Import the legend component for colors
try:
    from updated_legend_component import get_category_colors, get_ranking_color_gradient
except ImportError:
    def get_category_colors(category):
        return {}
    def get_ranking_color_gradient():
        return {}

# Set page configuration
st.set_page_config(
    page_title="Solar Suitability Dashboard",
    page_icon="☀️",
    layout="wide"
)

# Add professional styling
st.markdown("""
<style>
    /* Base styles */
    .main > div {
        padding: 1rem 2rem;
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Dashboard title */
    .dashboard-title {
        font-size: 2.2rem;
        color: #00ADB5;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        padding: 1rem;
        border-bottom: 2px solid #00ADB5;
    }
    
    /* Filter section */
    .filter-section {
        background-color: #1A1B1E;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border: 1px solid #2C2E33;
    }
    
    /* Section headers */
    .section-header {
        color: #00ADB5;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #00ADB5;
    }
    
    /* Status boxes */
    .status-box {
        padding: 0.8rem;
        border-radius: 6px;
        margin-bottom: 0.5rem;
        text-align: center;
        color: white;
    }
    
    .status-box.very-high {
        background-color: #0D47A1;
    }
    
    .status-box.high {
        background-color: #2196F3;
    }
    
    .status-box.moderate {
        background-color: #FF9800;
    }
    
    .status-box.low {
        background-color: #FF5722;
    }
    
    .status-box.very-low {
        background-color: #FF1744;
    }
    
    .status-box.no-data {
        background-color: #757575;
    }
    
    /* Metric containers */
    .metric-container {
        background-color: #1A1B1E;
        padding: 0.8rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        border: 1px solid #2C2E33;
    }
    
    /* Metric styling */
    .metric-name {
        color: #EEEEEE;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .metric-value {
        color: #00ADB5;
        font-weight: bold;
        font-size: 0.9rem;
        float: right;
    }
    
    /* Text boxes */
    .text-box {
        background-color: #1A1B1E;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #00ADB5;
        color: #EEEEEE;
    }
    
    /* Select box styling */
    .stSelectbox label {
        color: #EEEEEE !important;
        font-weight: bold;
    }
    
    /* Hide unnecessary elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Remove empty space around map */
    .stMarkdown {
        margin: 0;
        padding: 0;
    }
    
    iframe {
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Cache data loading
@st.cache_data(ttl=3600)
def load_shapefile(file_path):
    if file_path is None or not os.path.exists(file_path):
        return None
        
    try:
        # Check if all required shapefile components exist
        base_path = file_path.replace('.shp', '')
        required_files = ['.shp', '.shx', '.dbf']
        missing_files = []
        
        for ext in required_files:
            if not os.path.exists(base_path + ext):
                missing_files.append(base_path + ext)
        
        if missing_files:
            st.warning(f"Missing shapefile components: {', '.join(missing_files)}")
            return None
        
        # Set GDAL environment variable to restore missing .shx files if possible
        import geopandas as gpd
        import os as gdal_os
        gdal_os.environ['SHAPE_RESTORE_SHX'] = 'YES'
        
        gdf = gpd.read_file(file_path)
        
        # Simplify geometry for better performance if dataset is large
        if len(gdf) > 100:
            gdf.geometry = gdf.geometry.simplify(0.001, preserve_topology=False)
        
        return gdf
        
    except Exception as e:
        st.error(f"Error loading shapefile {file_path}: {e}")
        return None

@st.cache_data(ttl=3600)
def load_text_data():
    try:
        return pd.read_csv('district_text_data.csv')
    except:
        return pd.DataFrame()

# Parameter mappings for National/State level (exact column names from shapefile)
NATIONAL_PARAMETER_MAPPING = {
    "Solar Irradiance": "2Solar_Irr",
    "Cropping Intensity(%)": "2CropInten", 
    "Irrigation Intensity (%)": "2IrriInten",
    "IWU (% of CWU)": "2IWU_CWU",
    "Elect(%)": "2Elect",
    "GW_dev_stage (%)": "2GW_dev",
    "Surface water area (km2)-%": "2SWArea",
    "Cultivated land (%)": "2Cul-Land",
    "Electricity Subsidy": "2El.Subsid",  # Fixed: exact name from shapefile
    "GW share irr (% of IWU)": "2GW_share",
    "WL (m)": "2WL_m",
    "Small& Marginal % Holdings": "2S_M_Holds"
}

# Parameter mappings for District level (exact column names from shapefile)
DISTRICT_PARAMETER_MAPPING = {
    "Cultivated land (%)": "1Cult_land",  # Fixed: was 1Cult_land1
    "Cropping Intensity(%)": "1Crop_Int",
    "Irrigation Coverage (%)": "1Irrig_Int",  # Fixed: was 1Irrig_Inte
    "Irrigation Water Requirement (% of CWU)": "1IWU",
    "GW irrigation (%)": "1GW_Irr_Sh",
    "GW development (%)": "1GW_Dev",
    "SW bodies (#)": "1no_of_SWB",
    "SW bodies (% of district area)": "1SW_body",
    "Electric pumps (%)": "1ElectPtg",
    "Diesel pumps (%)": "1DieselPtg",
    "Electricity Tariff (paisa/kWH)": "1el_Tariff",
    "Small& Marginal Holdings (%)": "1S_M_Hold",
    "Avg. farmer area (ha)": "1ALLGrps",
    "Avg. number of parcels": "1ALLGrpsNo",
    "DISCOM Name": "1DISCOMNam",
    "DISCOM Rating": "1DISCOMRat",
    "Feeder segregation": "1Feederseg"
}

categories = {
    "Adapt": "Adaptation",
    "Mitigate": "Mitigation", 
    "Replace": "Replacement",
    "General_SI": "General SI"
}

def get_status_class(status):
    """Get CSS class for status based on ranking"""
    if status in ['Very High']:
        return 'very-high'
    elif status in ['High']:
        return 'high'
    elif status in ['Moderate']:
        return 'moderate'
    elif status in ['Low']:
        return 'low'
    elif status in ['Very Low']:
        return 'very-low'
    else:
        return 'no-data'

def calculate_statistics(gdf, category):
    if category not in gdf.columns:
        return None
    
    stats = {}
    # Filter out invalid values before calculating statistics
    valid_data = gdf[gdf[category].apply(is_valid_value)]
    
    if len(valid_data) == 0:
        return None
    
    if valid_data[category].dtype == 'object':
        value_counts = valid_data[category].value_counts()
        total = len(valid_data)  # Use valid data count, not all data
        
        stats['counts'] = {}
        for value, count in value_counts.items():
            if is_valid_value(value):
                percentage = (count / total) * 100
                stats['counts'][value] = {
                    'count': int(count),
                    'percentage': round(percentage, 2)
                }
    return stats

def get_district_details(gdf, state_name, district_name):
    """Get detailed information for a specific district with better matching"""
    if state_name == "All States" or district_name == "All Districts":
        return None
    
    # Try exact match first
    district_data = gdf[
        (gdf["NAME_1"] == state_name) & 
        (gdf["NAME_2"] == district_name)
    ]
    
    # If no exact match, try case-insensitive match
    if len(district_data) == 0:
        district_data = gdf[
            (gdf["NAME_1"].str.lower() == state_name.lower()) & 
            (gdf["NAME_2"].str.lower() == district_name.lower())
        ]
    
    # If still no match, try partial match
    if len(district_data) == 0:
        district_data = gdf[
            (gdf["NAME_1"].str.contains(state_name, case=False, na=False)) & 
            (gdf["NAME_2"].str.contains(district_name, case=False, na=False))
        ]
    
    if len(district_data) == 0:
        st.warning(f"No data found for {district_name}, {state_name}")
        return None
    
    return district_data.iloc[0]

def render_district_dashboard(district_data, selected_category, text_data):
    """Render detailed district-level dashboard with all categories side by side"""
    
    # Get text data for this district
    district_name = district_data.get('NAME_2', 'Unknown District')
    district_text = text_data[text_data['District'] == district_name].iloc[0] if len(text_data[text_data['District'] == district_name]) > 0 else {}
    
    # Create layout with all sections side by side
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    # COLUMN 1: District Information
    with col1:
        st.markdown('<div class="section-header">District</div>', unsafe_allow_html=True)
        
        # Map first - Show district boundary with state boundary overlay
        gdf = st.session_state.get('gdf', None)
        state_boundary_gdf = st.session_state.get('state_boundary_gdf', None)
        
        if gdf is not None:
            state_name = district_data.get('NAME_1', 'Unknown State')
            district_gdf = gdf[(gdf['NAME_1'] == state_name) & (gdf['NAME_2'] == district_name)]
            
            if not district_gdf.empty:
                # Convert to projected CRS for accurate centroid calculation
                district_gdf_projected = district_gdf.to_crs(epsg=3857)  # Web Mercator
                centroid_projected = district_gdf_projected.geometry.centroid.iloc[0]
                # Convert centroid back to WGS84 for folium
                centroid_wgs = gpd.GeoSeries([centroid_projected], crs='EPSG:3857').to_crs('EPSG:4326').iloc[0]
                
                district_gdf_wgs = district_gdf.to_crs(epsg=4326)
                
                m = folium.Map(
                    location=[centroid_wgs.y, centroid_wgs.x],
                    zoom_start=8,
                    tiles="CartoDB dark_matter",
                    width='100%',
                    height='250px'
                )
                
                # Add district boundary
                folium.GeoJson(
                    district_gdf_wgs,
                    style_function=lambda x: {
                        'fillColor': '#00ADB5',
                        'color': '#00ADB5',
                        'weight': 2,
                        'fillOpacity': 0.3
                    }
                ).add_to(m)
                
                # Add state boundary overlay if available
                if state_boundary_gdf is not None:
                    # Check what columns the state boundary has
                    state_cols = state_boundary_gdf.columns.tolist()
                    state_name_col = None
                    
                    # Try to find the state name column
                    for col in ['NAME_1', 'State', 'STATE', 'state', 'name', 'NAME']:
                        if col in state_cols:
                            state_name_col = col
                            break
                    
                    if state_name_col:
                        state_gdf = state_boundary_gdf[state_boundary_gdf[state_name_col] == state_name]
                        if not state_gdf.empty:
                            state_gdf_wgs = state_gdf.to_crs(epsg=4326)
                            folium.GeoJson(
                                state_gdf_wgs,
                                style_function=lambda x: {
                                    'fillColor': 'transparent',
                                    'color': 'white',
                                    'weight': 2,
                                    'fillOpacity': 0
                                }
                            ).add_to(m)
                    else:
                        # If no matching column found, add all state boundaries
                        state_gdf_wgs = state_boundary_gdf.to_crs(epsg=4326)
                        folium.GeoJson(
                            state_gdf_wgs,
                            style_function=lambda x: {
                                'fillColor': 'transparent',
                                'color': 'white',
                                'weight': 1,
                                'fillOpacity': 0
                            }
                        ).add_to(m)
                
                m.fit_bounds([[district_gdf_wgs.geometry.bounds.miny.iloc[0], 
                             district_gdf_wgs.geometry.bounds.minx.iloc[0]],
                            [district_gdf_wgs.geometry.bounds.maxy.iloc[0], 
                             district_gdf_wgs.geometry.bounds.maxx.iloc[0]]])
                
                # Use st_folium instead of folium_static
                st_folium(m, height=250, width=None, returned_objects=[])
            else:
                st.info("District geometry not found")
        else:
            st.info("Map data not loaded")
        
        # Status boxes for all three categories
        for objective, label in [
            ('Adapt', 'Adaptation'),
            ('Mitigate', 'Mitigation'),
            ('Replace', 'Replacement')
        ]:
            status = district_data.get(objective, 'No Data')
            status_class = get_status_class(status)
            st.markdown(f"""
            <div class="status-box {status_class}">
                <div style="font-size: 0.8rem;">{label}: {status}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # District and state info
        st.markdown(f"""
        <div class="metric-container">
            <span class="metric-name">District</span>
            <span class="metric-value">{district_name}</span>
        </div>
        <div class="metric-container">
            <span class="metric-name">State</span>
            <span class="metric-value">{state_name}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # COLUMN 2: Crop Information
    with col2:
        st.markdown('<div class="section-header">Crop</div>', unsafe_allow_html=True)
        crop_params = [
            ("1Crop_Int", "Cropping intensity", "%"),
            ("1Cult_land", "Cultivated land", "%"),
            ("1IWU", "Irrigation water req.", "% of CWU")
        ]
        for param_col, param_name, unit in crop_params:
            value = district_data.get(param_col, 'XX')
            display_value = format_value_with_unit(value, unit)
            st.markdown(f"""
            <div class="metric-container">
                <span class="metric-name">{param_name}</span>
                <span class="metric-value">{display_value}</span>
            </div>
            """, unsafe_allow_html=True)
        
        crop_text = district_text.get('Text-Crop', '')
        if is_valid_value(crop_text):
            st.markdown(f"""
            <div class="text-box">
                <div style="font-size: 0.8rem;">{crop_text}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # COLUMN 3: Water Information
    with col3:
        st.markdown('<div class="section-header">Water</div>', unsafe_allow_html=True)
        water_params = [
            ("1Irrig_Int", "Irrigation coverage", "%"),
            ("1GW_Dev", "GW development", "%"),
            ("1GW_Irr_Sh", "GW irrigation", "%"),
            ("1SW_body", "SW bodies area", "% of district")
        ]
        for param_col, param_name, unit in water_params:
            value = district_data.get(param_col, 'XX')
            display_value = format_value_with_unit(value, unit)
            st.markdown(f"""
            <div class="metric-container">
                <span class="metric-name">{param_name}</span>
                <span class="metric-value">{display_value}</span>
            </div>
            """, unsafe_allow_html=True)
        
        water_text = district_text.get('Text-Water', '')
        if is_valid_value(water_text):
            st.markdown(f"""
            <div class="text-box">
                <div style="font-size: 0.8rem;">{water_text}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # COLUMN 4: Energy Information
    with col4:
        st.markdown('<div class="section-header">Energy</div>', unsafe_allow_html=True)
        energy_params = [
            ("1ElectPtg", "Electric pumps", "%"),
            ("1DieselPtg", "Diesel pumps", "%"),
            ("1el_Tariff", "Electricity tariff", "paisa/kWH")
        ]
        for param_col, param_name, unit in energy_params:
            value = district_data.get(param_col, 'XX')
            display_value = format_value_with_unit(value, unit)
            st.markdown(f"""
            <div class="metric-container">
                <span class="metric-name">{param_name}</span>
                <span class="metric-value">{display_value}</span>
            </div>
            """, unsafe_allow_html=True)
        
        energy_text = district_text.get('Text-Energy', '')
        if is_valid_value(energy_text):
            st.markdown(f"""
            <div class="text-box">
                <div style="font-size: 0.8rem;">{energy_text}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # COLUMN 5: Utility Information
    with col5:
        st.markdown('<div class="section-header">Utility</div>', unsafe_allow_html=True)
        utility_params = [
            ("1DISCOMNam", "DISCOM", ""),
            ("1DISCOMRat", "DISCOM rating", ""),
            ("1Feederseg", "Feeder segregation", "")
        ]
        for param_col, param_name, unit in utility_params:
            value = district_data.get(param_col, 'N/A')
            # Better handling for utility data which might have longer text values
            if is_valid_value(value):
                display_value = str(value)
                # Truncate very long DISCOM names for display
                if len(display_value) > 15 and param_name == "DISCOM":
                    display_value = display_value[:15] + "..."
            else:
                display_value = 'N/A'
            
            st.markdown(f"""
            <div class="metric-container">
                <span class="metric-name">{param_name}</span>
                <span class="metric-value">{display_value}</span>
            </div>
            """, unsafe_allow_html=True)
        
        utility_text = district_text.get('Text-Utilty', '')
        if is_valid_value(utility_text):
            st.markdown(f"""
            <div class="text-box">
                <div style="font-size: 0.8rem;">{utility_text}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # COLUMN 6: Farmer Information
    with col6:
        st.markdown('<div class="section-header">Farmer</div>', unsafe_allow_html=True)
        farmer_params = [
            ("1S_M_Hold", "Small & Marginal", "%"),
            ("1ALLGrps", "Average area", "ha"),
            ("1ALLGrpsNo", "Number of parcels", "")
        ]
        for param_col, param_name, unit in farmer_params:
            value = district_data.get(param_col, 'XX')
            display_value = format_value_with_unit(value, unit)
            st.markdown(f"""
            <div class="metric-container">
                <span class="metric-name">{param_name}</span>
                <span class="metric-value">{display_value}</span>
            </div>
            """, unsafe_allow_html=True)
        
        farmer_text = district_text.get('Text-Farmer', '')
        if is_valid_value(farmer_text):
            st.markdown(f"""
            <div class="text-box">
                <div style="font-size: 0.8rem;">{farmer_text}</div>
            </div>
            """, unsafe_allow_html=True)

    # Add Text-Model as a full-width horizontal box below all columns
    model_text = district_text.get('Text-Model', '')
    if is_valid_value(model_text):
        st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)  # Add spacing
        st.markdown('<div class="section-header">💡 Recommended Model</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="text-box" style="margin-bottom: 0;">
            <div style="font-size: 0.9rem; text-align: center; font-weight: 500;">{model_text}</div>
        </div>
        """, unsafe_allow_html=True)

def get_parameter_values(gdf, selected_state, selected_district, param_mapping):
    filtered_data = gdf.copy()
    
    if selected_state != "All States":
        filtered_data = filtered_data[filtered_data["NAME_1"] == selected_state]
    
    if selected_district != "All Districts":
        filtered_data = filtered_data[filtered_data["NAME_2"] == selected_district]
    
    parameter_values = {}
    for param_name, column_name in param_mapping.items():
        if column_name in filtered_data.columns:
            # Filter out invalid values before calculation
            valid_values = filtered_data[column_name][filtered_data[column_name].apply(is_valid_value)]
            
            if len(valid_values) > 0:
                if valid_values.dtype in ['float64', 'int64']:
                    # Calculate mean only from valid numeric values
                    mean_val = valid_values.mean()
                    if pd.notna(mean_val):
                        parameter_values[param_name] = f"{mean_val:.2f}"
                    else:
                        parameter_values[param_name] = "N/A"
                else:
                    # For categorical data, get the most common valid value
                    mode_values = valid_values.mode()
                    if len(mode_values) > 0 and is_valid_value(mode_values.iloc[0]):
                        parameter_values[param_name] = str(mode_values.iloc[0])
                    else:
                        parameter_values[param_name] = "N/A"
            else:
                parameter_values[param_name] = "N/A"
        else:
            parameter_values[param_name] = "N/A"
    
    return parameter_values

def render_national_state_dashboard(filtered_gdf, selected_category, selected_state):
    """Render the national/state level dashboard"""
    
    # Main content - 3 columns layout
    map_col, stats_col, params_col = st.columns([2, 1, 1])
    
    # MAP COLUMN
    with map_col:
        st.markdown('<div class="section-header">🗺️ Solar Suitability Map</div>', unsafe_allow_html=True)
        
        if not filtered_gdf.empty:
            # Map bounds calculation
            if selected_state == "All States":
                try:
                    full_bounds = filtered_gdf.geometry.total_bounds
                    center_lat = (full_bounds[1] + full_bounds[3]) / 2
                    center_lon = (full_bounds[0] + full_bounds[2]) / 2
                    center = [center_lat, center_lon]
                    zoom_level = 4
                except:
                    center = [20.5937, 78.9629]
                    zoom_level = 4
            else:
                try:
                    bounds = filtered_gdf.geometry.total_bounds
                    center_lat = (bounds[1] + bounds[3]) / 2
                    center_lon = (bounds[0] + bounds[2]) / 2
                    center = [center_lat, center_lon]
                    
                    lat_diff = bounds[3] - bounds[1]
                    lon_diff = bounds[2] - bounds[0]
                    
                    if lat_diff > 8 or lon_diff > 8:
                        zoom_level = 6
                    elif lat_diff > 3 or lon_diff > 3:
                        zoom_level = 7
                    elif lat_diff > 1 or lon_diff > 1:
                        zoom_level = 8
                    else:
                        zoom_level = 9
                except:
                    center = [20.5937, 78.9629]
                    zoom_level = 5
            
            # Create map
            m = folium.Map(location=center, zoom_start=zoom_level, tiles="CartoDB dark_matter")
            
            # Add state boundary overlay if available
            state_boundary_gdf = st.session_state.get('state_boundary_gdf', None)
            if state_boundary_gdf is not None:
                try:
                    state_boundary_wgs = state_boundary_gdf.to_crs(epsg=4326)
                    folium.GeoJson(
                        state_boundary_wgs,
                        style_function=lambda x: {
                            'fillColor': 'transparent',
                            'color': 'white',
                            'weight': 1,
                            'fillOpacity': 0
                        }
                    ).add_to(m)
                except Exception as e:
                    # If there's any issue with state boundary, just skip it
                    pass
            
            # Fit bounds for full view
            if selected_state == "All States":
                try:
                    full_bounds = filtered_gdf.geometry.total_bounds
                    lat_padding = (full_bounds[3] - full_bounds[1]) * 0.05
                    lon_padding = (full_bounds[2] - full_bounds[0]) * 0.05
                    
                    southwest = [full_bounds[1] - lat_padding, full_bounds[0] - lon_padding]
                    northeast = [full_bounds[3] + lat_padding, full_bounds[2] + lon_padding]
                    
                    m.fit_bounds([southwest, northeast])
                except:
                    pass
            
            # Style function with updated colors
            category_colors = get_category_colors(selected_category)
            ranking_colors = get_ranking_color_gradient()
            
            def style_function(feature):
                if selected_category in feature['properties'] and feature['properties'][selected_category] is not None:
                    category_value = str(feature['properties'][selected_category])
                    
                    if category_value in category_colors:
                        color = category_colors[category_value]
                    elif category_value in ranking_colors:
                        color = ranking_colors[category_value]
                    else:
                        color = '#757575'  # Grey for unknown values
                    
                    return {'fillColor': color, 'color': 'black', 'weight': 1, 'fillOpacity': 0.7}
                else:
                    return {'fillColor': '#757575', 'color': 'black', 'weight': 1, 'fillOpacity': 0.7}
            
            # Add data to map
            folium.GeoJson(filtered_gdf, style_function=style_function).add_to(m)
            
            # Display map
            st_folium(m, height=400, width=None, returned_objects=[])
        else:
            st.warning("No data available for selected filters.")
    
    # STATISTICS COLUMN
    with stats_col:
        st.markdown('<div class="section-header">📊 Summary Statistics</div>', unsafe_allow_html=True)
        
        stats = calculate_statistics(filtered_gdf, selected_category)
        
        if stats and 'counts' in stats:
            levels = list(stats['counts'].keys())
            percentages = [stats['counts'][level]['percentage'] for level in levels]
            
            # Show distribution with updated colors
            category_colors = get_category_colors(selected_category)
            ranking_colors = get_ranking_color_gradient()
            
            for level in levels:
                percentage = stats['counts'][level]['percentage']
                
                if level in category_colors:
                    color = category_colors[level]
                elif level in ranking_colors:
                    color = ranking_colors[level]
                else:
                    color = '#757575'  # Grey for unknown values
                
                display_name = level[:25] + "..." if len(level) > 25 else level
                
                st.markdown(f"""
                <div class="metric-container">
                    <span class="metric-name">
                        <span style="display: inline-block; width: 10px; height: 10px; background-color: {color}; margin-right: 6px; border-radius: 2px;"></span>
                        {display_name}
                    </span>
                    <span class="metric-value">{percentage:.1f}%</span>
                </div>
                """, unsafe_allow_html=True)
            
            # Compact pie chart
            if len(levels) <= 6:
                try:
                    fig, ax = plt.subplots(figsize=(3.5, 3.5))
                    pie_colors = []
                    for level in levels:
                        if level in category_colors:
                            pie_colors.append(category_colors[level])
                        elif level in ranking_colors:
                            pie_colors.append(ranking_colors[level])
                        else:
                            pie_colors.append('#757575')
                    
                    wedges, texts, autotexts = ax.pie(
                        percentages, 
                        colors=pie_colors,
                        autopct='%1.1f%%',
                        startangle=90,
                        textprops={'fontsize': 8}
                    )
                    fig.patch.set_facecolor('#2C3E50')
                    ax.set_facecolor('#2C3E50')
                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontweight('bold')
                        autotext.set_fontsize(8)
                    for text in texts:
                        text.set_fontsize(0)  # Hide labels to save space
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close()
                except Exception as chart_error:
                    st.write("Chart could not be rendered")
        else:
            st.markdown('<div class="metric-container"><span class="metric-name">No statistics available</span></div>', unsafe_allow_html=True)
    
    # PARAMETERS COLUMN  
    with params_col:
        st.markdown('<div class="section-header">📋 Key Parameters</div>', unsafe_allow_html=True)
        parameter_values = get_parameter_values(filtered_gdf, selected_state, "All Districts", NATIONAL_PARAMETER_MAPPING)
        for param_name, value in parameter_values.items():
            # Get icon
            if "Solar" in param_name:
                icon = "☀️"
            elif "Water" in param_name or "Irrigation" in param_name or "IWU" in param_name:
                icon = "💧"
            elif "Land" in param_name or "Cultivated" in param_name:
                icon = "🌾"
            elif "Energy" in param_name or "Electric" in param_name:
                icon = "⚡"
            elif "Marginal" in param_name or "Holdings" in param_name:
                icon = "👨‍🌾"
            elif "GW" in param_name:
                icon = "🏞️"
            else:
                icon = "📊"
            st.markdown(f"""
            <div class="metric-container">
                <span class="metric-name">{icon} {param_name}</span>
                <span class="metric-value">{value}</span>
            </div>
            """, unsafe_allow_html=True)

# Main app logic
def main():
    # Function to find shapefiles in current directory and subdirectories
    def find_shapefiles():
        shapefiles = []
        
        # Check current directory
        for file in os.listdir('.'):
            if file.endswith('.shp'):
                shapefiles.append(file)
        
        # Check common subdirectories
        common_dirs = ['Shapefiles', 'shapefiles', 'data', 'Data']
        for dir_name in common_dirs:
            if os.path.exists(dir_name):
                for file in os.listdir(dir_name):
                    if file.endswith('.shp'):
                        shapefiles.append(os.path.join(dir_name, file))
        
        return shapefiles
    
    # Load main shapefile
    available_shapefiles = find_shapefiles()
    
    shapefile_path = None
    
    # Priority order for main shapefile
    priority_names = [
        "true_solar_suitability_with_data.shp", 
        "true_solar_suitability.shp", 
        "Solar_Suitability_layer.shp"
    ]
    
    for priority_name in priority_names:
        for shapefile in available_shapefiles:
            if priority_name in shapefile:
                shapefile_path = shapefile
                break
        if shapefile_path:
            break
    
    # If no priority shapefile found, use the first available one
    if not shapefile_path and available_shapefiles:
        shapefile_path = available_shapefiles[0]
    
    # Load state boundary shapefile - try multiple possible locations
    state_boundary_paths = [
        "F:/GitHub/IWMI_dashboard_7.0/Shapefiles/India_State_Boundary.shp",
        "Shapefiles/India_State_Boundary.shp",
        "shapefiles/India_State_Boundary.shp",
        "India_State_Boundary.shp"
    ]
    
    state_boundary_gdf = None
    
    for path in state_boundary_paths:
        if os.path.exists(path):
            state_boundary_gdf = load_shapefile(path)
            if state_boundary_gdf is not None:
                break
    
    # Load main shapefile
    gdf = load_shapefile(shapefile_path) if shapefile_path else None
    text_data = load_text_data()

    if gdf is not None:
        # Store GeoDataFrame in session state for use in district view
        st.session_state['gdf'] = gdf
        st.session_state['state_boundary_gdf'] = state_boundary_gdf
        
        # Dashboard header
        st.markdown('<h1 class="dashboard-title">🌞 Solar Suitability Dashboard</h1>', unsafe_allow_html=True)
        
        # Top filters - clean and simple
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🌍 State**")
            states = ["All States"]
            if "NAME_1" in gdf.columns:
                valid_states = [str(s) for s in gdf["NAME_1"].unique() if s is not None and str(s) != "nan"]
                states.extend(sorted(valid_states))
            selected_state = st.selectbox("State", states, label_visibility="collapsed")
        
        with col2:
            st.markdown("**🏘️ District**")
            if selected_state != "All States":
                state_filtered = gdf[gdf["NAME_1"] == selected_state]
            else:
                state_filtered = gdf
            
            districts = ["All Districts"]
            if "NAME_2" in gdf.columns:
                valid_districts = [str(d) for d in state_filtered["NAME_2"].unique() if d is not None and str(d) != "nan"]
                districts.extend(sorted(valid_districts))
            selected_district = st.selectbox("District", districts, label_visibility="collapsed")
        
        with col3:
            st.markdown("**🎯 Objective**")
            objective_options = list(categories.keys())
            selected_category = st.selectbox(
                "Objective",
                objective_options,
                format_func=lambda x: categories[x],
                label_visibility="collapsed"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Apply filters
        filtered_gdf = gdf.copy()
        if selected_state != "All States":
            filtered_gdf = filtered_gdf[filtered_gdf["NAME_1"] == selected_state]
        if selected_district != "All Districts":
            filtered_gdf = filtered_gdf[filtered_gdf["NAME_2"] == selected_district]
        
        # Check if showing district-level detail
        show_district_dashboard = (selected_state != "All States" and selected_district != "All Districts")
        
        if show_district_dashboard:
            # Show detailed district dashboard
            district_data = get_district_details(gdf, selected_state, selected_district)
            if district_data is not None:
                render_district_dashboard(district_data, selected_category, text_data)
            else:
                st.error("District data not found")
        else:
            # Show original national/state level dashboard
            render_national_state_dashboard(filtered_gdf, selected_category, selected_state)
    else:
        st.error("Could not load main shapefile. Please check file availability.")
        
        # Show helpful information
        st.markdown("### Available files in current directory:")
        current_files = [f for f in os.listdir('.') if f.endswith(('.shp', '.csv'))]
        if current_files:
            for file in current_files:
                st.write(f"- {file}")
        else:
            st.write("No .shp or .csv files found in current directory")

if __name__ == "__main__":
    main()