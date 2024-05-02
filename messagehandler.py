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


localmodel= ChatOpenAI(model_name="qwen:0.5b-chat",
    openai_api_key="no",
    openai_api_base="http://127.0.0.1:11434/v1"
)





low_llm= ChatOpenAI(
    model_name=os.getenv("low_model_name","gpt-3.5-turbo")
) 


# llama3 需要套本地模型作为翻译

# 英文翻译成中文
prompt_en_to_cn = PromptTemplate.from_template("""
    你是一个中英文翻译专家，将用户输入的英文翻译成中文。对于非中文内容，它将提供中文翻译结果。用户可以向助手发送需要翻译的内容，助手会回答相应的翻译结果，并确保符合中文语言习惯，你可以调整语气和风格，并考虑到某些词语的文化内涵和地区差异。同时作为翻译家，需将原文翻译成具有信达雅标准的译文。"信" 即忠实于原文的内容与意图；"达" 意味着译文应通顺易懂，表达清晰；"雅" 则追求译文的文化审美和语言的优美。目标是创作出既忠于原作精神，又符合目标语言文化和读者审美的翻译。
            以下是用户的描述，如果内容包含英文， 请重新用中文描述这段内容。如果全部为中文，请不要修改直接原样输出原文内容。
    
            {text}
    """)
en_to_cn = {"text": RunnablePassthrough()} | prompt_en_to_cn | groqmodel | StrOutputParser()








# 主要的llm
# llm =model.with_fallbacks([localmodel])|StrOutputParser()
llm = groqmodel|StrOutputParser()

# 次要的llm 做些简单工作节省资源

lowllm= low_llm.with_fallbacks([localmodel])|StrOutputParser()


# 意图识别判断
intent_prompt = PromptTemplate.from_template("""
    你是一个意图识别助手，通过用户的描述，判断用户意图,并选择合适的类别标签输出。
        draw: 用户明确说明想要AI绘画创作,用户描述的内容是包含具体想画什么的描述。例如：“请给我画一只猫” 或“我想要一幅美丽的名山大川的图”。
        weather: 需要查询天气请况。例如：“今天苏州会下雨吗？” 或 “今天需要带伞吗？”,“今天的紫外线指数是多少？”
        remember: 用户想要保存一些信息。通常会包含“记住” 这个词或同类词。例如：“请记住我喜欢吃苹果” 或 “记住我喜欢看电影” 或 “记住，你的名字叫猫局”
        file:用户想要上传文件.
        other: 其他。任何不包含在以上类别的对话，都选择other类别。

        以下是用户的描述，严谨的请判断用户的意图，并只返回类别标签。不用输出其他内容。

        "{text}"
""")
@chain
def intent(input):
    return {"text": RunnablePassthrough()}|intent_prompt|groqmodel|StrOutputParser()








# 普通聊天







prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """这是属于你的长期记忆，请从长期记忆中提取信息，然后回答问题。

                ***********记忆开始***********
                {memory}
                ***********记忆结束***********

                这是针对用户的问题进行了网络搜索，请参考搜索结果回答问题。
                ***********搜索结果开始***********
                {search_data}
                ***********搜索结果结束***********

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
    searchresult= search.invoke(question)
    return {"messages": messages,"memory":memory,"search_data":searchresult}


# chatchain= build_message|prompt|llm 

chatchain = build_message|prompt|llm|en_to_cn




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

weather_data = {"input": RunnablePassthrough()} | weather_prompt | llm | get_json  |get_weather 

weather_chain = {"input": weather_data, "question": RunnablePassthrough() }|show_prompt|lowllm|StrOutputParser()





def  main():
    out= intent.invoke  ("江山如画，美不胜收，请对下联进行润色。")
    print(out)

if __name__ == "__main__":
    main()
