import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from data_reader import read_data
from grid_reader import read_grids
from grid_mapper import map_to_taxiZones
from visit_counter import count_visits
from shapely.geometry import Polygon
import joblib

# Set page config
st.set_page_config(
    page_title="Astoria Visitor Analysis",
    page_icon="🗽",
    layout="wide"
)

# Title and description
st.title("Astoria Visitor Analysis Dashboard")
st.markdown("""
This dashboard visualizes visitor patterns and taxi usage in the Astoria neighborhood of Queens, NYC.
The analysis includes mobile phone data and taxi trip data to understand movement patterns.
""")

# Function to load and process data
@st.cache_data
def load_data():
    st.write("Loading data...")
    # Import Census Block map and data
    cbg_grids_name = "cb_2021_36_bg_500k.shp"
    nyc_geoids, cbgs_nyc = read_grids(cbg_grids_name, grid_name='Census Blocks')
    
    # Import Taxi Zone map and data
    taxi_grids_name = "geo_export_e612eba5-03f4-49f0-a0ac-528f1c3802b8.shp"
    taxi_zones = read_grids(taxi_grids_name, grid_name='taxi zones')
    
    # Map census blocks to taxi zones
    cbgs_nyc = map_to_taxiZones(cbgs_nyc, taxi_zones)
    
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
    
    return nyc_geoids, cbgs_nyc, taxi_zones, attraction_zone

def plot_map(fig, ax, title):
    plt.axis('off')
    st.subheader(title)
    st.pyplot(fig)
    plt.close(fig)  # Clear the figure

# Function to create and display maps
def create_maps(nyc_geoids, cbgs_nyc, taxi_zones, attraction_zone):
    # Base Map
    st.write("Creating base map...")
    fig1, ax1 = plt.subplots(figsize=(10, 10))
    taxi_zones.plot(ax=ax1)
    attraction_zone.plot(ax=ax1, color='red', alpha=0.7)
    plot_map(fig1, ax1, "Astoria Area Overview")
    
    try:
        # Load mobile phone data
        st.write("Processing visitor data...")
        file_name = 'data/poi_NY_initial_subset.csv'
        geo_data = read_data(file_name)
        geo_data = geo_data[geo_data.within(attraction_zone.loc[0,'geometry'])]
        geo_data = geo_data[~geo_data['visitor_home_cbgs'].isna()][['location_name','visitor_home_cbgs']]
        
        # Process visitor data
        visits = count_visits(geo_data, nyc_geoids)
        merged = pd.merge(
            cbgs_nyc, 
            visits, 
            left_on='GEOID', 
            right_on='geoid', 
            how='right'
        )[['taxi_object_id','visitor_cnt','geometry','geoid','GEOID']]
        merged = merged[~merged['taxi_object_id'].isna()]
        
        visitor_counts = pd.DataFrame(merged.groupby('taxi_object_id')['visitor_cnt'].sum()).reset_index(drop=False)
        visitor_counts = pd.merge(
            taxi_zones, 
            visitor_counts, 
            left_on='objectid', 
            right_on='taxi_object_id', 
            how='right'
        )
        
        # Visitor Counts Map
        st.write("Creating visitor counts map...")
        fig2, ax2 = plt.subplots(figsize=(10, 10))
        cbgs_nyc.plot(ax=ax2, alpha=0.7)
        tmp = visitor_counts[~visitor_counts['geometry'].isna()]
        tmp.plot(
            column='visitor_cnt',
            ax=ax2,
            legend=True,
            cmap='viridis',
            legend_kwds={'loc': 'upper left'},
            scheme='User_Defined',
            classification_kwds=dict(bins=[8, 20, 60, 100, 150, 250, 300, 500])
        )
        ax2.get_legend().set_title("Astoria Visitor Counts")
        attraction_zone.plot(ax=ax2, color='red', alpha=0.4)
        plot_map(fig2, ax2, "Visitor Counts by Zone")
        
        try:
            # Load and process taxi data
            st.write("Processing taxi data...")
            taxi_data = pd.read_parquet('data/yellow_tripdata_2022-12.parquet')
            AttDO_zones = taxi_zones[taxi_zones.intersects(attraction_zone.loc[0,'geometry'])]
            AttDO_zones_ids = AttDO_zones['objectid'].unique().tolist()
            
            taxi_data = taxi_data[taxi_data['DOLocationID'].isin(AttDO_zones_ids)]
            trip_passenger_counts = pd.DataFrame(
                taxi_data.groupby('PULocationID')['passenger_count'].sum()
            ).reset_index(drop=False)
            
            # Combine visitor and taxi data
            visitor_counts_wTaxi_use = pd.merge(
                visitor_counts,
                trip_passenger_counts,
                left_on='taxi_object_id',
                right_on='PULocationID',
                how='left'
            )
            
            # Taxi Passenger Counts Map
            st.write("Creating taxi passenger counts map...")
            fig3, ax3 = plt.subplots(figsize=(10, 10))
            cbgs_nyc.plot(ax=ax3, alpha=0.7)
            visitor_counts_wTaxi_use.plot(
                column='passenger_count',
                ax=ax3,
                legend=True,
                cmap='viridis',
                legend_kwds={'loc': 'upper left'},
                scheme='User_Defined',
                classification_kwds=dict(bins=[25, 50, 100, 1000, 5000, 10000, 20000, 30000])
            )
            ax3.get_legend().set_title("Taxi Passengers Count")
            attraction_zone.plot(ax=ax3, color='red', alpha=0.4)
            plot_map(fig3, ax3, "Taxi Passenger Counts")
            
            # Ratio Map
            st.write("Creating ratio map...")
            comparison_data = visitor_counts_wTaxi_use[['taxi_object_id', 'visitor_cnt', 'passenger_count', 'geometry']]
            comparison_data['ratio'] = comparison_data['passenger_count'] / comparison_data['visitor_cnt']
            
            fig4, ax4 = plt.subplots(figsize=(10, 10))
            cbgs_nyc.plot(ax=ax4, alpha=0.7)
            comparison_data.plot(
                column='ratio',
                ax=ax4,
                legend=True,
                cmap='viridis',
                legend_kwds={'loc': 'upper left'},
                scheme='User_Defined',
                classification_kwds=dict(bins=[0.03, 0.08, 0.81, 10, 66.2, 100, 200, 500, 1200])
            )
            ax4.get_legend().set_title("Ratio of taxi use over visitor cnt")
            attraction_zone.plot(ax=ax4, color='red', alpha=0.4)
            plot_map(fig4, ax4, "Ratio of Taxi Usage to Visitor Count")
            
        except Exception as e:
            st.error(f"Error processing taxi data: {str(e)}")
            st.write("Please make sure the taxi data file (yellow_tripdata_2022-12.parquet) is present in the data directory.")
    except Exception as e:
        st.error(f"Error processing visitor data: {str(e)}")
        st.write("Please make sure the POI data file (poi_NY_initial_subset.csv) is present in the data directory.")

# Main execution
try:
    with st.spinner('Loading data...'):
        nyc_geoids, cbgs_nyc, taxi_zones, attraction_zone = load_data()
    
    create_maps(nyc_geoids, cbgs_nyc, taxi_zones, attraction_zone)
    
    # Add insights section
    st.subheader("Key Insights")
    
    # Try to load the ML model
    try:
        model = joblib.load('astoria_visitor_model.joblib')
        st.write("ML Model Performance:", model.score)
    except:
        st.write("ML model not available. Run the analysis in lab.py first to generate the model.")
    
    # Add additional statistics
    st.markdown("""
    ### Additional Information
    - The red highlighted area shows the Astoria neighborhood boundaries
    - Visitor counts are based on mobile phone data
    - Taxi data is from December 2022
    - The ratio map shows the relationship between taxi usage and visitor counts
    """)

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.write("Please make sure all required data files are present and the analysis in lab.py has been run first.") 