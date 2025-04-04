import streamlit as st
import matplotlib.pyplot as plt
import geopandas as gpd
from grid_reader import read_grids
from shapely.geometry import Polygon
from PIL import Image
import os

# Set page config
st.set_page_config(
    page_title="Astoria Visitor Analysis",
    page_icon="🗽",
    layout="wide"
)

# Title and description
st.title("Astoria Visitor Analysis Dashboard")
st.markdown("""
This dashboard visualizes the Astoria neighborhood area in Queens, NYC and related analysis visualizations.
""")

# Function to load and process data
@st.cache_data
def load_data():
    try:
        st.write("Loading data...")
        # Import Taxi Zone map and data
        taxi_grids_name = "geo_export_e612eba5-03f4-49f0-a0ac-528f1c3802b8.shp"
        taxi_zones = read_grids(taxi_grids_name, grid_name='taxi zones')
        
        # Define Astoria boundaries
        astoria_coords = [
            (-73.9326, 40.7723),  # Northwest corner (near Astoria Park)
            (-73.9096, 40.7716),  # Northeast corner (near LaGuardia Airport)
            (-73.9132, 40.7637),  # East point (near 49th Street)
            (-73.9220, 40.7563),  # Southeast corner (near Northern Blvd)
            (-73.9387, 40.7574),  # Southwest corner (near 36th Avenue)
            (-73.9428, 40.7686),  # West point (near 21st Street)
            (-73.9326, 40.7723)   # Back to start to close the polygon
        ]
        
        astoria_polygon = Polygon(astoria_coords)
        attraction_zone = gpd.GeoDataFrame(
            {'geometry': [astoria_polygon]},
            crs="EPSG:4326"
        )
        attraction_zone = attraction_zone.to_crs(taxi_zones.crs)
        st.write("Data loading complete!")
        
        return taxi_zones, attraction_zone
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None

def plot_map(fig, ax, title):
    try:
        plt.axis('off')
        st.subheader(title)
        st.pyplot(fig)
    finally:
        plt.close(fig)  # Ensure figure is closed even if error occurs

def safe_display_image(image_path, caption):
    """Safely display an image with error handling"""
    try:
        if os.path.exists(image_path):
            st.image(image_path, caption=caption)
        else:
            st.warning(f"Image not found: {image_path}")
    except Exception as e:
        st.error(f"Error displaying image {caption}: {str(e)}")

# Function to create and display maps
def create_maps(taxi_zones, attraction_zone):
    if taxi_zones is None or attraction_zone is None:
        st.error("Cannot create maps: required data not loaded")
        return
        
    try:
        # Base Map
        st.write("Creating base map...")
        fig1, ax1 = plt.subplots(figsize=(10, 10))
        taxi_zones.plot(ax=ax1)
        attraction_zone.plot(ax=ax1, color='red', alpha=0.7)
        plot_map(fig1, ax1, "Astoria Area Overview")
    except Exception as e:
        st.error(f"Error creating base map: {str(e)}")

# Main execution
try:
    with st.spinner('Loading data...'):
        taxi_zones, attraction_zone = load_data()
    
    if taxi_zones is not None and attraction_zone is not None:
        create_maps(taxi_zones, attraction_zone)
    
        # Display additional visualizations
        st.subheader("Additional Visualizations")
        
        # Create three columns for the images
        col1, col2, col3 = st.columns(3)
        
        # Load and display images
        with col1:
            safe_display_image("data/visitorcountsbyzone.png", "Visitor Counts by Zone")
        
        with col2:
            safe_display_image("data/taxipassengercounts.png", "Taxi Passenger Counts")
        
        with col3:
            safe_display_image("data/taxiratio.png", "Taxi Usage Ratio")
        
        # Add insights section
        st.subheader("Map Legend")
        st.markdown("""
        ### Area Information
        - The red highlighted area shows the Astoria neighborhood boundaries
        - The surrounding areas show NYC taxi zones
        - Additional visualizations show visitor counts, taxi passenger counts, and usage ratios
        """)

except Exception as e:
    st.error(f"An error occurred in the main execution: {str(e)}")
    st.write("Please check if all required files and dependencies are present.") 