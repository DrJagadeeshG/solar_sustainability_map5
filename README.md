# 🌞 Solar Suitability Dashboard

A comprehensive interactive dashboard for analyzing solar energy suitability across Indian districts and states. This application provides detailed insights into solar potential, agricultural patterns, water resources, energy infrastructure, and farmer demographics to support solar energy planning and decision-making.

![Solar Suitability Dashboard](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![GeoPandas](https://img.shields.io/badge/GeoPandas-139C5A?style=for-the-badge&logo=pandas&logoColor=white)

## 🚀 Features

### 📊 Multi-Scale Analysis
- **National Level**: Overview of solar suitability across all Indian states
- **State Level**: Detailed analysis within selected states
- **District Level**: Comprehensive district-specific insights with 6 thematic categories

### 🎯 Solar Suitability Objectives
- **Adaptation**: Areas suitable for adapting existing agricultural practices with solar
- **Mitigation**: Regions where solar can help mitigate agricultural challenges
- **Replacement**: Locations ideal for replacing traditional energy sources with solar

### 📈 Comprehensive Data Categories

#### 🌾 Crop Information
- Cropping intensity percentages
- Cultivated land coverage
- Irrigation water requirements (% of CWU)

#### 💧 Water Resources
- Irrigation coverage statistics
- Groundwater development levels
- Groundwater irrigation share
- Surface water body coverage

#### ⚡ Energy Infrastructure
- Electric vs diesel pump distribution
- Electricity tariff information
- Energy consumption patterns

#### 🏢 Utility Information
- DISCOM (Distribution Company) details with smart acronym extraction
- DISCOM ratings and performance metrics
- Feeder segregation status

#### 👨‍🌾 Farmer Demographics
- Small and marginal farmer percentages
- Average farm area per holding
- Land parcel fragmentation data

### 🗺️ Interactive Mapping
- **High-performance cached maps** with state boundary overlays
- **Color-coded visualization** based on solar suitability rankings
- **Responsive zoom levels** adapting to geographic scale
- **White state boundaries** for clear geographic context

### 📋 Smart Data Processing
- **Intelligent data validation** with handling of missing/invalid values
- **Automated average calculations** using pandas optimization
- **DISCOM name processing** with acronym extraction
- **Performance caching** for lightning-fast loading

## 🛠️ Technology Stack

- **Frontend**: Streamlit with custom CSS styling
- **Geospatial**: GeoPandas, Folium, Streamlit-Folium
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib, Folium maps
- **Performance**: Streamlit caching with TTL optimization

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/DrJagadeeshG/solar_sustainability_map5.git
   cd solar_sustainability_map5
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare data files**
   - Ensure shapefiles are in the root directory or `Shapefiles/` folder
   - Required files: `true_solar_suitability_with_data.shp` (and associated .shx, .dbf files)
   - Optional: `India_State_Boundary.shp` for state boundaries
   - Text data: `district_text_data.csv`

5. **Run the application**
   ```bash
   streamlit run "app - Copy.py"
   ```

## 📁 Project Structure

```
solar_sustainability_map5/
├── app - Copy.py                 # Main Streamlit application
├── district_text_data.csv        # District-specific text descriptions
├── updated_legend_component.py   # Color scheme definitions
├── requirements.txt              # Python dependencies
├── Shapefiles/                   # Geospatial data directory
│   ├── true_solar_suitability_with_data.shp
│   ├── India_State_Boundary.shp
│   └── ... (associated shapefile components)
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## 🎨 User Interface

### Dashboard Layout
- **Clean, professional dark theme** with teal accent colors
- **Responsive 6-column layout** for district-level analysis
- **Intuitive filter system** with state and district selection
- **Status indicators** with color-coded solar suitability rankings

### Performance Optimizations
- **Aggressive caching** for data processing and map generation
- **Geometry simplification** for faster rendering
- **Smart data loading** with session state management
- **Optimized folium maps** with cached boundary processing

## 📊 Data Sources

The dashboard processes geospatial and tabular data including:
- **Solar irradiance measurements**
- **Agricultural statistics** (cropping intensity, irrigation coverage)
- **Water resource data** (groundwater development, surface water bodies)
- **Energy infrastructure** (pump types, electricity tariffs)
- **Utility information** (DISCOM details, ratings)
- **Farmer demographics** (land holding patterns)

## 🔧 Configuration

### Customizing Colors
Edit `updated_legend_component.py` to modify:
- Category color schemes
- Ranking color gradients
- Legend configurations

### Performance Tuning
Adjust caching parameters in the main application:
```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
```

### Map Settings
Modify map parameters:
- Zoom levels for different scales
- Geometry simplification tolerance
- Boundary line weights and colors

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Dr. Jagadeesh G** - *Project Lead* - [@DrJagadeeshG](https://github.com/DrJagadeeshG)

## 🙏 Acknowledgments

- **IWMI (International Water Management Institute)** for data and research support
- **Streamlit community** for the excellent framework
- **GeoPandas and Folium teams** for geospatial capabilities
- **Contributors** who helped optimize performance and user experience

## 📞 Support

For questions, issues, or contributions:
- 📧 Email: [Contact Information]
- 🐛 Issues: [GitHub Issues](https://github.com/DrJagadeeshG/solar_sustainability_map5/issues)
- 📖 Documentation: This README and inline code comments

---

**Built with ❤️ for sustainable energy planning and agricultural development** 