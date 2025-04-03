
import geopandas as gpd
import matplotlib.pyplot as plt

def read_grids(grid_file_name,grid_name):
    fig, ax = plt.subplots(figsize = (15,10))
    if grid_name == 'Census Blocks':
        cbgs = gpd.read_file('shapefiles/cb_2021_36_bg_500k/' + grid_file_name)
        
        COUNTYFP = ['081','061','005','047','085']  # NYC 5 borough codes
        cbgs[cbgs['COUNTYFP'].isin( COUNTYFP )].plot(ax = ax)
        cbgs_nyc = cbgs[cbgs['COUNTYFP'].isin(COUNTYFP)].reset_index(drop=True)
        print('we have {} unique cbg zones in New York City in all 5 boroughs'.format(len(cbgs_nyc.GEOID.unique())))
        nyc_geoids = cbgs_nyc.GEOID.unique()
        return nyc_geoids, cbgs_nyc
    
    elif grid_name == 'taxi zones':
        taxi_zones = gpd.read_file( 'shapefiles/NYC Taxi Zones/' + grid_file_name)
        taxi_zones.plot(ax = ax)
        print('we have {} unique taxi zones'.format(len(taxi_zones.objectid.unique())))
        return taxi_zones
    
    elif grid_name == 'attraction':
        attraction = gpd.read_file( 'shapefiles/Hudson_Yards_Cut/' + grid_file_name)
        attraction.plot(ax = ax, color = 'red')
        return attraction

    else:
        return None