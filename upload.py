import qrcode
import json
from fastapi import FastAPI,Body,UploadFile,Request,File
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocket
from fastapi.responses import JSONResponse,HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.responses import FileResponse
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
      


# 上传文件
@app.post("/uploadfile")
async def upload_file(file: UploadFile):
    
    # 保存 JPG 文件到本地
    with open("uploaded_file.jpg", "wb") as buffer:
        buffer.write(await file.read())



def start_upload():
    uvicorn.run(app, host="0.0.0.0", port=8100)

if __name__ == '__main__':
    start_upload()
