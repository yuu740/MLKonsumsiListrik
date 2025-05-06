from data_utils import load_data, get_cluster_result, get_geojson_with_cluster
import gradio as gr
import leafmap.foliumap as leafmap

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
    for c, prov_list in cluster_result.items():
        cl_name = f"Cluster {c}" if c != -1 else "Outlier (-1)"
        output_text += f"\n- **{cl_name}**:\n  - " + "\n  - ".join(str(prov) for prov in prov_list)
    

    merged = get_geojson_with_cluster(cluster_result)
    m = leafmap.Map(center=[-2.5, 117], zoom=5)
    
    for cluster in sorted(merged["Cluster"].unique()):
        cluster_df = merged[merged["Cluster"] == cluster]
        color = cluster_colors.get(cluster, "gray")
        layer_name = f"Cluster {cluster}" if cluster != -1 else "Outlier"
        m.add_gdf(cluster_df, layer_name=layer_name, fill_colors=[color])

    map_file = "map.html"
    m.to_html(map_file)
    print(f"Peta disimpan di {map_file}")
    
    map_file_url = f"/{map_file}"
    
    map_html = f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="1;url={map_file_url}">
        </head>
        <body>
            <p>Redirecting to the map...</p>
        </body>
    </html>
    """
    
    return output_text, map_html  

def build_interface():
    return gr.Interface(
        fn=show_results, 
        inputs=gr.Dropdown(choices=["2021", "2022", "2023"], label="Pilih Tahun"),
        outputs=[gr.Markdown(), gr.HTML()],
        title="Visualisasi Clustering DBSCAN",
        description="Pilih tahun dan lihat hasil clustering baik dalam bentuk daftar maupun peta geografis"
    )
    
if __name__ == "__main__":
    demo = build_interface()
    demo.launch() 