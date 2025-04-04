import os
import requests
from pathlib import Path
import streamlit as st
import zipfile
import tempfile

@st.cache_data
def download_file(url, filename):
    """
    Download a file from a URL to the specified filename with caching
    """
    try:
        with st.spinner(f"Downloading {filename}..."):
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            file_path = Path("data") / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            if filename.endswith('.zip'):
                with st.spinner(f"Extracting {filename}..."):
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(file_path.parent)
                    os.remove(file_path)  # Remove the zip file after extraction
            
            return True
    except Exception as e:
        st.error(f"Error downloading {filename}: {str(e)}")
        return False

def setup_data():
    """
    Download and setup all required data files
    """
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # URLs for the data files
    data_urls = {
        "yellow_tripdata_2022-12.parquet": "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-12.parquet",
        "taxi_zones.zip": "https://data.cityofnewyork.us/api/geospatial/d3c5-ddgc?method=export&format=Shapefile"
    }
    
    st.write("Setting up data files...")
    success = True
    
    for filename, url in data_urls.items():
        if not download_file(url, filename):
            success = False
    
    if success:
        st.success("Data files downloaded successfully!")
    else:
        st.warning("""
        Some files could not be downloaded. Note that some files need to be downloaded manually:
        1. Census Block Groups (cb_2021_36_bg_500k.shp) from US Census Bureau
        2. Points of Interest data (poi_NY_initial_subset.csv) requires authorization
        
        Please refer to the README for instructions on obtaining these files.
        """)
    
    return success

if __name__ == "__main__":
    setup_data() 