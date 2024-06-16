import os,re, dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
dotenv.load_dotenv()
# xunzi = ChatOpenAI( # 荀子模型
#     openai_api_base="http://xunziallm.njau.edu.cn:21180/v1",
#     openai_api_key="ANY THING",
#     model_name="/home/gpu0/Xunzi-Qwen1.5-7B_chat",
#     temperature=0
# )|StrOutputParser()
qianwen32b=ChatOpenAI(temperature=0)|StrOutputParser() # 千问32b模型
kimi=ChatOpenAI(temperature=0,model_name='kimi')|StrOutputParser() # Kimi模型
question="文言文中的“爱”字是什么意思？请举例说明"
# xunzi_result=xunzi.invoke(question)
# qwen_result= qianwen32b.invoke(question)
# kimi_result=kimi.invoke(question)
# print(f"问题：{question}")
# # print(f"荀子模型返回：\n {xunzi_result}")
# print(f"千问32b模型返回：\n {qwen_result}")
# print(f"Kimi模型返回：\n {kimi_result}")
coze=ChatOpenAI(temperature=0,model_name='coze.cn')|StrOutputParser() # Coze模型
coze_result=coze.invoke(question)
print(f"问题：{question}")
print(f"Coze模型返回：\n {coze_result}")


