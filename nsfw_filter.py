import os
from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests
import json 


def nsfw():
    url = 'http://jscn.sz-hgy.com/image.jpg'
    # 从url 下载图片保存到image_file
    try:
        response = requests.get(url)
    except:
        return False
    with open('image.jpg', 'wb') as f:
        f.write(response.content)
    image_file = 'image.jpg'
    encoder = MultipartEncoder(
        {'image': (os.path.basename(image_file), open(image_file, 'rb'))})
    headers = {'Content-Type': encoder.content_type}
    response = requests.post('http://127.0.0.1:8080/nsfw', headers=headers, data=encoder)
    classe= response.json()
    print(classe)
    # 只有netural 和drawing 两个类别是安全的
    return classe[0].get('className')== "Neutral" or classe[0].get('className')== "Drawing"


def main():
    print(nsfw())

if __name__ == '__main__':
    main()
