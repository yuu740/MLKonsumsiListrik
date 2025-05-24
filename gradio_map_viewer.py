import gradio as gr

def load_map():
    with open("map.html", "r", encoding="utf-8") as f:
        return f.read()

with gr.Blocks() as demo:
    gr.Markdown("### Interactive Map Display")
    btn = gr.Button("Load Map")
    output = gr.HTML()

    btn.click(fn=load_map, outputs=output)

demo.launch()