import gradio as gr
import numpy as np

def draw_bresenham_line(x0, y0, x1, y1):
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    canvas = np.ones((600, 600, 3), dtype=np.uint8) * 255  # White background
    
    # Bresenham's line algorithm implementation
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    
    while True:
        if 0 <= x0 < 600 and 0 <= y0 < 600:
            canvas[y0, x0] = [0, 0, 255]  # Red pixel for the line
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy
    
    return canvas

with gr.Blocks(title="Bresenham's Line Algorithm Demo") as demo:
    gr.Markdown("""
    # Computer Graphics Algorithm Demo: Bresenham's Line Drawing
    
    This Gradio app implements the classic **Bresenham's line algorithm**, a fundamental computer graphics technique for rasterizing straight lines efficiently using only integer operations.
    
    Enter the start and end coordinates (0-599) and click "Draw" to see the line plotted on a 600x600 canvas.
    """)
    
    with gr.Row():
        x0 = gr.Number(label="Start X", value=50, precision=0, minimum=0, maximum=599)
        y0 = gr.Number(label="Start Y", value=50, precision=0, minimum=0, maximum=599)
        x1 = gr.Number(label="End X", value=550, precision=0, minimum=0, maximum=599)
        y1 = gr.Number(label="End Y", value=550, precision=0, minimum=0, maximum=599)
    
    btn = gr.Button("Draw Line", variant="primary")
    
    canvas_output = gr.Image(label="Rasterized Line", width=600, height=600)
    
    btn.click(
        fn=draw_bresenham_line,
        inputs=[x0, y0, x1, y1],
        outputs=canvas_output
    )
    
    gr.Examples(
        examples=[
            [50, 50, 550, 550],
            [50, 550, 550, 50],
            [100, 200, 500, 300],
            [300, 100, 300, 500],  # Vertical line
            [100, 300, 500, 300],  # Horizontal line
        ],
        inputs=[x0, y0, x1, y1]
    )

# To run: 
demo.launch()