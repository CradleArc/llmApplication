


# 大模型应用实践 ~~ 持续更新

## AI Studio

#### 搜索推荐系列

* PaddleRec -- 基于MovieLens数据集的电影推荐系统 https://aistudio.baidu.com/projectdetail/559336?channelType=0&channel=0

* 动手搭建一套端到端文本语义检索系统 https://aistudio.baidu.com/projectdetail/3351784?channelType=0&channel=0

#### 文生图系列 

* 【有手就会系列】四步教你生成二次元小姐姐 https://aistudio.baidu.com/projectdetail/4666819?channelType=0&channel=0

* 想定制自己的文图生成模型吗？想画什么画什么 https://aistudio.baidu.com/projectdetail/4905623?channelType=0&channel=0

#### LLM系列

* 基于 ERNIE Bot 和 LLM2Json 的问卷生成器 https://aistudio.baidu.com/projectdetail/7431608?channelType=0&channel=0

* 基于PP-OCR和ErnieBot的智能视频问答 https://aistudio.baidu.com/projectdetail/7892508?channelType=0&channel=0

#### 图像系列

* PaddleHub一键OCR中文识别（超轻量8.1M模型，火爆）https://aistudio.baidu.com/projectdetail/507159?channelType=0&channel=0

* ERNIE Bot魔改SD的webUI，生成专属字符图 https://aistudio.baidu.com/projectdetail/6951379?channelType=0&channel=0

* 一键AI抠图，证件照换背景，可部署成自己的应用 https://aistudio.baidu.com/projectdetail/7580793?channelType=0&channel=0




## 搭建向量数据库

### 词向量的优势

在RAG（Retrieval Augmented Generation，检索增强生成）方面词向量的优势主要有两点：

* 词向量比文字更适合检索。当我们在数据库检索时，如果数据库存储的是文字，主要通过检索关键词（词法搜索）等方法找到相对匹配的数据，匹配的程度是取决于关键词的数量或者是否完全匹配查询句的；但是词向量中包含了原文本的语义信息，可以通过计算问题与数据库中数据的点积、余弦距离、欧几里得距离等指标，直接获取问题与数据在语义层面上的相似度；

* 词向量比其它媒介的综合信息能力更强，当传统数据库存储文字、声音、图像、视频等多种媒介时，很难去将上述多种媒介构建起关联与跨模态的查询方法；但是词向量却可以通过多种向量模型将多种数据映射成统一的向量形式。











