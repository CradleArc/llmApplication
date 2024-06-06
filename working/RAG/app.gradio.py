import gradio as gr
from common import *

with gr.Blocks(gr.themes.Soft(primary_hue=gr.themes.colors.slate, secondary_hue=gr.themes.colors.purple)) as demo:
    gr.Markdown('''# ErnieRAG''')
    with gr.Row():

        with gr.Column(scale=0.5, variant = 'panel'):
            gr.Markdown("## 上传知识库 & 创建向量 ")
            file = gr.File(type="file")
            with gr.Row(equal_height=True):
                with gr.Column(scale=1):
                    eb_token = gr.Textbox(label='输入AIStudio Token', type = "password")
            with gr.Row(equal_height=True):
                with gr.Column(scale=1, variant = 'panel'):
                    embedding_model = gr.Dropdown(choices= ["ernie-text-embedding"],
                    value="ernie-text-embedding",
                    label= "选择Embedding模型")

                with gr.Column(scale=1, variant='compact'):
                    vector_index_btn = gr.Button('创建向量数据库', variant='primary',scale=1)
                    vector_index_msg_out = gr.Textbox(show_label=False, lines=1,scale=1, placeholder="未创建向量数据库 ...")

            instruction = gr.Textbox(label="角色身份设定", lines=3, value="使用以下文段来回答最后的问题。仅根据给定的文段生成答案。如果你在给定的文段中没有找到任何与问题相关的信息，就说你不知道，不要试图编造答案。保持你的答案富有表现力。")

            with gr.Accordion(label="文本生成调整参数"):
                temperature = gr.Slider(label="temperature", minimum=0.1, maximum=1, value=0.1, step=0.05)
                top_p=gr.Slider(label="top_p", minimum=0, maximum=1, value=0.95, step=0.05)

            vector_index_btn.click(upload_and_create_vector_store,[file, eb_token],vector_index_msg_out)

        with gr.Column(scale=0.5, variant = 'panel'):
            gr.Markdown("## 选择大语言模型")

            with gr.Row(equal_height=True):
                with gr.Column(scale=1):
                    llm = gr.Dropdown(choices= ["ernie-turbo","ernie-4.0"],  value="ernie-4.0", label="选择对话模型")

            chatbot = gr.Chatbot([], elem_id="chatbot",
                                label='文心大模型', height=700, )

            txt = gr.Textbox(label= "提问区",lines=2,placeholder="请输入你的问题 ")

            with gr.Row():

                with gr.Column(scale=0.5):
                    submit_btn = gr.Button('确定提交',variant='primary', size = 'sm')

                with gr.Column(scale=0.5):
                    clear_btn = gr.Button('清空对话框',variant='stop',size = 'sm')

            submit_btn.click(add_text, [chatbot, txt], [chatbot, txt]).then(bot, [chatbot,llm,eb_token, instruction,temperature, top_p], chatbot)

            clear_btn.click(lambda: None, None, chatbot, queue=False)


if __name__ == '__main__':
    demo.queue()
    demo.launch(debug=True, share=True)