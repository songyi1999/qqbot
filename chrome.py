import mistune
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import urllib.parse

# 将 Markdown 文本转换为 HTML
def build_image_from_markdown(markdown, screenshot_path):
    html = mistune.markdown(markdown)
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.binary_location = '/usr/bin/chromium-browser'  # 指定 Chromium 的路径
    # driver_path = '/usr/bin/chromedriver'  
    driver = webdriver.Chrome( options=options)
    driver.set_window_size(360,100 ) # 适合手机查看
   
    template= f"""
    <!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>水晶粉风格网页</title>
    <style>
        body {{
            margin: 10px;
            padding: 0;
            width: 360px;
            min-height: 300px;
            background: linear-gradient(to bottom, #e6f7ff, #3399ff, #cceeff);
            font-family: Arial, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: #333;
        }}
        .container {{
             width: 100%;
            padding: 20px;
            box-sizing: border-box;
            background: rgba(255, 255, 255, 0.7);
            border-radius: 15px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);}}
        .header {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #ff69b4;
            text-align: left;}}
        .content {{
            font-size: 28px;
            line-height: 1.5;
            text-align: left;}}
    </style>
</head>
<body>
    <div class="container">
        <div class="header"></div>
        <div class="content">
            {html}
        </div>
    </div>
</body>
</html>
    """
    # print(template)
     # URL 编码 HTML 内容
    encoded_html = urllib.parse.quote(template)
    driver.get('data:text/html;charset=UTF-8,'+ encoded_html)
     # 获取页面高度并设置窗口高度
    total_height = driver.execute_script("return document.body.scrollHeight")+50

    #获取页面宽度并设置窗口宽度
    total_width = driver.execute_script("return document.body.scrollWidth")+100

    driver.set_window_size(total_width, total_height)

    driver.save_screenshot(screenshot_path)
    driver.quit()
    return screenshot_path

def main():
    markdown = """
    # 标题

    这是段落。
 * 项目 1
    * 项目 2 * 项目 1
    * 项目 2 * 项目 1
    * 项目 2
    * 项目 1
    * 项目 2
 * 项目 1
    * 项目 2 * 项目 1
    * 项目 2 * 项目 1
    * 项目 2 * 项目 1
    * 项目 2 * 项目 1
    * 项目 2
    ![](https://p19-flow-sign-sg.ciciai.com/ocean-cloud-tos-sg/3a01e01b83644db98d73e5039448072a.png~tplv-0es2k971ck-image.png?rk3s=18ea6f23&x-expires=1749369216&x-signature=498FpGWm1NEMO0DWovkUbK3f8%2FM%3D)
    """
    screenshot_path = build_image_from_markdown(markdown, 'screenshot.png')
    print('Screenshot saved to', screenshot_path)

if __name__ == '__main__':
    main()
