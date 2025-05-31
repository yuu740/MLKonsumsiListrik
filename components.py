# components.py
import os
import pandas as pd
import gradio as gr
import folium
import tempfile
import time
import logging
from data_utils import get_cluster_result, get_geojson_with_cluster

logger = logging.getLogger("components")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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

def create_map_html(geojson_df: pd.DataFrame):
    if geojson_df.empty:
        logger.warning("Input geojson_df is empty, cannot create map.")
        return "<p>Tidak ada data untuk membuat peta.</p>"
    m = folium.Map(location=[-2.5, 118], zoom_start=5)

    def style_function(feature):
        cluster = feature['properties'].get('Cluster', -1)
        return {
            'fillColor': cluster_colors.get(cluster, '#000000'),
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7,
        }
    if 'Cluster' not in geojson_df.columns:
        logger.error("Column 'Cluster' not found in geojson_df for map styling.")
        return "<p>Kolom 'Cluster' tidak ditemukan untuk pembuatan peta.</p>"


    gjson_data = geojson_df[['geometry', 'name', 'Cluster']].copy()
    gjson_data['Cluster'] = gjson_data['Cluster'].astype(int)

    folium.GeoJson(
        gjson_data.to_json(),
        style_function=style_function,
        tooltip=folium.features.GeoJsonTooltip(fields=['name', 'Cluster'], aliases=['Provinsi', 'Cluster ID'])
    ).add_to(m)

    temp_file_name = next(tempfile._get_candidate_names()) + ".html"
    map_path = os.path.join("maps", temp_file_name)
    try:
        m.save(map_path)
        logger.info(f"Map saved to {map_path}")
        return f'<iframe src="/maps/{temp_file_name}" width="100%" height="500px" style="border:none;"></iframe>'
    except Exception as e:
        logger.error(f"Error saving Folium map to {map_path}: {e}")
        return f"<p>Error saat membuat peta: {e}</p>"


def get_cluster_summary(clustered_df):
    if clustered_df.empty:
        return "### Ringkasan Hasil Clustering:\n\nTidak ada data clustering."
    text = "### Ringkasan Hasil Clustering:\n"
    if 'Cluster' not in clustered_df.columns:
        logger.error("Column 'Cluster' not found in clustered_df for summary.")
        return "### Ringkasan Hasil Clustering:\n\nKolom 'Cluster' tidak ditemukan."

    sorted_cluster_ids = sorted(clustered_df['Cluster'].unique())

    for cluster_id in sorted_cluster_ids:
        provinsi = clustered_df[clustered_df['Cluster'] == cluster_id]['Province'].tolist()
        cluster_name = f"Cluster {cluster_id}" if cluster_id != -1 else "**Outlier (-1)**"
        if provinsi:
            text += f"\n- {cluster_name}:\n  - " + "\n  - ".join(provinsi) + "\n"
        else:
            text += f"\n- {cluster_name}: (Tidak ada provinsi)\n"
    return text

def cluster_and_map(eps: float, min_samples: int):
    start_total = time.time()
    logger.info(f"[Input] eps={eps}, min_samples={min_samples}")

    try:
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

        return clustered[['Province', 'Cluster']].copy(), html_map, summary
    
    except Exception as e:
        logger.exception(f"Error during cluster_and_map process: {e}")
        error_msg = f"Terjadi kesalahan: {e}. Silakan periksa log untuk detail lebih lanjut."
        return pd.DataFrame(columns=['Province', 'Cluster']), f"<p>{error_msg}</p>", f"### Error:\n\n{error_msg}"

def build_interface():
    with gr.Blocks() as demo:
        gr.Markdown("## DBSCAN Clustering Seluruh Fitur Listrik Provinsi Indonesia")
        with gr.Row():
            with gr.Column(scale=1):
                eps = gr.Slider(1.0, 10.0, value=6.0, step=0.1, label="Nilai eps (Radius pencarian titik data)", min_width=300)
                min_samples = gr.Slider(1, 30, value=16, step=1, label="Nilai min_samples (Jumlah minimum sampel dalam radius)", min_width=300)
                btn = gr.Button("Jalankan Clustering")
            with gr.Column(scale=2):
                gr.Markdown(
                    """
                    **Penjelasan Parameter DBSCAN:**
                    - **`eps`**: Jarak maksimum antara dua sampel agar dianggap berada di lingkungan yang sama.
                      Nilai yang lebih kecil berarti cluster akan lebih padat.
                    - **`min_samples`**: Jumlah sampel (atau total bobot) dalam lingkungan suatu titik agar titik tersebut dianggap sebagai *core point*.
                      Nilai yang lebih tinggi berarti cluster akan membutuhkan lebih banyak titik untuk terbentuk.
                    """
                )

        with gr.Tabs():
            with gr.TabItem("Tabel Hasil Clustering"):
                output_table = gr.DataFrame(headers=["Province", "Cluster"])
            with gr.TabItem("Peta Hasil Clustering"):
                output_map = gr.HTML()
            with gr.TabItem("Ringkasan Clustering"):
                output_text = gr.Markdown()

        btn.click(
            cluster_and_map,
            inputs=[eps, min_samples],
            outputs=[output_table, output_map, output_text]
        )
    # demo.queue(True)
    return demo

