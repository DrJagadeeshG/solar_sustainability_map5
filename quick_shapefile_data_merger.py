import pandas as pd
import geopandas as gpd

print("=== Working Data Merger ===")

# Load files
print("Loading files...")
gdf = gpd.read_file('Shapefiles/true_solar_suitability.shp')
country_data = pd.read_csv('Country_State_Param_Values.csv')
rankings = pd.read_csv('Solar_new_ranking.csv')

try:
    district_params = pd.read_csv('District_Param_Values.csv')
    print(f"✅ District params loaded: {len(district_params)} rows")
except:
    print("⚠️  District_Param_Values.csv not found or empty")
    district_params = pd.DataFrame()

try:
    district_colnames = pd.read_csv('District_ColNames.csv')
    print(f"✅ District column names loaded: {len(district_colnames)} rows")
except:
    print("⚠️  District_ColNames.csv not found")
    district_colnames = pd.DataFrame()

print(f"Shapefile: {len(gdf)} districts")
print(f"Country data: {len(country_data)} rows")
print(f"Rankings: {len(rankings)} rows")

# STEP 1: Add rankings by district name
print("\n=== Step 1: Adding Rankings ===")
rankings_dict = {}
for _, row in rankings.iterrows():
    district = row['District']
    rankings_dict[district] = {
        'Adapt': row.get('Adapt_new', 'No Data'),
        'Mitigate': row.get('Mitigate_new', 'No Data'), 
        'Replace': row.get('Replace_new', 'No Data'),
        'General_SI': row.get('Combine', 'No Data')
    }

# Add ranking columns to shapefile
for col in ['Adapt', 'Mitigate', 'Replace', 'General_SI']:
    gdf[col] = 'No Data'

ranking_matches = 0
for idx, row in gdf.iterrows():
    district = row['NAME_2']
    if district in rankings_dict:
        gdf.at[idx, 'Adapt'] = rankings_dict[district]['Adapt']
        gdf.at[idx, 'Mitigate'] = rankings_dict[district]['Mitigate']
        gdf.at[idx, 'Replace'] = rankings_dict[district]['Replace']
        gdf.at[idx, 'General_SI'] = rankings_dict[district]['General_SI']
        ranking_matches += 1

print(f"✅ Rankings added: {ranking_matches} districts matched")

# STEP 2: Add Country/State level data
print("\n=== Step 2: Adding Country/State Data ===")
# Exact column mappings from your files
country_mappings = {
    'Solar Irradiance': '2Solar_Irra',
    'Cropping Intensity(%)': '2CropInten',
    'Irrigation Intensity (%)': '2IrriInten',
    'IWU (% of CWU)': '2IWU_CWU',
    'Elect(%)': '2Elect',
    'GW_dev_stage (%)': '2GW_dev',
    'Surface water area (km2)-%': '2SWArea',
    'Cultivated land (%)': '2Cul-Land',
    'Electricity Subsidy': '2El.Subsidy',
    'GW share irr (% of IWU)': '2GW_share',
    'WL (m)': '2WL_m',
    'Small& Marginal % Holdings': '2S_M_Holds'
}

# Create district lookup from country data
country_dict = {}
for _, row in country_data.iterrows():
    district = row['District']
    country_dict[district] = row.to_dict()

print(f"Available columns in country data: {list(country_data.columns)}")
print(f"Sample district data: {list(country_dict.keys())[:5]}")

# Add country-level columns
for orig_col, qgis_col in country_mappings.items():
    print(f"Processing {orig_col} -> {qgis_col}")
    
    if orig_col not in country_data.columns:
        print(f"  ⚠️  Column '{orig_col}' not found in country data")
        continue
        
    gdf[qgis_col] = None
    
    matched = 0
    for idx, row in gdf.iterrows():
        district = row['NAME_2']
        if district in country_dict:
            value = country_dict[district][orig_col]
            if pd.notna(value) and str(value).strip() not in ['', 'N/A', 'nan']:
                gdf.at[idx, qgis_col] = value
                matched += 1
    
    print(f"  ✅ {matched} districts matched for {orig_col}")

print(f"✅ Country/State data added: {len(country_mappings)} columns processed")

# STEP 3: Add District level data (hardcoded mappings)
print("\n=== Step 3: Adding District Data ===")

# Hardcoded district column mappings
district_mappings = {
    'Cultivated land (%)': '1Cult_land1',
    'Cropping Intensity(%)': '1Crop_Int',
    'Irrigation Intensity (%)': '1Irrig_Inte',
    'IWU (% of CWU)': '1IWU',
    'GW share irr (% of IWU)': '1GW_Irr_Sh',
    'GW_dev_stage (%)': '1GW_Dev',
    'Number of SW bodies': '1no_of_SWB',
    'Surface water area (km2)-%': '1SW_body',
    'Elect(%)': '1ElectPtg',
    'Diesel (%)': '1DieselPtg',
    'Electricity Tariff': '1el_Tariff',
    'Small& Marginal % Holdings': '1S_M_Hold',
    'Avg Area per holding (ALLGrps)': '1ALLGrps',
    'Avg. No. of Parcel per holdings (Allgrps)': '1ALLGrpsNo',
    'DISCOM Name': '1DISCOMNam',
    'DISCOM Rating': '1DISCOMRat',
    'Feeder segregation': '1Feederseg'
}

# Text columns (go to CSV)
text_columns = [
    'Text-Crop',
    'Text-Water', 
    'Text-Energy',
    'Text-Farmer',
    'Text-Utilty',
    'Text-Model'
]

if not district_params.empty:
    print("Processing district-level data...")
    print(f"Available columns in district data: {list(district_params.columns)}")
    
    # Create district lookup
    district_dict = {}
    for _, row in district_params.iterrows():
        district = row.get('District', '')
        if district:
            district_dict[district] = row.to_dict()
    
    print(f"District data has {len(district_dict)} districts")
    
    # Process district numerical columns
    numerical_added = 0
    
    for orig_col, qgis_col in district_mappings.items():
        print(f"Processing {orig_col} -> {qgis_col}")
        
        if orig_col not in district_params.columns:
            print(f"  ⚠️  Column '{orig_col}' not found in district data")
            continue
            
        gdf[qgis_col] = None
        
        matched = 0
        for idx, gdf_row in gdf.iterrows():
            district = gdf_row['NAME_2']
            if district in district_dict:
                value = district_dict[district][orig_col]
                if pd.notna(value) and str(value).strip() not in ['', 'N/A', 'nan']:
                    gdf.at[idx, qgis_col] = value
                    matched += 1
        
        print(f"  ✅ {matched} districts matched for {orig_col}")
        numerical_added += 1
    
    print(f"✅ District numerical data: {numerical_added} columns processed")
    
    # Create text CSV
    print(f"\n=== Creating Text CSV ===")
    text_data = []
    for _, row in district_params.iterrows():
        text_row = {'District': row.get('District', '')}
        for col in text_columns:
            if col in district_params.columns:
                value = row[col]
                text_row[col] = str(value).strip() if pd.notna(value) and str(value).strip() not in ['N/A', 'nan', 'null'] else ''
            else:
                text_row[col] = ''
                print(f"  ⚠️  Text column '{col}' not found")
        text_data.append(text_row)
    
    text_df = pd.DataFrame(text_data)
    text_df.to_csv('district_text_data.csv', index=False)
    print(f"✅ Text CSV created with {len(text_columns)} text columns")
    
    # Show text data completeness
    for col in text_columns:
        if col in text_df.columns:
            non_empty = (text_df[col] != '').sum()
            print(f"  {col}: {non_empty} districts have text")
    
else:
    print("⚠️  District data not available - using country data only")
    # Create empty text CSV
    empty_text_df = pd.DataFrame({'District': []})
    for col in text_columns:
        empty_text_df[col] = []
    empty_text_df.to_csv('district_text_data.csv', index=False)
    print("✅ Created empty text CSV")

# Save the final shapefile
print("\n=== Saving Files ===")
output_path = 'Shapefiles/true_solar_suitability_with_data.shp'
gdf.to_file(output_path)
print(f"✅ Shapefile saved to: {output_path}")

# Final check
print("\n=== Final Results ===")
print(f"Total shapefile columns: {len(gdf.columns)}")

# Check rankings
adapt_count = len(gdf[gdf['Adapt'] != 'No Data'])
print(f"Districts with ranking data: {adapt_count}/{len(gdf)}")

# Check numerical data
numerical_cols = [col for col in gdf.columns if col.startswith(('1', '2'))]
print(f"Numerical columns added: {len(numerical_cols)}")

# Show non-null counts for each numerical column
print("\nData completeness:")
for col in numerical_cols:
    non_null = gdf[col].notna().sum()
    print(f"  {col}: {non_null}/{len(gdf)} districts")

# Show sample data
if adapt_count > 0:
    sample = gdf[gdf['Adapt'] != 'No Data'].iloc[0]
    print(f"\nSample district: {sample['NAME_2']}, {sample['NAME_1']}")
    print(f"  Adapt: {sample['Adapt']}")
    print(f"  Mitigate: {sample['Mitigate']}")
    print(f"  Replace: {sample['Replace']}")
    
    # Show some numerical values
    for col in numerical_cols[:3]:
        value = sample.get(col, 'NULL')
        print(f"  {col}: {value}")

print("\n🎉 Data merger completed successfully!")
print("You can now use the updated shapefile in your Streamlit app.")