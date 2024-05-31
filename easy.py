# *_* encoding: utf-8 *_*

# 调用coze实现对话，搜索，画图等各种功能，免除各种意图识别。
# 20240520
import os,re, dotenv,botpy
from botpy.message import Message,DirectMessage,GroupMessage
from botpy.manage import GroupManageEvent
dotenv.load_dotenv()
from  messagehandler import  chatchain,drawchain,memary_chain,weather_chain,intent
from urllib.parse import quote
import  requests,json
from  db_helper import dbManager
import time 
from langchain_core.runnables import chain
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage,AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from chrome import build_image_from_markdown
import requests
llm= ChatOpenAI(model_name='coze.cn')


prompt = ChatPromptTemplate.from_messages(    [    MessagesPlaceholder(variable_name="messages"),    ])
@chain
def  build_message(input):
    member_openid = input.get("member_openid")
    question = input.get("question")
    db = dbManager(member_openid)
    historys= db.query()
    historys.reverse()
    db.close()
    messages=[]
    for history in historys:
        content = history[2]
        role = history[3]
        if role == 'user':
            messages.append(HumanMessage(content))
        else:
            messages.append(AIMessage(content))
    return {"messages": messages}

chatchain = build_message|prompt|llm| StrOutputParser()

def fixquestion(question):
    question=question.strip()
    pattern = r"<@!(\d+)>\s*(.*)"
    match = re.search(pattern, question)
    if match:
        user_id = match.group(1)
        question = match.group(2)
    return question

def message_handler(question:str,member_openid)->str:
        
        content = ""
        if question == "/weather":
            content = "今天天气晴朗，温度适中"
        if question =="/joke":
            content = "笑话：有一天，小明去买菜，结果买了一个西红柿，回家后，他把西红柿放在桌子上，然后西红柿就滚下来了，小明说：西红柿，你别滚，我买单！"
        if not content:
            for i  in  chatchain.stream({"question":question,"member_openid":member_openid}):
                print(i, end="", flush=True)
                content+=i
           
        # content = re.sub(r"https?://", "", content)
        # content = content.replace(".", "。")       
        return  content 

class MyClient(botpy.Client): 
    async def on_group_at_message_create(self, message: GroupMessage):
        member_openid= message.author.member_openid
        question = fixquestion(message.content)
        db= dbManager(member_openid)
        addtime = int(time.time())
        db.add(addtime,question,'user')
        content= message_handler(question,member_openid)
        db.add(addtime,content,'ai')
        pattern = r"\[\w+\]\((.*?)\)"
        match = re.search(pattern, content)

        # 如果找到了匹配项，则提取URL
        if match:
            url = match.group(1)
            print("匹配到下载图片网址:"+ url )
            res=requests.post("http://yifus.win/proxy.php",data={"url":url})
            imageurl="http://yifus.win/"+res.text
            print(imageurl)
            content=""" ![image]({})""".format(imageurl)
            
          
        sp="client/"+ str(member_openid)+".png"
        build_image_from_markdown(content,sp)
        uploadMedia = await message._api.post_group_file(
                group_openid=message.group_openid, 
                file_type=1, # 文件类型要对应上，具体支持的类型见方法说明
                url= "http://fastgpt.xinpanmen.com:8100/"+sp
            )
        await message._api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=7,  # 7表示富媒体类型
                    msg_id=message.id, 
                    media=uploadMedia
                )



def start_qqbot():
    intents = botpy.Intents(direct_message=True,public_guild_messages=True,public_messages=True) 
    client = MyClient(intents=intents)
    client.run(appid=os.getenv("QQ_APP_ID")  ,secret=os.getenv("QQ_APP_SECRET"))



def main():
    start_qqbot()

    

if __name__ == "__main__":
    main()

    