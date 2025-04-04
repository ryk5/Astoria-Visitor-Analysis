# Astoria Visitor Analysis

This project analyzes visitor patterns and taxi usage in the Astoria neighborhood of Queens, NYC. It uses mobile phone data and taxi trip data to understand movement patterns and transportation preferences in the area.

## Features

- Interactive visualization of Astoria neighborhood boundaries
- Analysis of visitor counts by zone
- Taxi passenger count analysis
- Ratio analysis of taxi usage to visitor count
- Machine learning model for visitor prediction

## Requirements

- Python 3.7+
- Required Python packages:
  - streamlit
  - matplotlib
  - pandas
  - geopandas
  - shapely
  - joblib
  - requests
  - mapclassify

## Data Requirements

The following data files are needed in the `data/` directory:
- `poi_NY_initial_subset.csv`: Points of Interest data with visitor information
- `yellow_tripdata_2022-12.parquet`: NYC Yellow Taxi trip data
- `cb_2021_36_bg_500k.shp`: Census Block Groups shapefile
- `geo_export_e612eba5-03f4-49f0-a0ac-528f1c3802b8.shp`: NYC Taxi Zone shapefile

### Downloading the Data

1. First, run the download script to get the taxi data and taxi zone shapefiles:
```bash
python download_data.py
```

2. For the remaining files:

   a. Census Block Groups shapefile:
   - Visit [US Census Bureau TIGER/Line Shapefiles](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html)
   - Download the 2021 Block Groups shapefile for New York
   - Extract and place the files in the `data/` directory

   b. Points of Interest data:
   - This data contains sensitive information and requires proper authorization
   - Contact the data administrator for access
   - Once obtained, place the file in the `data/` directory

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ryk5/Astoria-Visitor-Analysis.git
cd Astoria-Visitor-Analysis
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Download the required data:
```bash
python download_data.py
```

## Usage

1. Run the main analysis:
```bash
python lab.py
```

2. Launch the Streamlit dashboard:
```bash
streamlit run streamlit_app.py
```

## Project Structure

- `lab.py`: Main analysis script
- `streamlit_app.py`: Interactive dashboard
- `download_data.py`: Script to download required data files
- `data_reader.py`: Data loading utilities
- `grid_reader.py`: Grid/shapefile processing
- `grid_mapper.py`: Mapping utilities
- `visit_counter.py`: Visitor counting functions

## License

MIT License

## Author

Ryan Kim (rjk2189)

This tutorial guides you through the basic process of reading data and drawing conclusions on that data with python. 
No previous coding knowledge is required. All of the code is already written for you by Ethan!

First, if you haven't already done it, download Anaconda at this link "https://www.anaconda.com/download/success".
Once set up in Anaconda, navigate to Spyder.
To make sure our code can do everything we want it to do, we need to download python packages.
    These packages contain the special fuctions to read and map data so we don't have to write all of the code ourselves (when done right, coding is very open and collaborative!).
Type into your terminal:
    "pip install geopandas", and 
    "pip install mapclassify".

Now that we have everything set up, download the zip file in the GitHub repository (what we're in right now).
Unzip the file. It's okay to leave it in your downloads folder.
In the top right corner of Spyder, click on the file symbol to set your directory to the folder with lab.py in it.
In the top left corner of Spyder, click on the file symbol and open lab.py (in the same folder).

There's one more thing we have to do before coding. One of the data files (taxi data) we need was too big to put in this repository.
Go to this link: "https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page". 
We will be using taxi data from December 2022. Navigate to the yellow taxi data from December 2022 and download the set. 
Copy this file to your clipboard. Navigate to the "data" folder in the project folder and paste the file into it. 

We're ready to start coding! 
First, put your name and uni after author. This is customary when writing code. 

Next, we need to import the necessary libraries for reading data, drawing our maps, etc.
Copy and paste this code under step 1:

    import matplotlib.pyplot as plt 
    import pandas as pd 
    from data_reader import read_data 
    from grid_reader import read_grids 
    from grid_mapper import map_to_taxiZones 
    from visit_counter import count_visits 
    pd.set_option('display.max_columns',None) 

Next, we need to import our data files and associated maps:

This code will import the census block map and data (copy and paste under step 2):
    
    cbg_grids_name = "cb_2021_36_bg_500k.shp" 
    nyc_geoids, cbgs_nyc = read_grids(cbg_grids_name, grid_name = 'Census Blocks') 
    print(cbgs_nyc.head(3)) 
        
This code will import the taxi zone map and taxi data (copy and paste under step 3):
    
    taxi_grids_name = "geo_export_e612eba5-03f4-49f0-a0ac-528f1c3802b8.shp" 
    taxi_zones = read_grids(taxi_grids_name, grid_name = 'taxi zones') 
    print(taxi_zones.head(3)) 

    cbgs_nyc = map_to_taxiZones(cbgs_nyc, taxi_zones) 
    print(cbgs_nyc.head(3)) 
        
This code will import the boundary for Hudson Yards (copy and paste under step 4):
    
    grids_name = "Hudson_Yards_Cut.shp" 
    attraction_zone = read_grids(grids_name, grid_name = 'attraction') 

Let's put what we have so far all together into one map (copy and paste under step 5):

    fig, ax = plt.subplots(figsize = (10,10))
    taxi_zones.plot(ax=ax)
    attraction_zone.plot(ax=ax, color='red', alpha=0.7)
    plt.show()
    
Run the code using the green play button in the top left. 

Let's start looking at mobile phone data. 

This code will isolate the mobile phone data to only show trips to Hudson Yards (copy and paste under step 6).
    
    file_name = 'data/poi_NY_initial_subset.csv'
    geo_data = read_data(file_name)
    print(geo_data.head(5))
    geo_data = geo_data[geo_data.within(attraction_zone.loc[0,'geometry'])]
    geo_data = geo_data[~geo_data['visitor_home_cbgs'].isna()][['location_name','visitor_home_cbgs']] #clean data
    visits = count_visits(geo_data, nyc_geoids)
    print(visits.head(4))
        
This code will match that data to the taxi zones we have defined (copy and paste under step 7). 

    merged = pd.merge(cbgs_nyc, visits, left_on = 'GEOID', right_on = 'geoid', how = 'right' )[['taxi_object_id','visitor_cnt','geometry','geoid','GEOID']]
    merged = merged[~merged['taxi_object_id'].isna()]
    print(merged.head(2))
    visitor_counts = pd.DataFrame(merged.groupby('taxi_object_id')['visitor_cnt'].sum()).reset_index(drop=False)
    visitor_counts = pd.merge(taxi_zones, visitor_counts, left_on='objectid', right_on='taxi_object_id', how='right' )  
    print(visitor_counts.sort_values("taxi_object_id").head(3))

Let's check in on our progress.

This code gives a "heat map" of where people are coming from when they travel to Hudson Yards (copy and paste under step 8). 
    
    fig, ax = plt.subplots(figsize=(10,10))
    cbgs_nyc.plot(ax=ax, alpha=0.7) #, column='objectid'
    tmp = visitor_counts[~visitor_counts['geometry'].isna()] #viridis, RdBu
    tmp.plot(column = 'visitor_cnt', ax = ax, legend=True, cmap='viridis',legend_kwds={'loc': 'upper left'},
        scheme ='User_Defined', #quantiles
        classification_kwds =dict(bins=[ 8,20, 60, 100, 150, 250,300, 500])) #[4, 8, 50, 100, 200, merged['cnt'].max()]
    ax.get_legend().set_title("Hudson Yards Visitor Counts")
    attraction_zone.plot(ax=ax, color='red', alpha = 0.4)
    plt.show()

Run the code using the green play button in the top left. 

Next, we will make our taxi trip map:

This code extracts the taxi data (copy and paste under step 9).

    taxi_data = pd.read_parquet('data/yellow_tripdata_2022-12.parquet')
    print('1-month taxi data count ', len(taxi_data))
    print(taxi_data.head(3))

This code defines taxi zones that Hudson Yards contains (copy and paste under step 10):

    AttDO_zones = taxi_zones[taxi_zones.intersects(attraction_zone.loc[0,'geometry'])]
    print(AttDO_zones.head(4))

    fig, ax = plt.subplots(figsize = (5,5))
    AttDO_zones.plot(ax = ax)
    attraction_zone.plot(ax=ax, color='red', alpha = 0.6)
    plt.show()
    AttDO_zones_ids = AttDO_zones['objectid'].unique().tolist()
    print('taxi zone IDs within the attraction region: ', AttDO_zones_ids)

This code isolates the taxi data that goes into Hudson Yards (copy and paste under step 11):

    taxi_data = taxi_data[taxi_data['DOLocationID'].isin(AttDO_zones_ids)] # AttDO: attraction drop off zone id
    print(taxi_data.head(5))
    trip_passenger_counts = pd.DataFrame(taxi_data.groupby('PULocationID')['passenger_count'].sum()).reset_index(drop=False)
    print(trip_passenger_counts.head(5))

Now, we can map our progress again (copy and paste under step 12):

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

Run the code using the green play button in the top left. 

Now, we want to look at the ratio of trips taken by taxi vs the total trips taken.

This "ratio map" shows us each taxi zone and the ratio of trips taken by taxi vs the total trips taken from that zone (from the mobile phone data) (copy and paste under step 13).

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

Run the code using the green play button in the top left. 

With our final maps done and dusted, think about what our maps tell us about transportation infrastructure needs.



    
