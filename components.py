from data_utils import load_data, get_cluster_result, get_geojson_with_cluster
import gradio as gr
import folium
import tempfile
import os
import fastapi
from fastapi.staticfiles import StaticFiles
from gradio.routes import mount_gradio_app
import uvicorn

STATIC_PATH = "./static_maps"

os.makedirs(STATIC_PATH, exist_ok=True)

cluster_colors = {
    0: "green",
    1: "blue",
    2: "purple",
    3: "orange",
    -1: "red"
}

def show_results(year):
    raw_data = load_data()  
    cluster_result = get_cluster_result(raw_data, year)
    
    output_text = f"### Hasil Clustering DBSCAN Tahun {year}\n"
    # for c, prov_list in cluster_result.items():
    #     cl_name = f"Cluster {c}" if c != -1 else "Outlier (-1)"
    #     output_text += f"\n- **{cl_name}**:\n  - " + "\n  - ".join(str(prov) for prov in prov_list)
    for cluster_id in sorted(cluster_result['Cluster'].unique()):
        provinsi = cluster_result[cluster_result['Cluster'] == cluster_id]['Province'].tolist()
        cl_name = f"Cluster {cluster_id}" if cluster_id != -1 else "Outlier (-1)"
        output_text += f"\n- **{cl_name}**:\n  - " + "\n  - ".join(provinsi)
    

    merged = get_geojson_with_cluster(cluster_result)
    m = folium.Map(location=[-2.5, 117], zoom_start=5)
    # m = leafmap.Map(center=[-2.5, 117], zoom=5)
    
    for cluster in sorted(merged["Cluster"].unique()):
        cluster_df = merged[merged["Cluster"] == cluster]
        color = cluster_colors.get(cluster, "gray")
        # layer_name = f"Cluster {cluster}" if cluster != -1 else "Outlier"
        # m.add_gdf(cluster_df, layer_name=layer_name, fill_colors=[color])
        folium.GeoJson(
            cluster_df,
            name=f"Cluster {cluster}",
            style_function=lambda x, color=color: {
                "fillColor": color,
                "color": "black",
                "weight": 1,
                "fillOpacity": 0.5
            }
        ).add_to(m)
    # map_file = "map.html"
    # m.to_html(map_file)
    folium.LayerControl().add_to(m)
    # map_html = m.to_html(outfile=None)
    # map_html = m.get_root().render()
    # map_html = f"""
    # <iframe src="{map_file}" width="100%" height="600px" frameborder="0"></iframe>
    # """
    
    # with open(map_file, 'r', encoding='utf-8') as f:
    #     map_html = f.read()
    
    # with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
    #     m.save(tmp.name)
    #     tmp_path = tmp.name 

    # map_html = f'<iframe src="/file/{os.path.basename(tmp_path)}" width="100%" height="600px" frameborder="0"></iframe>'

    # os.remove(tmp.name) 
    
    map_filename = f"cluster_map_{year}.html"
    map_filepath = os.path.join(STATIC_PATH, map_filename)
    m.save(map_filepath)
    
    map_html = f'<iframe src="/file/{map_filename}" width="100%" height="600px" frameborder="0"></iframe>'

    return output_text, map_html
    # return output_text, map_html

app = fastapi.FastAPI()

app.mount("/file", StaticFiles(directory="."), name="static")


def build_interface():
    return gr.Interface(
        fn=show_results, 
        inputs=gr.Dropdown(choices=["2021", "2022", "2023"], label="Pilih Tahun"),
        outputs=[gr.Markdown(), gr.HTML()],

        title="Visualisasi Clustering DBSCAN",
        description="Pilih tahun dan lihat hasil clustering baik dalam bentuk daftar maupun peta geografis"
    )
    
# if __name__ == "__main__":
#     demo = build_interface()
#     demo.launch() 

app = mount_gradio_app(app, build_interface(), path="/")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)