import streamlit as st
import matplotlib.pyplot as plt
import geopandas as gpd
from grid_reader import read_grids
from shapely.geometry import Polygon

# Set page config
st.set_page_config(
    page_title="Astoria Visitor Analysis",
    page_icon="🗽",
    layout="wide"
)

# Title and description
st.title("Astoria Visitor Analysis Dashboard")
st.markdown("""
This dashboard visualizes the Astoria neighborhood area in Queens, NYC.
""")

# Function to load and process data
@st.cache_data
def load_data():
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

def plot_map(fig, ax, title):
    plt.axis('off')
    st.subheader(title)
    st.pyplot(fig)
    plt.close(fig)  # Clear the figure

# Function to create and display maps
def create_maps(taxi_zones, attraction_zone):
    # Base Map
    st.write("Creating base map...")
    fig1, ax1 = plt.subplots(figsize=(10, 10))
    taxi_zones.plot(ax=ax1)
    attraction_zone.plot(ax=ax1, color='red', alpha=0.7)
    plot_map(fig1, ax1, "Astoria Area Overview")

# Main execution
try:
    with st.spinner('Loading data...'):
        taxi_zones, attraction_zone = load_data()
    
    create_maps(taxi_zones, attraction_zone)
    
    # Add insights section
    st.subheader("Map Legend")
    st.markdown("""
    ### Area Information
    - The red highlighted area shows the Astoria neighborhood boundaries
    - The surrounding areas show NYC taxi zones
    """)

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.write("Please make sure all required data files are present.") 