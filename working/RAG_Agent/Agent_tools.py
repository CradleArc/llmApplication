import os
from utils import read_yaml
config = read_yaml("/home/aistudio/config.yaml")
import asyncio
import requests
from pydantic import Field
from typing import Dict, Type
from erniebot_agent.tools.base import Tool
from erniebot_agent.tools.schema import ToolParameterView

tools_token = config.get('Tools_Access_Token')

def translation(text):
    url = 'http://tool-translation.aistudio-hub.baidu.com/translation'

    q = text  # example: hello
    from_lang = 'zh'  # example: en
    to_lang = 'en'  # example: zh
    term_ids = ''  # 术语库id，多个逗号隔开
    headers = {'Content-Type': 'application/json', 'Authorization': f'token {tools_token}'}
    payload = {'q': q, 'from': from_lang, 'to': to_lang, 'termIds': term_ids}
    r = requests.post(url, json=payload, headers=headers)
    result = r.json()
    result = result['result']['trans_result'][0]['dst']
    return str(result)


# 第一个类是描述这个工具输入的参数
class TranslationInputView(ToolParameterView):
    text: str = Field(description="需要翻译的文本")


# 第二个类就是描述response这个变量，这是这个工具输出的参数。
class TranslationOutputView(ToolParameterView):
    response: str = Field(description="已经翻译好的文本")


class Translation(Tool):
    description: str = "Texttospeech，是一个文本翻译工具。"
    input_type: Type[ToolParameterView] = TranslationInputView
    output_type: Type[ToolParameterView] = TranslationOutputView

    async def __call__(self, text: str) -> Dict[str, str]:
        response = await asyncio.to_thread(translation, text)
        return {"response": response}

