import gradio as gr
import numpy as np

# --- 1. The Computer Graphics Algorithm (Bresenham) ---
# 定义 Canvas 尺寸
CANVAS_WIDTH = 600
CANVAS_HEIGHT = 400

def bresenham_line_algorithm(start_x, start_y, end_x, end_y):
    """
    实现 Bresenham's Line Algorithm，将线绘制到 NumPy 数组上。
    """
    # 创建一个白色底色的 Canvas (H, W, 3)
    canvas = np.ones((CANVAS_HEIGHT, CANVAS_WIDTH, 3), dtype=np.uint8) * 255
    
    # 绘制一个浅灰色的网格 (可选，但有助于看出像素点)
    canvas[::20, :, :] = 240
    canvas[:, ::20, :] = 240

    # 确保坐标为整数
    x0, y0 = int(round(start_x)), int(round(start_y))
    x1, y1 = int(round(end_x)), int(round(end_y))

    # 边界检查，确保坐标在 Canvas 范围内
    x0 = np.clip(x0, 0, CANVAS_WIDTH - 1)
    y0 = np.clip(y0, 0, CANVAS_HEIGHT - 1)
    x1 = np.clip(x1, 0, CANVAS_WIDTH - 1)
    y1 = np.clip(y1, 0, CANVAS_HEIGHT - 1)

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    
    err = dx - dy # 初始误差

    while True:
        # 绘制当前像素点 (设置为红色 [255, 0, 0])
        # 绘制一个 3x3 的方块以使像素点更明显
        canvas[y0-1:y0+2, x0-1:x0+2] = [255, 0, 0] 

        if x0 == x1 and y0 == y1:
            break
            
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
            
    return canvas

# --- 2. The Custom Javascript for Interaction ---
# 移除了您之前代码中用于触发 Gradio 按钮的部分，改为使用 CustomEvent。
canvas_js = f"""
<div id="canvas-container" style="position: relative; width: {CANVAS_WIDTH}px; height: {CANVAS_HEIGHT}px; margin: 0 auto; border: 2px solid #333; cursor: crosshair; background-color: #f0f0f0;">
    <canvas id="drawingLayer" width="{CANVAS_WIDTH}" height="{CANVAS_HEIGHT}" style="position: absolute; top: 0; left: 0;"></canvas>
    <div style="position: absolute; bottom: 10px; right: 10px; color: #555; pointer-events: none; user-select: none;">
        在灰色区域拖动鼠标绘制线条
    </div>
</div>

<script>
// 等待元素加载
setTimeout(() => {{
    const canvas = document.getElementById('drawingLayer');
    const ctx = canvas.getContext('2d');
    let isDrawing = false;
    let startX = 0;
    let startY = 0;

    // 清除并绘制半透明预览线 (只在客户端显示)
    function drawPreview(x1, y1, x2, y2) {{
        ctx.clearRect(0, 0, canvas.width, canvas.height); // 清除上一帧
        
        // 绘制预览线
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.strokeStyle = 'rgba(0, 0, 255, 0.5)'; // 半透明蓝色预览线
        ctx.lineWidth = 2;
        ctx.stroke();
    }}

    canvas.addEventListener('mousedown', (e) => {{
        isDrawing = true;
        const rect = canvas.getBoundingClientRect();
        startX = e.clientX - rect.left;
        startY = e.clientY - rect.top;
        drawPreview(startX, startY, startX, startY);
    }});

    canvas.addEventListener('mousemove', (e) => {{
        if (!isDrawing) return;
        const rect = canvas.getBoundingClientRect();
        const currentX = e.clientX - rect.left;
        const currentY = e.clientY - rect.top;
        drawPreview(startX, startY, currentX, currentY);
    }});

    canvas.addEventListener('mouseup', (e) => {{
        if (!isDrawing) return;
        isDrawing = false;
        
        const rect = canvas.getBoundingClientRect();
        const endX = e.clientX - rect.left;
        const endY = e.clientY - rect.top;

        // 鼠标释放后，清除客户端的预览线，让服务器返回的图像更清晰
        ctx.clearRect(0, 0, canvas.width, canvas.height); 

        // --- 触发 Gradio 后端调用 ---
        window.dispatchEvent(new CustomEvent("coords_ready", {{
            detail: {{ x1: startX, y1: startY, x2: endX, y2: endY }}
        }}));
    }});
}}, 1000);
</script>
"""

# --- 3. The Gradio Application Structure ---

with gr.Blocks(title="CG Algorithms Canvas") as demo:
    gr.Markdown("# 🖥️ 计算机图形学：Bresenham's 直线算法演示")
    gr.Markdown(
        "**操作说明：** 在左侧 **灰色区域** 点击并拖动鼠标绘制一条线段。JavaScript 将捕获坐标，并发送给 Python 后端，由 Bresenham 算法精确计算并返回右侧的 **红色像素点** 图像。"
    )
    
    with gr.Row():
        # 左侧列：用户输入/Canvas
        with gr.Column(scale=1):
            gr.Markdown("### 1. 客户端交互区域 (HTML Canvas)")
            gr.HTML(canvas_js)
            
            # 隐藏的输入框，用于接收 JS 传来的坐标
            with gr.Group(visible=False):
                in_x1 = gr.Number(label="X1")
                in_y1 = gr.Number(label="Y1")
                in_x2 = gr.Number(label="X2")
                in_y2 = gr.Number(label="Y2")

        # 右侧列：算法输出
        with gr.Column(scale=1):
            gr.Markdown("### 2. 服务器端渲染结果 (Bresenham 像素点)")
            output_image = gr.Image(
                label="Bresenham 精确像素线", 
                type="numpy",
                interactive=False,
                height=CANVAS_HEIGHT,
                width=CANVAS_WIDTH
            )

    # --- 4. JavaScript 到 Python 的桥接逻辑 ---
    js_handler = """
    (x1, y1, x2, y2) => {
        return new Promise((resolve) => {
            // 监听 JavaScript Canvas 触发的 custom event
            window.addEventListener('coords_ready', (e) => {
                // 将坐标作为值返回，Gradio 会自动填充到 outputs 中
                resolve([e.detail.x1, e.detail.y1, e.detail.x2, e.detail.y2]);
            }, { once: true }); // 只监听一次，避免重复触发
        });
    }
    """

    # 1. 在页面加载时，绑定 JS 监听器
    demo.load(
        fn=None, 
        inputs=None, 
        outputs=[in_x1, in_y1, in_x2, in_y2], 
        js=js_handler
    )
    
    # 2. 当隐藏的输入框值发生变化时 (即 JS 成功写入坐标后)，触发 Python 函数
    in_y2.change(
        fn=bresenham_line_algorithm,
        inputs=[in_x1, in_y1, in_x2, in_y2],
        outputs=output_image
    )

if __name__ == "__main__":
    # 使用 share=True 可以生成一个临时的公共链接
    demo.launch()