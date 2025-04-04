#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 18:21:35 2025

@author: columbiauniversity
"""

#pip install geopandas
import matplotlib.pyplot as plt
import pandas as pd
from data_reader import read_data
from grid_reader import read_grids
from grid_mapper import map_to_taxiZones
from visit_counter import count_visits
pd.set_option('display.max_columns',None)

#census block
cbg_grids_name = "cb_2021_36_bg_500k.shp"
nyc_geoids, cbgs_nyc = read_grids(cbg_grids_name, grid_name = 'Census Blocks')
print(cbgs_nyc.head(3))

#taxi zones
taxi_grids_name = "geo_export_e612eba5-03f4-49f0-a0ac-528f1c3802b8.shp"
taxi_zones = read_grids(taxi_grids_name, grid_name = 'taxi zones')
print(taxi_zones.head(3))

#map census blocks to taxi zones
cbgs_nyc = map_to_taxiZones(cbgs_nyc, taxi_zones)
print(cbgs_nyc.head(3))

#define area of interest
grids_name = "Hudson_Yards_Cut.shp"
attraction_zone = read_grids(grids_name, grid_name = 'attraction')

#show what we've done so far (will show 4 maps)
fig, ax = plt.subplots(figsize = (10,10))
taxi_zones.plot(ax=ax)
attraction_zone.plot(ax=ax, color='red', alpha=0.7)
plt.show()

#mobile phone data
file_name = 'data/poi_NY_initial_subset.csv'
geo_data = read_data(file_name)
print(geo_data.head(5))
#find how many trips in Hudson Yards"
geo_data = geo_data[geo_data.within(attraction_zone.loc[0,'geometry'])]
geo_data = geo_data[~geo_data['visitor_home_cbgs'].isna()][['location_name','visitor_home_cbgs']] #clean data
visits = count_visits(geo_data, nyc_geoids)
print(visits.head(4))

#nerge the origin of  trips with  taxi zones
merged = pd.merge(cbgs_nyc, visits, left_on = 'GEOID', right_on = 'geoid', how = 'right' )[['taxi_object_id','visitor_cnt','geometry','geoid','GEOID']]
merged = merged[~merged['taxi_object_id'].isna()]
print(merged.head(2))
visitor_counts = pd.DataFrame(merged.groupby('taxi_object_id')['visitor_cnt'].sum()).reset_index(drop=False)
visitor_counts = pd.merge(taxi_zones, visitor_counts, left_on='objectid', right_on='taxi_object_id', how='right' )  
print(visitor_counts.sort_values("taxi_object_id").head(3))

#map the number of trips from each taxi zone to Hudson Yards
fig, ax = plt.subplots(figsize=(10,10))
cbgs_nyc.plot(ax=ax, alpha=0.7) #, column='objectid'
tmp = visitor_counts[~visitor_counts['geometry'].isna()] #viridis, RdBu
tmp.plot(column = 'visitor_cnt', ax = ax, legend=True, cmap='viridis',legend_kwds={'loc': 'upper left'},
        scheme ='User_Defined', #quantiles
        classification_kwds =dict(bins=[ 8,20, 60, 100, 150, 250,300, 500])) #[4, 8, 50, 100, 200, merged['cnt'].max()]
ax.get_legend().set_title("Hudson Yards Visitor Counts")
attraction_zone.plot(ax=ax, color='red', alpha = 0.4)
plt.show()

#extract taxi data
taxi_data = pd.read_parquet('data/yellow_tripdata_2022-12.parquet')
print('1-month taxi data count ', len(taxi_data))
print(taxi_data.head(3))

#Determine the taxi zones that Hudson Yards contains
AttDO_zones = taxi_zones[taxi_zones.intersects(attraction_zone.loc[0,'geometry'])]
print(AttDO_zones.head(4))

#Map out the intersection of Hudson Yards and Taxi Zones
fig, ax = plt.subplots(figsize = (5,5))
AttDO_zones.plot(ax = ax)
attraction_zone.plot(ax=ax, color='red', alpha = 0.6)
plt.show()
AttDO_zones_ids = AttDO_zones['objectid'].unique().tolist()
print('taxi zone IDs within the attraction region: ', AttDO_zones_ids)

#isolate the taxi data that goes to Hudson Yards
taxi_data = taxi_data[taxi_data['DOLocationID'].isin(AttDO_zones_ids)] # AttDO: attraction drop off zone id
print(taxi_data.head(5))

#aggregate the taxi data that goes to Hudson Yards
trip_passenger_counts = pd.DataFrame(taxi_data.groupby('PULocationID')['passenger_count'].sum()).reset_index(drop=False)
print(trip_passenger_counts.head(5))

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
