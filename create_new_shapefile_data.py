import pandas as pd
import numpy as np

def clean_data_value(value):
    """Clean and standardize data values, converting various forms of missing data to NaN"""
    if pd.isna(value):
        return np.nan
    
    # Convert to string for checking
    str_val = str(value).strip()
    
    # List of values to treat as missing/invalid
    invalid_values = ['', 'XX', 'N/A', 'n/a', 'nan', 'NaN', 'null', 'NULL', '#N/A', '-', 'None', 'none']
    
    if str_val.lower() in [v.lower() for v in invalid_values]:
        return np.nan
    
    # Try to convert to numeric if possible
    try:
        numeric_val = pd.to_numeric(str_val)
        # Check for unrealistic values that might be data errors
        if numeric_val == 0 and str_val != '0':  # Zero that wasn't originally zero
            return np.nan
        return numeric_val
    except (ValueError, TypeError):
        # Return as string if not numeric
        return str_val if str_val else np.nan

# Load the data files
country_state_params = pd.read_csv('Country_State_Param_Values.csv')
district_params = pd.read_csv('District_Param_Values.csv')
solar_ranking = pd.read_csv('Solar_new_ranking.csv')
country_state_colnames = pd.read_csv('Country_State_ColNames.csv')
district_colnames = pd.read_csv('District_ColNames.csv')

print(f"Country/State params: {len(country_state_params)} rows")
print(f"District params: {len(district_params)} rows")
print(f"Solar ranking: {len(solar_ranking)} rows")

# Clean the data
print("\n=== Cleaning Data ===")

# Clean country/state params
for col in country_state_params.columns:
    if col != 'District':
        country_state_params[col] = country_state_params[col].apply(clean_data_value)

# Clean district params
for col in district_params.columns:
    if col != 'District' and not col.startswith('Text-'):
        district_params[col] = district_params[col].apply(clean_data_value)

# Clean solar ranking
for col in solar_ranking.columns:
    if col != 'District':
        solar_ranking[col] = solar_ranking[col].apply(lambda x: x if pd.notna(x) and str(x).strip() else 'No Data')

print("Data cleaning completed.")

# Create the national/state level shapefile data
print("\n=== Creating National/State Level Data ===")

# Merge country/state params with solar ranking
national_state_data = pd.merge(country_state_params, solar_ranking, on='District', how='left')

# Create the shapefile columns based on naming convention
shapefile_data_national = pd.DataFrame()
shapefile_data_national['District'] = national_state_data['District']

# Add the ranking columns (Adapt, Mitigate, replace)
shapefile_data_national['Adapt'] = national_state_data['Adapt_new'].fillna('No Data')
shapefile_data_national['Mitigate'] = national_state_data['Mitigate_new'].fillna('No Data')
shapefile_data_national['Replace'] = national_state_data['Replace_new'].fillna('No Data')
shapefile_data_national['General_SI'] = national_state_data['Combine'].fillna('No Data')

# Add numerical parameters using the naming convention
for _, row in country_state_colnames.iterrows():
    original_col = row['Column']
    qgis_col = row['QGIS Naming Convention']
    
    if original_col in national_state_data.columns:
        shapefile_data_national[qgis_col] = national_state_data[original_col]

print(f"National/State shapefile data columns: {list(shapefile_data_national.columns)}")
print(f"National/State shapefile data shape: {shapefile_data_national.shape}")

# Check for missing data in key columns
print("\nMissing data summary (National/State):")
for col in shapefile_data_national.columns:
    missing_count = shapefile_data_national[col].isna().sum()
    if missing_count > 0:
        print(f"  {col}: {missing_count} missing values ({missing_count/len(shapefile_data_national)*100:.1f}%)")

# Save national/state data
shapefile_data_national.to_csv('national_state_shapefile_data.csv', index=False)

# Create the district level shapefile data
print("\n=== Creating District Level Data ===")

# Merge district params with solar ranking
district_data = pd.merge(district_params, solar_ranking, on='District', how='left')

# Create the shapefile columns for district level
shapefile_data_district = pd.DataFrame()
shapefile_data_district['District'] = district_data['District']

# Add the ranking columns
shapefile_data_district['Adapt'] = district_data['Adapt_new'].fillna('No Data')
shapefile_data_district['Mitigate'] = district_data['Mitigate_new'].fillna('No Data')
shapefile_data_district['Replace'] = district_data['Replace_new'].fillna('No Data')
shapefile_data_district['General_SI'] = district_data['Combine'].fillna('No Data')

# Add numerical parameters using the district naming convention
for _, row in district_colnames.iterrows():
    original_col = row['Column']
    qgis_col = row['QGIS Naming Convention']
    
    if original_col in district_data.columns and not original_col.startswith('Text-'):
        shapefile_data_district[qgis_col] = district_data[original_col]

print(f"District shapefile data columns: {list(shapefile_data_district.columns)}")
print(f"District shapefile data shape: {shapefile_data_district.shape}")

# Check for missing data in key columns
print("\nMissing data summary (District):")
for col in shapefile_data_district.columns:
    missing_count = shapefile_data_district[col].isna().sum()
    if missing_count > 0:
        print(f"  {col}: {missing_count} missing values ({missing_count/len(shapefile_data_district)*100:.1f}%)")

# Save district data
shapefile_data_district.to_csv('district_shapefile_data.csv', index=False)

# Create text data CSV (separate from shapefile)
print("\n=== Creating Text Data CSV ===")

text_data = pd.DataFrame()
text_data['District'] = district_data['District']

# Add all text columns and clean them
text_columns = ['Text-Crop', 'Text-Water', 'Text-Energy', 'Text-Farmer', 'Text-Utilty', 'Text-Model']
for col in text_columns:
    if col in district_data.columns:
        # Clean text data - replace various forms of missing data with empty string
        text_data[col] = district_data[col].apply(lambda x: str(x).strip() if pd.notna(x) and str(x).strip() not in ['N/A', 'nan', 'NaN', 'null', 'NULL'] else '')

text_data.to_csv('district_text_data.csv', index=False)

print(f"Text data shape: {text_data.shape}")
print(f"Text data columns: {list(text_data.columns)}")

# Check text data completeness
print("\nText data completeness:")
for col in text_columns:
    if col in text_data.columns:
        non_empty = (text_data[col] != '').sum()
        print(f"  {col}: {non_empty} districts have text ({non_empty/len(text_data)*100:.1f}%)")

# Create parameter mapping for the updated app
print("\n=== Creating Parameter Mappings ===")

# National/State parameter mapping
national_mapping = {}
for _, row in country_state_colnames.iterrows():
    label = row['LabelonDashboard']
    qgis_col = row['QGIS Naming Convention']
    if pd.notna(label):
        national_mapping[label] = qgis_col

print("National/State Parameter Mapping:")
for k, v in national_mapping.items():
    print(f"  '{k}': '{v}',")

# District parameter mapping
district_mapping = {}
for _, row in district_colnames.iterrows():
    label = row['LabelonDashboard']
    qgis_col = row['QGIS Naming Convention']
    if pd.notna(label):
        district_mapping[label] = qgis_col

print("\nDistrict Parameter Mapping:")
for k, v in district_mapping.items():
    print(f"  '{k}': '{v}',")

print("\n=== Files Created ===")
print("1. national_state_shapefile_data.csv - Data to merge with national/state shapefile")
print("2. district_shapefile_data.csv - Data to merge with district shapefile")
print("3. district_text_data.csv - Text data to be read separately")
print("\nNext steps:")
print("1. Merge these CSV files with your shapefiles in QGIS")
print("2. Update the app.py with the new parameter mappings shown above")
print("3. Update the legend_component.py with the new ranking values")
print("\nData Quality Notes:")
print("- All N/A, blank, and invalid values have been standardized")
print("- Numeric columns have been properly cleaned and validated")
print("- Text columns have been cleaned but preserved where meaningful")
print("- Ranking categories default to 'No Data' when missing")