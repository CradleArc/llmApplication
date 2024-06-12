
## 项目结构说明

- LangchainUsing：Langchain对文档的综合应用。
- Text： 传统的NLP任务，以 paddle 框架实现。
- Tasks：文本任务中常见的方案。
- Working：企业级的 Agent 应用。

## 一、Application
#### llmApplication/LangchainUsing：
* wordwvec
* Case-Faiss使用
* pdf-faiss-embedding
* rag-weaviate-llama3
* pdf-清洗

#### llmApplication/Text: 
* 情感分析-paddle
* 文本分类-paddle

#### llmApplication/Tasks:
* fastapi-llm
* ocr中文识别-paddle
* 命名实体识别-paddle
* 情感分析-paddle
* 抽取回答-paddle
* 知识图谱回答-paddle

#### llmApplication/Working: 
* KBQA-知识库问答
* RAG
* RAG-Agent
* 知识图谱-优质文章识别

## 二、Vector Database

### 词向量的优势

在RAG（Retrieval Augmented Generation，检索增强生成）方面词向量的优势主要有两点：

* 词向量比文字更适合检索。当我们在数据库检索时，如果数据库存储的是文字，主要通过检索关键词（词法搜索）等方法找到相对匹配的数据，匹配的程度是取决于关键词的数量或者是否完全匹配查询句的；但是词向量中包含了原文本的语义信息，可以通过计算问题与数据库中数据的点积、余弦距离、欧几里得距离等指标，直接获取问题与数据在语义层面上的相似度；

* 词向量比其它媒介的综合信息能力更强，当传统数据库存储文字、声音、图像、视频等多种媒介时，很难去将上述多种媒介构建起关联与跨模态的查询方法；但是词向量却可以通过多种向量模型将多种数据映射成统一的向量形式。











