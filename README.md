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

    import matplotlib.pyplot as plt <br/>
    import pandas as pd <br/>
    from data_reader import read_data <br/>
    from grid_reader import read_grids <br/>
    from grid_mapper import map_to_taxiZones <br/>
    from visit_counter import count_visits <br/>
    pd.set_option('display.max_columns',None) <br/>

Next, we need to import our data files and associated maps:

This code will import the census block map and data (copy and paste under step 2):
    
    cbg_grids_name = "cb_2021_36_bg_500k.shp" <br/>
    nyc_geoids, cbgs_nyc = read_grids(cbg_grids_name, grid_name = 'Census Blocks') <br/>
    print(cbgs_nyc.head(3)) <br/>
        
This code will import the taxi zone map and taxi data (copy and paste under step 3):
    
    taxi_grids_name = "geo_export_e612eba5-03f4-49f0-a0ac-528f1c3802b8.shp" <br/>
    taxi_zones = read_grids(taxi_grids_name, grid_name = 'taxi zones') <br/>
    print(taxi_zones.head(3)) <br/>

    cbgs_nyc = map_to_taxiZones(cbgs_nyc, taxi_zones) <br/>
    print(cbgs_nyc.head(3)) <br/>
        
This code will import the boundary for Hudson Yards (copy and paste under step 4):
    
    grids_name = "Hudson_Yards_Cut.shp" <br/>
    attraction_zone = read_grids(grids_name, grid_name = 'attraction') <br/>

Let’s put what we have so far all together into one map (copy and paste under step 5):

    fig, ax = plt.subplots(figsize = (10,10))
    taxi_zones.plot(ax=ax)
    attraction_zone.plot(ax=ax, color='red', alpha=0.7)
    plt.show()
    
Run the code using the green play button in the top left. 

Let’s start looking at mobile phone data. 

This code will isolate the mobile phone data to only show trips to Hudson Yards (copy and paste under step 6).
    
    file_name = 'data/poi_NY_initial_subset.csv'
    geo_data = read_data(file_name)
    print(geo_data.head(5))
    geo_data = geo_data[geo_data.within(attraction_zone.loc[0,'geometry'])]
    geo_data = geo_data[~geo_data['visitor_home_cbgs'].isna()][['location_name','visitor_home_cbgs']] #clean data
    visits = count_visits(geo_data, nyc_geoids)
    print(visits.head(4))
        
This code will match that data to the taxi zones we have defined (copy and paste under step 7). 

Let’s check in on our progress.

This code gives a “heat map” of where people are coming from when they travel to Hudson Yards (copy and paste under step 8). 
    
    [code]

Run the code using the green play button in the top left. 

Next, we will make our taxi trip map

This code does something

    [code]

Now, we want to look at the ratio of trips taken by taxi vs the total trips taken.

This "ratio map" shows us each taxi zone and the ratio of trips taken by taxi vs the total trips taken from that zone (from the mobile phone data).




With our final maps done and dusted, think about what our maps tell us about transportation infrastructure needs.



    
