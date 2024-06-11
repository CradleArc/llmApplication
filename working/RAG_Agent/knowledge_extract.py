from utils import *
from typing import Dict, List, Union, Optional
from pathlib import Path
from tqdm import tqdm
import filetype
import numpy as np
import erniebot
import shutil
import time
import random
from vector_utils import DBUtils
import uuid
import os

def remove_ipynb_checkpoints_files(directory):
    for root, dirs, files in os.walk(directory):
        for dir_name in dirs:
            if dir_name == ".ipynb_checkpoints":
                dir_path = os.path.join(root, dir_name)
                shutil.rmtree(dir_path)
                print(f"Deleted: {dir_path}")


# Load configuration
config = read_yaml("/home/aistudio/config.yaml")
db_path = config.get("vector_db_path")
db_tools = DBUtils(db_path)

INPUT_TYPE = Union[str, Path]


# Encoder initialization
class ErnieEncodeText:
    def __init__(self, api_type: str, access_token: str):
        self.api_type = api_type
        self.access_token = access_token
        erniebot.api_type = self.api_type
        erniebot.access_token = self.access_token

    def __call__(self, sentences: List[str]):
        if not isinstance(sentences, list):
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


def init_encoder(encoder_name: str, api_type: str, access_token: str):
    if "ErnieBot-Text-Embedding" in encoder_name:
        return ErnieEncodeText(api_type, access_token)


encoder_config = config.get("Encoder")
encoder_name = list(encoder_config.keys())[0]
# print(encoder_name)
embedding_extract = init_encoder(
    encoder_name,
    encoder_config.get(encoder_name).get('api_type'),
    encoder_config.get(encoder_name).get("access_token")
)


# File loader class
class FileLoader:
    def __init__(self) -> None:
        self.file_map = {
            "office": ["docx", "doc", "ppt", "pptx", "xlsx", "xlx"],
            "txt": ["txt", "md"],
            "pdf": ["pdf"],
        }
        self.office_loader = OfficeLoader()
        self.pdf_loader = PDFLoader()
        self.txt_loader = TXTLoader()

    def __call__(self, file_path: INPUT_TYPE) -> Dict[str, List[str]]:
        all_content = {}
        file_list = self.get_file_list(file_path)

        for file in file_list:
            file_name = file.name
            if file.suffix[1:] in self.file_map["txt"]:
                content = self.txt_loader(file)
            else:
                file_type = self.which_type(file)
                if file_type in self.file_map["office"]:
                    content = self.office_loader(file)
                elif file_type in self.file_map["pdf"]:
                    content = self.pdf_loader(file)
                else:
                    # logger.warning("%s does not support.", file)
                    print("%s does not support.", file)
                    continue
            all_content[file_name] = content

        return all_content

    def get_file_list(self, file_path: INPUT_TYPE):
        if not isinstance(file_path, Path):
            file_path = Path(file_path)

        if file_path.is_dir():
            return list(file_path.rglob("*.*"))
        return [file_path]

    @staticmethod
    def which_type(content: Union[bytes, str, Path]) -> str:
        kind = filetype.guess(content)
        if kind is None:
            raise TypeError(f"The type of {content} does not support.")
        return kind.extension

def view_db_contents(uid):
    contents = db_tools.get_files(uid=uid)
    if contents:
        for item in contents:
            print(item)
    else:
        print("数据库中没有数据。")


def main():
    # action = input("请输入 'view' 查看数据库中的数据，'clear' 清空数据库 或 'extract' 提取向量: ").strip().lower()

    # if action == 'view':
    #     uid = input("请输入你需要查询的数据UID：")
    #     view_db_contents(uid)
    # elif action == 'clear':
    #     db_tools.clear_db()
    #     print("知识库已经被清空！")
    # elif action == 'extract':
    file_loader = FileLoader()
    upload_dir = config.get("upload_dir")
    remove_ipynb_checkpoints_files(upload_dir)
    all_doc_contents = file_loader(upload_dir)
    uid = str(uuid.uuid1())
    batch_size = config.get("encoder_batch_size", 16)

    for file_path, one_doc_contents in all_doc_contents.items():
        content_nums = len(one_doc_contents)
        all_embeddings = []

        for i in range(0, content_nums, batch_size):
            cur_contents = one_doc_contents[i:i + batch_size]
            if not cur_contents:
                continue
            print(cur_contents)
            embeddings = embedding_extract(cur_contents)
            if embeddings is None or embeddings.size == 0:
                continue

            all_embeddings.append(embeddings)

        if all_embeddings:
            all_embeddings = np.vstack(all_embeddings)
            db_tools.insert(file_path, all_embeddings, one_doc_contents, uid)
            print(f'uid:{uid},请记住您的uid，查询数据的时候需要用上。')
        else:
            print(f"从{file_path}提取向量为空。")
    # else:
    # print("无效的输入。请重新运行程序并输入 'view', 'clear' 或 'extract'。")


if __name__ == "__main__":
    main()
