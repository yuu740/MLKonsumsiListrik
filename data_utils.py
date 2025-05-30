# data_utils.py
import pandas as pd
import geopandas as gpd
from sklearn.preprocessing import RobustScaler
from sklearn.cluster import DBSCAN

# Global cache
data = pd.read_csv("Hasil_Gabungan.csv")
geo = gpd.read_file("id.json")
geo['name'] = geo['name'].replace({
    'Jakarta Raya': 'DKI Jakarta',
    'Kepulauan Riau': 'Kep. Riau',
    'Yogyakarta': 'DI Yogyakarta',
    'Bangka-Belitung': 'Kep. Bangka Belitung',
    'North Kalimantan': 'Kalimantan Utara'
})

def get_cluster_result(eps: float, min_samples: int):
    features = [
        'Residential_2021', 'Business_2021', 'Industrial_2021', 'Social_2021',
        'Gov_Office_2021', 'Pub_Street_2021', 'Total_2021', 'JP_2021', 'KP_2021',
        'Residential_2022', 'Business_2022', 'Industrial_2022', 'Social_2022',
        'Gov_Office_2022', 'Pub_Street_2022', 'Total_2022', 'JP_2022', 'KP_2022',
        'Residential', 'Business', 'Industrial', 'Social',
        'Gov_Office', 'Pub_Street', 'Total', 'JP_2023', 'KP_2023'
    ]

    scaler = RobustScaler()
    scaled = scaler.fit_transform(data[features])
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    clusters = dbscan.fit_predict(scaled)

    result = data.copy()
    result['Cluster'] = clusters
    return result

def get_geojson_with_cluster(clustered_data: pd.DataFrame):
    return geo.merge(clustered_data, left_on="name", right_on="Province")
