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


dotenv.load_dotenv()


model= ChatOpenAI(
    model_name=os.getenv("model_name","gpt-3.5-turbo")
) 

# groq 的 llama3-70b-8192 模型
groqmodel=ChatOpenAI(
    model_name="llama3-70b-8192",
    openai_api_key=os.getenv("GROQ_API_KEY"),
    openai_api_base=os.getenv("GROQ_API_BASE")
)
# llama3 需要套本地模型作为翻译

# 英文翻译成中文
prompt_en_to_cn = PromptTemplate.from_template("""
    你是一个中英文翻译专家，将用户输入的英文翻译成中文。对于非中文内容，它将提供中文翻译结果。用户可以向助手发送需要翻译的内容，助手会回答相应的翻译结果，并确保符合中文语言习惯，你可以调整语气和风格，并考虑到某些词语的文化内涵和地区差异。同时作为翻译家，需将原文翻译成具有信达雅标准的译文。"信" 即忠实于原文的内容与意图；"达" 意味着译文应通顺易懂，表达清晰；"雅" 则追求译文的文化审美和语言的优美。目标是创作出既忠于原作精神，又符合目标语言文化和读者审美的翻译。
            以下是用户的描述，如果内容包含英文， 请重新用中文描述这段内容。如果全部为中文，请直接输出原文内容。
    
            {text}
    """)
en_to_cn = {"text": RunnablePassthrough()} | prompt_en_to_cn | groqmodel | StrOutputParser()








localmodel= ChatOpenAI(model_name="qwen:0.5b-chat",
    openai_api_key="no",
    openai_api_base="http://127.0.0.1:11434/v1"
)


# 主要的llm
# llm =model.with_fallbacks([localmodel])|StrOutputParser()
llm = groqmodel|StrOutputParser()


# 次要的llm 做些简单工作节省资源
low_llm= ChatOpenAI(
    model_name=os.getenv("low_model_name","gpt-3.5-turbo")
) 


lowllm= low_llm.with_fallbacks([localmodel])|StrOutputParser()

# 普通聊天

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """这是属于你的长期记忆，请从长期记忆中提取信息，然后回答问题。


                {memory}
             """
        ),
        
        MessagesPlaceholder(variable_name="messages"),
    ]
)

@chain
def  build_message(input):
    member_openid = input.get("member_openid")
    question = input.get("question")
    db = dbManager(member_openid)
    historys= db.query()
    # 历史数据需要倒序
    historys.reverse()
    memorys =db.query_long()
    memory = ""
    for i  in memorys:
        memory += i[0] + "\n"

   
    db.close()
    messages=[]
    for history in historys:
        content = history[2]
        role = history[3]
        if role == 'user':
            messages.append(HumanMessage(content))
        else:
            messages.append(AIMessage(content))
    return {"messages": messages,"memory":memory}


# chatchain= build_message|prompt|llm 
chatchain= build_message|prompt|llm |en_to_cn




# 画图，生成图片

draw_prompt = PromptTemplate.from_template("""
    你是一个绘画助手，通过用户的描述，用简洁英语帮其丰富润色优化描述。

        以下是用户的画图描述，请用简洁英文描述这幅画的内容，让描述更加生动，字数不超过100字。

        {text}
""")



drawchain={"text": RunnablePassthrough()}| draw_prompt|lowllm|StrOutputParser()




# 保存记忆


@chain
def save_memory(input):
    member_openid = input.get("member_openid")
    text = input.get("question")
    db = dbManager(member_openid)
    memorys = db.query_long()
    memory = ""
    for i  in memorys:
        memory += i[0] + "\n"
    
    text =  text + "\n" + memory
    print(text)
    db.add_long(text)   
    db.close()
    return  "我已记住您说的话了！"


memary_chain = save_memory



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
    你是一个天气助手，通过分析以下的json数据，用简洁中文告诉用户天气情况。

    以下为 json 数据：

    {input}




    以下为用户问题：
    {question}






""")



# 正则表达式获取json
@chain
def  get_json( input:str)->str:
    import re
    pattern = re.compile(r'\{[^`]*\}')
    match = pattern.search(input)
    citydic= { "city":"Shanghai" }
    if match:

        cityjsonstr= match.group(0)
        cityjson = json.loads(cityjsonstr)
        city = cityjson.get("arguments")
        # 如果不是字符串 ，获取第一个元素
        if not isinstance(city,str):
            city = city[0]
        citydic["city"] = city
    return citydic


weather_data = {"input": RunnablePassthrough()} | weather_prompt | llm | get_json  |get_weather 

weather_chain = {"input": weather_data, "question": RunnablePassthrough() }|show_prompt|lowllm|StrOutputParser()





def  main():
    out= weather_chain.invoke  ("今天苏州天气如何？下雨了吗？")
    print(out)

if __name__ == "__main__":
    main()
