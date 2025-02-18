# 工具调用
from operator import itemgetter
from langchain_core.tools import tool
import json
from langchain_core.runnables import chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from langchain.tools.render import render_text_description
from typing import Union
from langchain_community.document_loaders import WebBaseLoader



# 天气预报
# https://wttr.in/Shanghai?format=j1
@tool
def get_weather(city )->dict:
    """  the  input type is String  city english name, return weather info, if city is not provided, set the default city name  to  'Shanghai' use english name. """
    #if the city is not provided, set the default city name to 'Shanghai'
   
    url = f"https://wttr.in/{city}?format=j1"
    loader = WebBaseLoader(url)
    doc= loader.load()
    weatherjson= json.loads(doc[0].page_content)
    if weatherjson.get("output") is None:
        return weatherjson.get("current_condition")[0]
    else :
        return  weatherjson.get("output").get("current_condition")[0]

rendered_tools = render_text_description([get_weather])

system_prompt = f"""
    You are an assistant that has access to the following set of tools. Here are the names and descriptions for each tool:

{rendered_tools}

Given the user input, return the name and input of the tool to use. Return your response as a JSON blob with 'name' and 'arguments' keys."""

weather_prompt = ChatPromptTemplate.from_messages(
    [("system", system_prompt), ("user", "{input}")]
)


show_prompt= ChatPromptTemplate.from_template("""
    你是一个天气助手，通过分析以下的json数据，用简洁中文告诉用户天气情况。温度请使用摄氏度，风速请使用公里每小时。

    以下为 json 数据：

    {input}




    以下为用户问题：
    {question}






""")



# 正则表达式获取json
@chain
def get_json(input: str) -> str:
    import re
    pattern = re.compile(r'\{[^`]*\}')
    match = pattern.search(input)
    citydic = {"city": "Shanghai"}  # 默认值
    if match:
        try:
            cityjsonstr = match.group(0)
            cityjson = json.loads(cityjsonstr)
            city = cityjson.get("arguments")
            
            # 处理不同的输入格式情况
            if isinstance(city, list) and len(city) > 0:
                city = city[0]  # 如果是列表，取第一个元素
            elif isinstance(city, dict):
                city = city.get("city", "Shanghai")  # 如果是字典，尝试获取city键
            elif isinstance(city, str):
                city = city  # 如果是字符串，直接使用
            else:
                city = "Shanghai"  # 其他情况使用默认值
                
            citydic["city"] = city
        except (json.JSONDecodeError, AttributeError, IndexError) as e:
            print(f"解析城市数据时出错: {str(e)}")
            # 发生错误时保持默认值
    return citydic



# duckduckgo search 代理
# http://yifus.win:3000/search?query=question
@chain
def search(question:str)->str:
    """  the  input type is String  question, return search result. """
    url = f"http://yifus.win:3000/search?query={question}"
    print(url)
    try:
        loader = WebBaseLoader(url)
        doc= loader.load()
        return doc[0].page_content
    except Exception as e:
        return ''
    
