# QQ 机器人代码

在官方机器人的基础上集成langchain。

## 功能

- [x] 长期记忆
- [x] 画图
- [x] 天气查询
- [ ] 文件上传
- [ ] 语音识别
- [ ] 语音合成


# 使用方法

1. 安装依赖

运行 ：
    
    ```shell
    pip install -r requirements.txt
    cd botpy 
    pip install -e .
    ```


2. 安装附加鉴黄依赖(可选)

运行 ：
    
    ```shell
    cd  nsfwjs
    npm install
    npm run build
    npm install -g pm2
    pm2 start pm2.json
    ```
3. 设置环境变量

新建一个.env 文件
    
        ```shell
        cp .env.example .env
    
        ```
修改对应设置



4. 安装ollama 
```
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen:0.5b
```