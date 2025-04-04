# -*- coding: utf-8 -*-
'''
@author: Ryan Kim rjk2189
'''

#Step 1: Import necessary libraries
import matplotlib.pyplot as plt 
import pandas as pd 
from data_reader import read_data 
from grid_reader import read_grids 
from grid_mapper import map_to_taxiZones 
from visit_counter import count_visits 
from shapely.geometry import Polygon
import geopandas as gpd
pd.set_option('display.max_columns',None) 

#Step 2: Import Census Block map and data
cbg_grids_name = "cb_2021_36_bg_500k.shp" 
nyc_geoids, cbgs_nyc = read_grids(cbg_grids_name, grid_name = 'Census Blocks') 
print(cbgs_nyc.head(3)) 

#Step 3: Import Taxi Zone map and data
taxi_grids_name = "geo_export_e612eba5-03f4-49f0-a0ac-528f1c3802b8.shp" 
taxi_zones = read_grids(taxi_grids_name, grid_name = 'taxi zones') 
print(taxi_zones.head(3)) 

cbgs_nyc = map_to_taxiZones(cbgs_nyc, taxi_zones) 
print(cbgs_nyc.head(3)) 

#Step 4: Define the Astoria boundaries using coordinates
# Coordinates for Astoria boundaries (following the general neighborhood boundaries)
astoria_coords = [
    (-73.9326, 40.7723),  # Northwest corner (near Astoria Park)
    (-73.9096, 40.7716),  # Northeast corner (near LaGuardia Airport)
    (-73.9132, 40.7637),  # East point (near 49th Street)
    (-73.9220, 40.7563),  # Southeast corner (near Northern Blvd)
    (-73.9387, 40.7574),  # Southwest corner (near 36th Avenue)
    (-73.9428, 40.7686),  # West point (near 21st Street)
    (-73.9326, 40.7723)   # Back to start to close the polygon
]

# Create a polygon and convert to GeoDataFrame
astoria_polygon = Polygon(astoria_coords)
attraction_zone = gpd.GeoDataFrame(
    {'geometry': [astoria_polygon]}, 
    crs="EPSG:4326"  # WGS84 coordinate system
)
# Convert to the same CRS as taxi zones if needed
attraction_zone = attraction_zone.to_crs(taxi_zones.crs)

#Step 5: Map what we've done so far
fig, ax = plt.subplots(figsize = (10,10))
taxi_zones.plot(ax=ax)
attraction_zone.plot(ax=ax, color='red', alpha=0.7)
plt.show()

#Step 6: Import mobile phone Data
file_name = 'data/poi_NY_initial_subset.csv'
geo_data = read_data(file_name)
print(geo_data.head(5))
geo_data = geo_data[geo_data.within(attraction_zone.loc[0,'geometry'])]
geo_data = geo_data[~geo_data['visitor_home_cbgs'].isna()][['location_name','visitor_home_cbgs']] #clean data
visits = count_visits(geo_data, nyc_geoids)
print(visits.head(4))

#Step 7: Merge the origin of the mobile phone data with their corresponding Taxi Zones
merged = pd.merge(cbgs_nyc, visits, left_on = 'GEOID', right_on = 'geoid', how = 'right' )[['taxi_object_id','visitor_cnt','geometry','geoid','GEOID']]
merged = merged[~merged['taxi_object_id'].isna()]
print(merged.head(2))
visitor_counts = pd.DataFrame(merged.groupby('taxi_object_id')['visitor_cnt'].sum()).reset_index(drop=False)
visitor_counts = pd.merge(taxi_zones, visitor_counts, left_on='objectid', right_on='taxi_object_id', how='right' )  
print(visitor_counts.sort_values("taxi_object_id").head(3))

#Step 8: Map the results so far
fig, ax = plt.subplots(figsize=(10,10))
cbgs_nyc.plot(ax=ax, alpha=0.7) #, column='objectid'
tmp = visitor_counts[~visitor_counts['geometry'].isna()] #viridis, RdBu
tmp.plot(column = 'visitor_cnt', ax = ax, legend=True, cmap='viridis',legend_kwds={'loc': 'upper left'},
    scheme ='User_Defined', #quantiles
    classification_kwds =dict(bins=[ 8,20, 60, 100, 150, 250,300, 500])) #[4, 8, 50, 100, 200, merged['cnt'].max()]
ax.get_legend().set_title("Astoria Visitor Counts")
attraction_zone.plot(ax=ax, color='red', alpha = 0.4)
plt.show()

#Step 9: Import the Yellow Taxi data
taxi_data = pd.read_parquet('data/yellow_tripdata_2022-12.parquet')
print('1-month taxi data count ', len(taxi_data))
print(taxi_data.head(3))

#Step 10: Define Astoria taxi zones
AttDO_zones = taxi_zones[taxi_zones.intersects(attraction_zone.loc[0,'geometry'])]
print(AttDO_zones.head(4)) 

fig, ax = plt.subplots(figsize = (5,5))
AttDO_zones.plot(ax = ax)
attraction_zone.plot(ax=ax, color='red', alpha = 0.6)
plt.show()
AttDO_zones_ids = AttDO_zones['objectid'].unique().tolist()
print('taxi zone IDs within the attraction region: ', AttDO_zones_ids)

#Step 11: Isolate data to Astoria
taxi_data = taxi_data[taxi_data['DOLocationID'].isin(AttDO_zones_ids)] # AttDO: attraction drop off zone id
print(taxi_data.head(5))
trip_passenger_counts = pd.DataFrame(taxi_data.groupby('PULocationID')['passenger_count'].sum()).reset_index(drop=False)
print(trip_passenger_counts.head(5))
#Step 12: Draw new map
visitor_counts_wTaxi_use = pd.merge(visitor_counts, trip_passenger_counts, left_on = 'taxi_object_id', right_on = 'PULocationID', how = 'left' )
print(len(visitor_counts_wTaxi_use))
print(visitor_counts_wTaxi_use.head(2))
fig, ax = plt.subplots(figsize=(10,10))
plt.axis('off')
cbgs_nyc.plot(ax=ax, alpha=0.7) #, column='objectid'
visitor_counts_wTaxi_use.plot(column = 'passenger_count', ax = ax, legend=True, cmap='viridis',legend_kwds={'loc': 'upper left'},
        scheme = 'User_Defined', #quantiles
        classification_kwds =dict(bins=[ 25,50,100, 1000,5000, 10000, 20000, 30000])) #[4, 8, 50, 100, 200, merged['cnt'].max()]
ax.get_legend().set_title("Taxi Passengers Count")
attraction_zone.plot(ax=ax, color='red', alpha = 0.4)
plt.show()

#Step 13: The ratio map
comparison_data = visitor_counts_wTaxi_use[['taxi_object_id',	'visitor_cnt','passenger_count', 'geometry']]
comparison_data['ratio'] = comparison_data['passenger_count']/comparison_data['visitor_cnt']
print(comparison_data.head(5))
fig, ax = plt.subplots(figsize=(10,10))
cbgs_nyc.plot(ax=ax, alpha=0.7) 
plt.axis('off')
comparison_data.plot(column = 'ratio', ax = ax, legend=True, cmap='viridis',legend_kwds={'loc': 'upper left'},
        scheme = 'User_Defined', #, #quantiles, User_Defined
        classification_kwds =dict(bins=[ 0.03, 0.08, 0.81,10, 66.2, 100, 200, 500, 1200])) #[4, 8, 50, 100, 200, merged['cnt'].max()]
ax.get_legend().set_title("Ratio of taxi use over visitor cnt")
attraction_zone.plot(ax=ax, color='red', alpha = 0.4)
plt.show()

#Step 14: ML Analysis
print("\n" + "="*50)
print("Starting Machine Learning Analysis")
print("="*50)

from ml_analysis import (
    prepare_features,
    train_visitor_prediction_model,
    cluster_visitor_origins,
    analyze_transportation_patterns,
    plot_analysis_results
)

print("\nPreparing input data...")
print("Visitor data columns:", visitor_counts_wTaxi_use.columns.tolist())
print("Taxi data columns:", taxi_data.columns.tolist())

# Prepare features for ML
features_df = prepare_features(visitor_counts_wTaxi_use, taxi_data)

if features_df is not None:
    # Train visitor prediction model
    print("\nTraining visitor prediction model...")
    model, feature_importance = train_visitor_prediction_model(features_df)
    
    if feature_importance is not None:
        print("\nTop 5 most important features for predicting visitors:")
        print(feature_importance.head())

    # Cluster visitor origins
    print("\nClustering visitor origins...")
    clustered_data, cluster_centers = cluster_visitor_origins(visitor_counts_wTaxi_use)

    if clustered_data is not None:
        # Analyze transportation patterns
        print("\nAnalyzing transportation patterns...")
        transport_analysis = analyze_transportation_patterns(visitor_counts_wTaxi_use, taxi_data)

        if transport_analysis is not None:
            # Plot results
            print("\nGenerating analysis visualizations...")
            analysis_fig = plot_analysis_results(
                visitor_counts_wTaxi_use,
                clustered_data,
                transport_analysis
            )

            if analysis_fig is not None:
                plt.show()

                # Print insights
                print("\nKey Insights:")
                if model is not None and hasattr(model, 'feature_names_in_'):
                    print("1. Visitor Prediction Model Performance:")
                    print(f"   - Model can explain {model.score(features_df[model.feature_names_in_], features_df['visitor_cnt']):.1%} of visitor count variation")

                if transport_analysis is not None:
                    print("\n2. Transportation Patterns:")
                    print(f"   - Average taxi usage ratio: {transport_analysis['taxi_ratio'].mean():.2f}")
                    high_usage = transport_analysis[transport_analysis['taxi_usage_category'] == 'High']
                    print(f"   - Areas with highest taxi usage: {len(high_usage)} zones")

                # Save the model and analysis results
                if model is not None:
                    import joblib
                    joblib.dump(model, 'astoria_visitor_model.joblib')
                    print("\nModel saved as 'astoria_visitor_model.joblib' for future predictions on Astoria")
            else:
                print("Error: Could not generate visualization plots")
        else:
            print("Error: Could not complete transportation pattern analysis")
    else:
        print("Error: Could not complete visitor origin clustering")
else:
    print("Error: Could not prepare features for analysis")
