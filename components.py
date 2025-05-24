# gradio_interface.py
from data_utils import load_data, get_cluster_result, get_geojson_with_cluster
import gradio as gr
import folium
from branca.element import Figure
import os
import uuid # For unique filenames

# This constant must match the directory name mounted in app.py
STATIC_MAPS_DIR = "static_maps"

# Define cluster colors globally
cluster_colors = {
    0: "green",
    1: "blue",
    2: "purple",
    3: "orange",
    -1: "red"
}

def show_results(year):
    # Load raw data
    raw_data = load_data()
    cluster_result = get_cluster_result(raw_data, year)

    # Prepare the text output for cluster details
    output_text = f"### Hasil Clustering DBSCAN Tahun {year}\n"
    for cluster_id in sorted(cluster_result['Cluster'].unique()):
        provinsi = cluster_result[cluster_result['Cluster'] == cluster_id]['Province'].tolist()
        cl_name = f"Cluster {cluster_id}" if cluster_id != -1 else "Outlier (-1)"
        output_text += f"\n- **{cl_name}**:\n  - " + "\n  - ".join(provinsi)

    # Get GeoJSON data merged with cluster results
    merged = get_geojson_with_cluster(cluster_result)

    # Initialize Folium map
    m = folium.Map(location=[-2.5, 117], zoom_start=5)

    # Add GeoJSON layers for each cluster
    for cluster in sorted(merged["Cluster"].unique()):
        cluster_df = merged[merged["Cluster"] == cluster]
        color = cluster_colors.get(cluster, "gray")

        folium.GeoJson(
            cluster_df,
            name=f"Cluster {cluster}" if cluster != -1 else "Outlier",
            style_function=lambda x, color=color: {
                "fillColor": color,
                "color": "black",
                "weight": 1,
                "fillOpacity": 0.5
            }
        ).add_to(m)

    # Add a layer control to toggle clusters on/off
    folium.LayerControl().add_to(m)

    # --- Save the Folium map to a file in the static directory ---
    # Generate a unique filename to avoid conflicts
    unique_id = uuid.uuid4().hex
    map_filename = f"cluster_map_{year}_{unique_id}.html"
    map_filepath = os.path.join(STATIC_MAPS_DIR, map_filename)

    # Ensure the directory exists before saving (though app.py creates it)
    os.makedirs(STATIC_MAPS_DIR, exist_ok=True)
    m.save(map_filepath)

    # Return a link that FastAPI will serve.
    # The '/maps/' path corresponds to the StaticFiles mount in app.py.
    # The `target="_blank"` ensures it opens in a new tab.
    map_link_html = f'<p><a href="/maps/{map_filename}" target="_blank">Click to open map for {year} in new tab</a></p>'

    return output_text, map_link_html

def build_interface():
    """
    Builds and returns the Gradio interface object.
    """
    return gr.Interface(
        fn=show_results,
        inputs=gr.Dropdown(choices=["2021", "2022", "2023"], label="Pilih Tahun"),
        outputs=[gr.Markdown(), gr.HTML()], # HTML for the link
        title="Visualisasi Clustering DBSCAN",
        description="Pilih tahun dan lihat hasil clustering baik dalam bentuk daftar maupun peta geografis."
    )

# No `if __name__ == "__main__":` block here!