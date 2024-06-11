import time
import numpy as np
import streamlit as st
from utils import *
import erniebot
config = read_yaml("/home/aistudio/config.yaml")
import random
from PIL import Image
from vector_utils import DBUtils


from erniebot_agent.chat_models import ERNIEBot
from erniebot_agent.memory import WholeMemory
from erniebot_agent.agents import FunctionAgent
from Agent_tools import *


INPUT_TYPE = Union[str, Path]
width = config.get('logo_width')
logo_dir = config.get('logo')
img = Image.open(logo_dir)
class ERNIEAgent:
    def __init__(self, api_type: str = None, access_token: str = None, model_name: str = None):
        self.api_type = api_type
        self.access_token = access_token
        self.model_name = model_name
        os.environ["EB_AGENT_LOGGING_LEVEL"] = "INFO"
        os.environ["EB_AGENT_ACCESS_TOKEN"] = self.access_token

    async def __call__(self, prompt: str, tools=None):
        memory = WholeMemory()
        llm_final = ERNIEBot(model=self.model_name, api_type=self.api_type, enable_multi_step_tool_call=True)
        agent_all = FunctionAgent(llm=llm_final, tools=tools, memory=memory, max_steps=10)
        response = await agent_all.run(prompt)
        return response.text, response.steps, response.chat_history


class ErnieEncodeText:
    def __init__(self, api_type: str, access_token: str):
        self.api_type = api_type
        self.access_token = access_token
        erniebot.api_type = self.api_type
        erniebot.access_token = self.access_token

    def __call__(self, sentences: List[str]):
        if not isinstance(sentences, List):
            sentences = [sentences]

        time.sleep(random.randint(3, 10))
        response = erniebot.Embedding.create(
            model="ernie-text-embedding",
            input=sentences,
        )
        datas = response.get("data", None)
        if not datas:
            return None

        embeddings = np.array([v["embedding"] for v in datas])
        return embeddings


async def predict_only_model(text, model):
    params_dict = st.session_state["params"]
    response = await model(text, tools=[st.session_state["params"]["tools"]])
    bot_print(response[0])


def bot_print(content, avatar: str = "🤖"):
    with st.chat_message("assistant", avatar=avatar):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in content.split():
            full_response += chunk + " "
            time.sleep(0.01)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)


def tips(txt: str, wait_time: int = 2, icon: str = "🎉"):
    st.toast(txt, icon=icon)
    # time.sleep(wait_time)


@st.cache_resource
def init_encoder(encoder_name: str, api_type, access_token):
    if "ErnieBot-Text-Embedding" in encoder_name:
        return ErnieEncodeText(api_type, access_token)


def init_ui_parameters():
    sider_title = config.get('sidebar_title')
    st.sidebar.title(sider_title)
    st.sidebar.markdown('-----')     
    param = config.get("Parameter")
    param_max_length = param.get("max_length")
    param_top = param.get("top_p")
    param_temp = param.get("temperature")
    ProjectIntroduction = config.get('ProjectIntroduction')
    st.session_state["params"] = {}
    st.sidebar.markdown(ProjectIntroduction)
    st.sidebar.markdown('----')
    with st.sidebar.expander('🤖 LLM 模型选择'):
        model_name = st.selectbox(
            "模型名称",
            options=config.get("LLM_API"),
            help="提供对话能力的大语言模型",
        )
        st.session_state["params"]["model_name"] = model_name

        encoder_model = st.selectbox(
            "提取语义向量模型",
            options=config.get("Encoder"),
            help="提取语义向量模型",
        )
        st.session_state["params"]["encoder"] = encoder_model
        st.session_state["params"]["api_type"] = config.get("Encoder").get(encoder_model).get("api_type")
        TOP_OPTIONS = [5, 10, 15]
        search_top = st.selectbox("🔍 搜索 Top_K:", TOP_OPTIONS)
        st.session_state["params"]["search_top"] = search_top
        st.session_state["params"]["access_token"] = config.get("LLM_API").get(model_name).get("access_token")

    with st.sidebar.expander('🛠️ LLM 参数设置'):
        max_length = st.slider(
            "max_length",
            min_value=param_max_length.get("min_value"),
            max_value=param_max_length.get("max_value"),
            value=param_max_length.get("default"),
            step=param_max_length.get("step"),
            help=param_max_length.get("tip"),
        )
        st.session_state["params"]["max_length"] = max_length

        top_p = st.slider(
            "top_p",
            min_value=param_top.get("min_value"),
            max_value=param_top.get("max_value"),
            value=param_top.get("default"),
            step=param_top.get("step"),
            help=param_top.get("tip"),
        )
        st.session_state["params"]["top_p"] = top_p

        temperature = st.slider(
            "temperature",
            min_value=param_temp.get("min_value"),
            max_value=param_temp.get("max_value"),
            value=param_temp.get("default"),
            step=param_temp.get("step"),
            help=param_temp.get("tip"),
        )
        st.session_state["params"]["temperature"] = temperature


async def get_model_response(text, context, custom_prompt, model):
    params_dict = st.session_state["params"]

    s_model = time.perf_counter()
    prompt_msg = make_prompt(text, context, custom_prompt)
    # logger.info(f"Final prompt: \n{prompt_msg}\n")

    response, steps, chat_history = await model(prompt_msg, tools=[st.session_state["params"]["tools"]])
    elapse = time.perf_counter() - s_model

    # logger.info(f"Reponse of LLM: \n{response}\n")
    if not response:
        response = "抱歉，我并不能正确回答该问题。"
    return response, steps, chat_history, elapse


async def predict(text, search_res, model, custom_prompt=None):
    # for file, content in search_res.items():
    #     content = "\n".join(content)
    #     one_context = f"**从《{file}》** 检索到相关内容： \n{content}"
    #     bot_print(one_context, avatar="📄")
        # logger.info(f"Context:\n{one_context}\n")
    tips('检索完成，正在推理...', icon="📄")
    context = "\n".join(sum(search_res.values(), []))
    response, steps, chat_history, elapse = await get_model_response(text, context, custom_prompt, model)

    print_res = f"**推理耗时:{elapse:.5f}s**"
    tips(print_res, 15, icon="📄")
    # tool_name = steps[0].info['tool_name']
    # tool_args = steps[0].info['tool_args']
    # st.write(chat_history[1])
    # st.write(chat_history[1].function_call)
    try:
        thoughts = chat_history[1].function_call['thoughts']
    except:
        thoughts = '无需调用工具'
    # bot_print(f'**Agent思考** ：\n {thoughts}', avatar="📄")
    # bot_print(f'**Agent推理** ：\n {steps}', avatar="📄")
    tips(f'**Agent思考** ：\n {thoughts}',icon="📄")
    tips(f'**Agent推理** ：\n {steps}', icon="📄")

    bot_print(response)


async def main():
    db_path = config.get("vector_db_path")
    db_tools = DBUtils(db_path)
    embedding_extract = init_encoder(st.session_state["params"]["encoder"],
                                     st.session_state["params"]['api_type'], st.session_state["params"]['access_token'])
    llm = st.session_state["params"]["model_name"]
    llm = ERNIEAgent(st.session_state["params"]['api_type'], st.session_state["params"]['access_token'], llm)

    with st.sidebar.expander("🛠️ Tools 选择"):
        tools = st.selectbox(
            "Tools 选择",
            options=config.get("Tools"),
            help="让大语言模型有更多的能力",
        )
        # st.session_state["params"]["tools"] = tools + '_tools'
        if tools == 'Translation':
            st.session_state["params"]["tools"] = Translation()

    # with st.expander("💡Prompt", expanded=False):
    #     text_area = st.empty()
    #     input_prompt = text_area.text_area(
    #         label="Input",
    #         max_chars=500,
    #         height=200,
    #         label_visibility="hidden",
    #         value=config.get("DEFAULT_PROMPT"),
    #         key="input_prompt",
    #     )
    
    input_prompt = config.get("DEFAULT_PROMPT")

    with st.sidebar.expander("📄 示例提问"):
        question = st.selectbox(
            "问题示例",
            options=config.get("question"),
            help="您可以尝试提问以下问题"
        )
    if question =='请选择':
        input_txt = st.chat_input("问点啥吧！")
        if input_txt:
            with st.chat_message("user", avatar="😀"):
                st.markdown(input_txt)

            if not input_prompt:
                input_prompt = config.get("DEFAULT_PROMPT")

            query_embedding = embedding_extract(input_txt)
            search_top = st.session_state["params"]["search_top"]
            with st.spinner("正在搜索相关文档..."):
                uid = st.session_state.get("connect_id", None)
                search_res, search_elapse = db_tools.search_local(
                    query_embedding, top_k=search_top, uid=uid
                )

            if search_res is None:
                # bot_print("从知识库中抽取结果为空，直接采用LLM的本身能力回答。", avatar="📄")
                tips("从知识库中抽取结果为空，直接采用LLM的本身能力回答。", icon="📄")
                await predict_only_model(input_txt, llm)
            else:
                # logger.info(f"使用 {type(llm).__name__}")

                res_cxt = f"**Top{search_top}\n(得分从高到低，耗时:{search_elapse:.5f}s):** \n"
                tips(res_cxt, 5, icon="📄")

                await predict(
                    input_txt,
                    search_res,
                    llm,
                    input_prompt,
                )
    else :
        input_txt =question
        with st.chat_message("user", avatar="😀"):
            st.markdown(input_txt)

        query_embedding = embedding_extract(input_txt)
        search_top = st.session_state["params"]["search_top"]
        with st.spinner("正在搜索相关文档..."):
            uid = st.session_state.get("connect_id", None)
            search_res, search_elapse = db_tools.search_local(
                query_embedding, top_k=search_top, uid=uid
            )

        if search_res is None:
            # bot_print("从知识库中抽取结果为空，直接采用LLM的本身能力回答。", avatar="📄")
            tips("从知识库中抽取结果为空，直接采用LLM的本身能力回答。", icon="📄")
            await predict_only_model(input_txt, llm)
        else:
            #logger.info(f"使用 {type(llm).__name__}")

            res_cxt = f"**Top{search_top}\n(得分从高到低，耗时:{search_elapse:.5f}s):** \n"
            tips(res_cxt, 5, icon="📄")

            await predict(
                input_txt,
                search_res,
                llm,
                input_prompt,
            )
    st.sidebar.image(img, width=width)

if __name__ == "__main__":
    title = config.get("title")
    st.markdown(
        f"#### {title} \n ---- ",
    )
    init_ui_parameters()
    asyncio.run(main())
