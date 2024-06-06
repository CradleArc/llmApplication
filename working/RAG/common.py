import pandas as pd 
import erniebot
from db import milvusClient
import time
import datetime
import logging
erniebot.api_type = "aistudio"

# ErnieBot Token配置
erniebot.access_token = "a19071560336532b319d631422b4f6546dc25bd0"
# 知识库文件，支持csv，txt，xlsx，xls
dbFile = "baoxianzhidao_filtertest.csv" 


logging.basicConfig(level=logging.INFO)
mc = milvusClient()
mc.createCollection()
mc.load()

def embedding(text):
    response = erniebot.Embedding.create(
        model="ernie-text-embedding",
        input=[text])

    return response.get_result()

# 自动加载知识库
if dbFile.endswith(".csv"):
    try:
        data_df = pd.read_csv(dbFile,encoding='gbk')
    except:
        data_df = pd.read_csv(dbFile, encoding="utf-8")
elif dbFile.endswith(".xlsx") or dbFile.endswith(".xls"):
    data_df = pd.read_excel(dbFile)
elif dbFile.endswith(".txt"):
    data_df = pd.read_table(dbFile, header=None)

reply = data_df.iloc[:, 0]
for rly in reply:
    try:
        rlyEmbedding = embedding(rly) #Embedding
    except Exception as e:
        logging.info("Embedding error:", e)
    try:
        mc.insert(rly, rlyEmbedding) #Insert
    except Exception as e:
        logging.info("Insert error:", e)
        time.sleep(0.5)

logging.info("【数据导入】成功导入文本向量")

def chat(model, text):
    response = erniebot.ChatCompletion.create(
        model=model, 
        messages=[{"role": "user", "content": text}],
    )
    return response.get_result()


def add_text(history, text):
    history = history + [[text, None]]
    return history, ""

def bot(history, llm):
    text = history[-1][0]
    logging.info("【用户输入】 {}".format(text))
    text_embedding = embedding(text)
    ragResult = mc.search(text_embedding)
    instruction = "使用以下文段来回答最后的问题。仅根据给定的文段生成答案。如果你在给定的文段中没有找到任何与问题相关的信息，就说你不知道，不要试图编造答案。保持你的答案富有表现力。"
    erniebotInput = instruction + "用户最后的问题是：" + text + "。给定的文段是：" + ragResult
    logging.info("【文心Prompt】 {}".format(erniebotInput))
    chatResult = chat(llm, erniebotInput)
    logging.info("【文心Answer】 {}".format(chatResult))
    history[-1][1] = chatResult
    return history


