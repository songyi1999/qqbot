# *_* encoding: utf-8 *_*
import os,re, dotenv,botpy
from botpy.message import Message,DirectMessage,GroupMessage
from botpy.manage import GroupManageEvent
dotenv.load_dotenv()
from  messagehandler import  chatchain,drawchain,memary_chain,weather_chain,intent
from urllib.parse import quote
import  requests,json
from  db_helper import dbManager
import time 
from  nsfw_filter import   nsfw
from upload import  showcode,start_upload
# 消息处理

# 去掉消息发送人的@，只保留问题内容
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
           
        # 替换答案中的所有网址，防止QQ出错。
        content = re.sub(r"https?://", "", content)
        # 所有出现的英文句号替换成中文句号
        content = content.replace(".", "。")       
        return  content        


class MyClient(botpy.Client):
    # 群消息
    async def on_group_at_message_create(self, message: GroupMessage):
        user= message.author
        member_openid= user.member_openid
        print(member_openid)
        question = fixquestion(message.content)
        db= dbManager(member_openid)
        addtime = int(time.time())
        db.add(addtime,question,'user')
        intent_result= intent.invoke(question)
        if "file" in intent_result:
            image_url=showcode(member_openid) 
            uploadMedia = await message._api.post_group_file(
                    group_openid=message.group_openid, 
                    file_type=1, # 文件类型要对应上，具体支持的类型见方法说明
                    url= image_url
                )
            await message._api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=7,  # 7表示富媒体类型
                    msg_id=message.id, 
                    media=uploadMedia
                )
            return 

        if "draw" in intent_result:
          # 回复图片        
            # 上传文件
            
            imagestr= drawchain.invoke(question)
            imagestr=imagestr.replace('"','').replace("'","").replace("?","")
            image_url= quote(imagestr)
            image_url = image_url.replace(".", "")
            file_url = "https://image.pollinations.ai/prompt/" + image_url 
            file_url= "https://jscn.sz-hgy.com/proxy.php?url="+file_url
            # 上传资源
            requests.get(file_url)
            if nsfw():
                uploadMedia = await message._api.post_group_file(
                    group_openid=message.group_openid, 
                    file_type=1, # 文件类型要对应上，具体支持的类型见方法说明
                    # url="http://yifus.win/image.jpg" # 文件Url
                    url= "https://jscn.sz-hgy.com/image.jpg"
                )
                # 资源上传后，会得到Media，用于发送消息
                addtime = int(time.time())
                content= "这是您要的画，"+ question
                db.add(addtime,content,'ai')
                db.close()
                await message._api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=7,  # 7表示富媒体类型
                    msg_id=message.id, 
                    media=uploadMedia
                )
               
                return 
            else:
                content= "抱歉，这个画不太合适，我不想画"
                await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=0, 
                msg_id=message.id,
                content=content)
                return 
        if "remember" in intent_result:
            content= memary_chain.invoke({"question":question,"member_openid":member_openid})
            await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=0, 
                msg_id=message.id,
                content=content)
            addtime = int(time.time())
            db.add(addtime,content,'ai')
            db.close()
            return 

        if "weather" in intent_result :

            content = weather_chain.invoke(question)

            await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=0, 
                msg_id=message.id,
                content=content)
        else:

            content= message_handler(question,member_openid)
            # 回复消息
            await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=0, 
                msg_id=message.id,
                content=content)
            addtime = int(time.time())
            db.add(addtime,content,'ai')
            db.close()


    # 私信
    async def on_direct_message_create(self, message: DirectMessage):
        member_openid=message.author.id
        content= message_handler(message.content,member_openid)
        await self.api.post_dms(
            guild_id=message.guild_id,
            content=content,
            msg_id=message.id,
        )


    # 频道聊天
    async def on_at_message_create(self, message: Message):
        member_openid= message.author.id
        content= message_handler(message.content,member_openid)
        await self.api.post_message(channel_id=message.channel_id, content=content)



def start_qqbot():
    intents = botpy.Intents(direct_message=True,public_guild_messages=True,public_messages=True) 
    client = MyClient(intents=intents)
    client.run(appid=os.getenv("QQ_APP_ID")  ,secret=os.getenv("QQ_APP_SECRET"))

from multiprocessing import Process

def main():
    try:
        # 创建进程
        qqbot_process = Process(target=start_qqbot)
        upload_process = Process(target=start_upload)
        
        # 启动进程
        qqbot_process.start()
        upload_process.start()
        
        # 等待进程完成
        qqbot_process.join()
        upload_process.join()

        print("所有任务完成")

    except Exception as e:
        print(f"发生错误：{e}")
        
    finally:
        try:
            # 清理进程，避免资源泄露
            qqbot_process.terminate()
            upload_process.terminate()
        except Exception as e:
            print(f"清理进程时出现错误：{e}")

if __name__ == "__main__":
    main()

    