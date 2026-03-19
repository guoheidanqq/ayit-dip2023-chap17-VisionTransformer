#该应用创建工具共包含三个区域，顶部工具栏，左侧代码区，右侧交互效果区，其中右侧交互效果是通过左侧代码生成的，存在对照关系。
#顶部工具栏：运行、保存、新开浏览器打开、实时预览开关，针对运行和在浏览器打开选项进行重要说明：
#[运行]：交互效果并非实时更新，代码变更后，需点击运行按钮获得最新交互效果。
#[在浏览器打开]：新建页面查看交互效果。
#以下为应用创建工具的示例代码

import gradio as gr
import numpy as np

# 1. 定义处理函数 (保持不变)
def process_canvas_drawing(img):
    if img is None:
        return "请在画布上绘制一些内容。"
    
    img_array = np.array(img)
    height, width, channels = img_array.shape
    pixels_drawn = np.sum(img_array[:, :, 3] > 0)
    
    return f"✅ 成功接收绘图数据！\n- 图像形状: {height} x {width} x {channels} (HWC, RGBA)\n- 绘制的像素数: {pixels_drawn}"

# 2. 创建 Gradio 界面
with gr.Blocks() as demo:
    gr.Markdown("## ✏️ Gradio Sketchpad 绘图示例")
    
    # 2.1 关键修改：使用 gr.Sketchpad 代替 gr.Image
    canvas_input = gr.Sketchpad(
        label="hello画布绘图区", 
        type="numpy",       # 将输出类型设置为 NumPy 数组
        image_mode="RGBA",
        height=300, 
        width=400
        # ⚠️ Sketchpad 组件通常不需要 'tool' 参数
    )
    
    # 2.2 创建输出组件和提交按钮
    output_text = gr.Textbox(label="处理结果")
    submit_btn = gr.Button("提交绘图进行处理")

    # 3. 绑定事件
    submit_btn.click(
        fn=process_canvas_drawing, 
        inputs=[canvas_input], 
        outputs=output_text
    )

# 4. 启动 Gradio 应用
demo.launch()
