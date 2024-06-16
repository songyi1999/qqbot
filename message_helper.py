# *_* encoding: utf-8 *_*
# 消息处理器
import os,re, dotenv
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.runnables import chain
import  base64
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage,AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from  db_helper  import  dbManager
import  time 
from operator import itemgetter
from langchain_core.tools import tool
import json
from langchain.tools.render import render_text_description
from typing import Union
from toolsuse import * 
from faiss_helper import *
from langchain_community.llms import Ollama 
from langchain_community.llms import QianfanLLMEndpoint #百度千帆
dotenv.load_dotenv()


llm= Ollama(
    base_url=os.getenv("OLLAMA_BASE_URL","http://localhost:11434"),
    model=os.getenv("OLLAMA_MODEL","llama3"),
    # model="llama3"
)

qianfanllm= QianfanLLMEndpoint(model_name="ERNIE-Speed-8K")

model= llm.with_fallbacks([qianfanllm])


def main():
    out=llm.invoke("你好，自我介绍下，你是谁")
    print(out)


if __name__ == '__main__':
    main()