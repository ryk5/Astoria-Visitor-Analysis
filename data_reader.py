
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def read_data(file_name):
    data = pd.read_csv(file_name) # mobile phone data
    # print(data.head(5))
    data = data[~data['longitude'].isna()].reset_index(drop=True) # clean data missing coordinates

    geometry_center = [Point(xy) for xy in zip( data.longitude, data.latitude)]
    data['geometry'] = geometry_center
    geo_data = gpd.GeoDataFrame(data, geometry='geometry')

    return geo_data