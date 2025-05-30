# components.py
import os
import gradio as gr
import folium
import tempfile
import time
import logging
from data_utils import get_cluster_result, get_geojson_with_cluster

logger = logging.getLogger("components")
logging.basicConfig(level=logging.INFO)


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
}
def create_map_html(geojson_df):
    m = folium.Map(location=[-2.5, 118], zoom_start=5)

    def style_function(feature):
        cluster = feature['properties'].get('Cluster', -1)
        return {
            'fillColor': cluster_colors.get(cluster, '#000000'),
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7,
        }

    # Ambil hanya kolom yang dibutuhkan
    gjson = geojson_df[['geometry', 'Cluster']]
    folium.GeoJson(
        gjson,
        style_function=style_function
    ).add_to(m)

    map_path = "maps/cluster_map.html"
    m.save(map_path)
    return f'<iframe src="/maps/cluster_map.html" width="100%" height="500"></iframe>'


def get_cluster_summary(clustered_df):
    text = "### Ringkasan Hasil Clustering:\n"
    for cluster_id in sorted(clustered_df['Cluster'].unique()):
        provinsi = clustered_df[clustered_df['Cluster'] == cluster_id]['Province'].tolist()
        cluster_name = f"Cluster {cluster_id}" if cluster_id != -1 else "**Outlier (-1)**"
        text += f"\n- {cluster_name}:\n  - " + "\n  - ".join(provinsi) + "\n"
    return text

def cluster_and_map(eps, min_samples):
    start_total = time.time()
    
    logger.info(f"[Input] eps={eps}, min_samples={min_samples}")

    start = time.time()
    clustered = get_cluster_result(eps, min_samples)
    logger.info(f"[Profiling] Clustering took {time.time() - start:.2f}s")

    start = time.time()
    geojson_df = get_geojson_with_cluster(clustered)
    logger.info(f"[Profiling] GeoJSON merge took {time.time() - start:.2f}s")
    
    start = time.time()
    html_map = create_map_html(geojson_df)
    logger.info(f"[Profiling] Map creation took {time.time() - start:.2f}s")

    summary = get_cluster_summary(clustered)
    logger.info(f"[Profiling] Total cluster_and_map took {time.time() - start_total:.2f}s")

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
        print("Button Clicked")
        print("processing")
        btn.click(
            cluster_and_map,
            inputs=[eps, min_samples],
            outputs=[output_table, output_map, output_text]
        )
    demo.queue(False) 
    return demo
