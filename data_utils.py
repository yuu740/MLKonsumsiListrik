import pandas as pd
import geopandas as gpd
from sklearn.preprocessing import RobustScaler
from sklearn.cluster import DBSCAN

def load_data():
    return pd.read_csv("Hasil_Gabungan.csv")

def get_cluster_result(data, year):
    if year == "2021":
        features = ['Residential_2021', 'Business_2021', 'Industrial_2021', 'Social_2021', 
                    'Gov_Office_2021', 'Pub_Street_2021', 'Total_2021', 'JP_2021', 'KP_2021']
    elif year == "2022":
        features = ['Residential_2022', 'Business_2022', 'Industrial_2022', 'Social_2022', 
                    'Gov_Office_2022', 'Pub_Street_2022', 'Total_2022', 'JP_2022', 'KP_2022']
    else:
        features = ['Residential', 'Business', 'Industrial', 'Social', 
                    'Gov_Office', 'Pub_Street', 'Total', 'JP_2023', 'KP_2023']

    scaler = RobustScaler()
    scaled = scaler.fit_transform(data[features])
    dbscan = DBSCAN(eps=6, min_samples=16)
    clusters = dbscan.fit_predict(scaled)

    data_copy = data.copy()
    data_copy['Cluster'] = clusters
    return data_copy

def get_geojson_with_cluster(data_with_cluster):
    geo = gpd.read_file("id.json")
    geo['name'] = geo['name'].replace({
        'Jakarta Raya': 'DKI Jakarta',
        'Kepulauan Riau': 'Kep. Riau',
        'Yogyakarta': 'DI Yogyakarta',
        'Bangka-Belitung': 'Kep. Bangka Belitung',
        'North Kalimantan': 'Kalimantan Utara'
    })

    merged = geo.merge(data_with_cluster, left_on="name", right_on="Province")
    return merged