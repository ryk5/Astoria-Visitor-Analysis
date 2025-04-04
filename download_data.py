import os
import requests
from pathlib import Path
import streamlit as st

def download_file(url, filename):
    """
    Download a file from a URL to the specified filename
    """
    print(f"Downloading {filename}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    file_path = Path("data") / filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print(f"Downloaded {filename}")

def main():
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # URLs for the data files
    data_urls = {
        "yellow_tripdata_2022-12.parquet": "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-12.parquet",
        "taxi_zones.zip": "https://data.cityofnewyork.us/api/geospatial/d3c5-ddgc?method=export&format=Shapefile"
    }
    
    print("Starting data download...")
    
    for filename, url in data_urls.items():
        try:
            download_file(url, filename)
        except Exception as e:
            print(f"Error downloading {filename}: {str(e)}")
            
    print("""
Download complete! 

Note: Some files still need to be downloaded manually:
1. Census Block Groups (cb_2021_36_bg_500k.shp) from US Census Bureau
2. Points of Interest data (poi_NY_initial_subset.csv) requires authorization

Please refer to the README for instructions on obtaining these files.
""")

if __name__ == "__main__":
    main() 