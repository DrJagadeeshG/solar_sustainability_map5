import geopandas as gpd

# Path to your shapefile
shapefile_path = "F:/GitHub/IWMI_dashboard_7.0/Shapefiles/true_solar_suitability_with_data.shp"

# Load the shapefile
gdf = gpd.read_file(shapefile_path)

# Print all column names
print("Column names in the shapefile:")
for col in gdf.columns:
    print(col)
