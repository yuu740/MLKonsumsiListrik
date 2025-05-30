# components.py
import os
import gradio as gr
import folium
import tempfile
from data_utils import get_cluster_result, get_geojson_with_cluster

cluster_colors = {
    -1: '#8c8c8c',
    0: '#1f78b4',
    1: '#33a02c',
    2: '#e31a1c',
    3: '#ff7f00',
    4: '#6a3d9a',
    5: '#b15928',
    6: '#a6cee3',
    7: '#b2df8a',
    8: '#fb9a99'
}

def create_map_html(geojson_df):
    m = folium.Map(location=[-2.5, 118], zoom_start=5)

    def style_function(feature):
        cluster = feature['properties']['Cluster']
        return {
            'fillColor': cluster_colors.get(cluster, '#000000'),
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7,
        }

    folium.GeoJson(
        geojson_df,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=['name', 'Cluster'], aliases=['Provinsi', 'Cluster'])
    ).add_to(m)

    return m._repr_html_()


def get_cluster_summary(clustered_df):
    text = "### Ringkasan Hasil Clustering:\n"
    for cluster_id in sorted(clustered_df['Cluster'].unique()):
        provinsi = clustered_df[clustered_df['Cluster'] == cluster_id]['Province'].tolist()
        cluster_name = f"Cluster {cluster_id}" if cluster_id != -1 else "**Outlier (-1)**"
        text += f"\n- {cluster_name}:\n  - " + "\n  - ".join(provinsi) + "\n"
    return text

def cluster_and_map(eps, min_samples):
    clustered = get_cluster_result(eps, min_samples)
    geojson_df = get_geojson_with_cluster(clustered)
    html_map = create_map_html(geojson_df)
    summary = get_cluster_summary(clustered)
    return clustered[['Province', 'Cluster']], html_map, summary

def build_interface():
    with gr.Blocks() as demo:
        gr.Markdown("## DBSCAN Clustering Seluruh Fitur Listrik Provinsi Indonesia")
        eps = gr.Slider(1.0, 10.0, value=6.0, step=0.1, label="Nilai eps")
        min_samples = gr.Slider(1, 30, value=16, step=1, label="Nilai min_samples")

        output_table = gr.DataFrame(headers=["Province", "Cluster"])
        output_map = gr.HTML()
        output_text = gr.Markdown()

        btn = gr.Button("Jalankan Clustering")
        btn.click(
            cluster_and_map,
            inputs=[eps, min_samples],
            outputs=[output_table, output_map, output_text]
        )

    return demo
