# data_utils.py (versi refactor)
import pandas as pd
import geopandas as gpd
from sklearn.preprocessing import RobustScaler
from sklearn.cluster import DBSCAN
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


province_name_map = {
    'Jakarta Raya': 'DKI Jakarta',
    'Kepulauan Riau': 'Kep. Riau',
    'Yogyakarta': 'DI Yogyakarta',
    'Bangka-Belitung': 'Kep. Bangka Belitung',
    'North Kalimantan': 'Kalimantan Utara'
}

@lru_cache(maxsize=1)
def load_data():
    """Loads the main data from CSV with caching."""
    try:
        data = pd.read_csv("Hasil_Gabungan.csv")
        logger.info(f"Successfully loaded data. Shape: {data.shape}")
        return data
    except FileNotFoundError:
        logger.error("Error: Hasil_Gabungan.csv not found. Please ensure the file is in the correct directory.")
        raise
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

@lru_cache(maxsize=1)
def load_geo():
    """Loads the geospatial data from JSON with caching and province name mapping."""
    try:
        geo = gpd.read_file("id.json")
        geo['name'] = geo['name'].replace(province_name_map)
        logger.info(f"Successfully loaded geospatial data. Shape: {geo.shape}")
        return geo
    except FileNotFoundError:
        logger.error("Error: id.json not found. Please ensure the file is in the correct directory.")
        raise
    except Exception as e:
        logger.error(f"Error loading geo data: {e}")
        raise

def get_cluster_result(eps: float, min_samples: int):
    data = load_data()
    features = [
        'Residential_2021', 'Business_2021', 'Industrial_2021', 'Social_2021',
        'Gov_Office_2021', 'Pub_Street_2021', 'Total_2021', 'JP_2021', 'KP_2021',
        'Residential_2022', 'Business_2022', 'Industrial_2022', 'Social_2022',
        'Gov_Office_2022', 'Pub_Street_2022', 'Total_2022', 'JP_2022', 'KP_2022',
        'Residential', 'Business', 'Industrial', 'Social',
        'Gov_Office', 'Pub_Street', 'Total', 'JP_2023', 'KP_2023'
    ]
    missing_features = [f for f in features if f not in data.columns]
    if missing_features:
        logger.error(f"Missing features in data: {missing_features}")
        raise ValueError(f"Missing features in data: {missing_features}")

    scaler = RobustScaler()
    scaled = scaler.fit_transform(data[features])
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    clusters = dbscan.fit_predict(scaled)

    result = data.copy()
    result['Cluster'] = clusters
    logger.info(f"Clustering complete. Found {len(set(clusters))} clusters (including -1 for outliers).")
    return result

def get_geojson_with_cluster(clustered_data: pd.DataFrame):
    geo = load_geo()
    if 'Province' not in clustered_data.columns:
        logger.error("Column 'Province' not found in clustered_data for merging.")
        raise ValueError("clustered_data must contain a 'Province' column.")
    merged_gdf = geo.merge(clustered_data, left_on="name", right_on="Province", how='left')
    unmatched_geo = merged_gdf[merged_gdf['Cluster'].isna()]
    if not unmatched_geo.empty:
        logger.warning(f"Provinces in GeoJSON not found in clustered data (will be assigned Cluster -1 if not already): {unmatched_geo['name'].tolist()}")
        merged_gdf['Cluster'] = merged_gdf['Cluster'].fillna(-1).astype(int)

    logger.info("GeoJSON merged with cluster results.")
    return merged_gdf
