from datetime import datetime
from pathlib import Path
from string import Template
from typing import List, Union
import yaml
import re
from typing import List
from rapidocr_pdf import PDFExtracter
from extract_office_content import ExtractOfficeContent

# knowledge_qa_llm

config_path = "/home/aistudio/config.yaml"


def read_yaml(yaml_path: Union[str, Path]):
    with open(str(yaml_path), "rb") as f:
        data = yaml.load(f, Loader=yaml.Loader)
    return data

def make_prompt(query: str, context: str = None, custom_prompt: str = None) -> str:
    # 如果上下文为空，则直接返回查询语句
    if context is None:
        return query

    # 如果自定义提示中没有$query或$context，则抛出值错误异常
    if "$query" not in custom_prompt or "$context" not in custom_prompt:
        raise ValueError("prompt中必须含有$query和$context两个值")

    # 使用自定义提示作为模板，将查询语句和上下文替换到模板中
    msg_template = Template(custom_prompt)
    message = msg_template.substitute(query=query, context=context)
    return message

def mkdir(dir_path):
    Path(dir_path).mkdir(parents=True, exist_ok=True)


def get_timestamp():
    return datetime.strftime(datetime.now(), "%Y-%m-%d")


def read_txt(txt_path: Union[Path, str]) -> List[str]:
    if not isinstance(txt_path, str):
        txt_path = str(txt_path)

    with open(txt_path, "r", encoding="utf-8") as f:
        data = list(map(lambda x: x.rstrip("\n"), f))
    return data


config = read_yaml(config_path)


class ChineseTextSplitter:
    def __init__(
        self,
        pdf: bool = False,
        sentence_size: int = config.get("SENTENCE_SIZE"),
    ):
        self.pdf = pdf
        self.sentence_size = sentence_size

    def split_text1(self, text: str) -> List[str]:
        if self.pdf:
            text = re.sub(r"\n{3,}", "\n", text)
            text = re.sub("\s", " ", text)
            text = text.replace("\n\n", "")
        sent_sep_pattern = re.compile(
            '([﹔﹖﹗。！？]["’”」』]{0,2}|(?=["‘“「『]{1,2}|$))'
        )  # del ：；
        sent_list = []
        for ele in sent_sep_pattern.split(text):
            ele = ele.strip()
            if sent_sep_pattern.match(ele) and sent_list:
                sent_list[-1] += ele
            elif ele:
                sent_list.append(ele)
        return sent_list

    def split_text(self, text: str) -> List[str]: 
        if self.pdf:
            text = re.sub(r"\n{3,}", r"\n", text)
            text = re.sub("\s", " ", text)
            text = re.sub("\n\n", "", text)

        text = re.sub(r"([;；!?。！？\?])([^”’])", r"\1\n\2", text)  # 单字符断句符
        text = re.sub(r'(\.{6})([^"’”」』])', r"\1\n\2", text)  # 英文省略号
        text = re.sub(r'(\…{2})([^"’”」』])', r"\1\n\2", text)  # 中文省略号
        text = re.sub(r'([;；!?。！？\?]["’”」』]{0,2})([^;；!?，。！？\?])', r"\1\n\2", text)
        # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
        text = text.rstrip()  # 段尾如果有多余的\n就去掉它
        # 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
        ls = [i for i in text.split("\n") if i]
        for ele in ls:
            if len(ele) > self.sentence_size:
                ele1 = re.sub(r'([,，.]["’”」』]{0,2})([^,，.])', r"\1\n\2", ele)
                ele1_ls = ele1.split("\n")
                for ele_ele1 in ele1_ls:
                    if len(ele_ele1) > self.sentence_size:
                        ele_ele2 = re.sub(
                            r'([\n]{1,}| {2,}["’”」』]{0,2})([^\s])', r"\1\n\2", ele_ele1
                        )
                        ele2_ls = ele_ele2.split("\n")
                        for ele_ele2 in ele2_ls:
                            if len(ele_ele2) > self.sentence_size:
                                ele_ele3 = re.sub(
                                    '( ["’”」』]{0,2})([^ ])', r"\1\n\2", ele_ele2
                                )
                                ele2_id = ele2_ls.index(ele_ele2)
                                ele2_ls = (
                                    ele2_ls[:ele2_id]
                                    + [i for i in ele_ele3.split("\n") if i]
                                    + ele2_ls[ele2_id + 1 :]
                                )
                        ele_id = ele1_ls.index(ele_ele1)
                        ele1_ls = (
                            ele1_ls[:ele_id]
                            + [i for i in ele2_ls if i]
                            + ele1_ls[ele_id + 1 :]
                        )

                id = ls.index(ele)
                ls = ls[:id] + [i.strip() for i in ele1_ls if i] + ls[id + 1 :]
        return ls

class PDFLoader:
    def __init__(
        self,
    ):
        self.extracter = PDFExtracter()
        self.splitter = ChineseTextSplitter(pdf=True)

    def __call__(self, pdf_path: Union[str, Path]) -> List[str]:
        contents = self.extracter(pdf_path)
        split_contents = [self.splitter.split_text(v[1]) for v in contents]
        return sum(split_contents, [])

class OfficeLoader:
    def __init__(self) -> None:
        self.extracter = ExtractOfficeContent()
        self.splitter = ChineseTextSplitter()

    def __call__(self, office_path: Union[str, Path]) -> str:
        contents = self.extracter(office_path)
        split_contents = [self.splitter.split_text(v) for v in contents]
        return sum(split_contents, [])

class TXTLoader:
    def __init__(self) -> None:
        self.splitter = ChineseTextSplitter()

    def __call__(self, txt_path: Union[str, Path]) -> List[str]:
        contents = read_txt(txt_path)
        split_contents = [self.splitter.split_text(v) for v in contents]
        return sum(split_contents, [])
