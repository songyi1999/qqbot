import qrcode
import json,dotenv
from fastapi import FastAPI,Body,UploadFile,Request,File,Query
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocket
from fastapi.responses import JSONResponse,HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader,Docx2txtLoader,PyPDFLoader,UnstructuredExcelLoader,CSVLoader
import os
dotenv.load_dotenv()

from fastapi.responses import FileResponse
from faiss_helper import FaissVectorManager,embeddings
def  showcode(member_openid):
 
  data=f"http://qqbot.sz-hgy.com:8100/client/index.html?member_openid={member_openid}"
  img=qrcode.make(data)
  img.save("client/qrcode.png")
  return "http://qqbot.sz-hgy.com:8100/client/qrcode.png"
  

app = FastAPI()

orgins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=orgins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 设置静态文件路径为client
app.mount("/client", StaticFiles(directory="client"), name="client")




# 下载图片文件
@app.get("/download_images")
async def download_images(file_path: str):
    return FileResponse(file_path, media_type="image/jpeg")
      


# 上传文件,接受参数为file 和member_openid
@app.post("/uploadfile")
async def upload_file(file: UploadFile,member_openid:str=Body(...) ):
    print("member_openid",member_openid)
    # 在files下创建member_openid文件夹
    if not os.path.exists(f"files/{member_openid}"):
        os.makedirs(f"files/{member_openid}")
    # 保存文件到files/member_openid
    with open(f"files/{member_openid}/{file.filename}", "wb") as buffer:
        buffer.write(await file.read())
    # 返回文件路径
    file_path= f"files/{member_openid}/{file.filename}"
    # 通过不同的文件类型载入不同的loader
    if file.filename.endswith('.docx'):
        loader=Docx2txtLoader(file_path)
    elif file.filename.endswith('.pdf'):
        loader=PyPDFLoader(file_path)
    elif file.filename.endswith('.xlsx'):
        loader=UnstructuredExcelLoader(file_path)
    elif file.filename.endswith('.csv'):
        loader=CSVLoader(file_path)
    else:
        loader=TextLoader(file_path)
    # 载入文档
    docs=loader.load()
    # 分割文档
    text_splitter= RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    # 创建FaissVectorManager
    db = FaissVectorManager(member_openid)
    # 添加文档
    db.add_documents(splits)
    return {"file_path":file_path}





def start_upload():
    uvicorn.run(app, host="0.0.0.0", port=8100)






if __name__ == '__main__':
    from messagehandler import  lowllm
    from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
    from langchain_cohere import CohereRerank
    # docx= './test.txt'
    # loader=TextLoader(docx)
    # docs=loader.load()
    # text_splitter= RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    # splits = text_splitter.split_documents(docs)
    db = FaissVectorManager('5199C654EC2E4CA459BF88666D1710E6')
   

   



    # db.add_documents(splits)
    question= "张三考多少分？"
    testresult = db.search(question)
    print(testresult)
    resulttext=testresult[0][0].page_content
    print(resulttext)
    prompt = f""" 请参考以下内容回答问题：
    内容如下：
    {resulttext}
    
    问题如下：
    {question}
    """
    for i in lowllm.stream(prompt):
        print(i,end="",flush=True)
    
   

