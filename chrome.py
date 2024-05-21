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
        <html>
        <head>
            <title>Image Viewer</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0"> 
            <style>
           
                body {{
                    font-size:28px;
            margin: 10px;
            padding: 0;
            width: 360px;
        }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
        }}
        </style>
        </head>
        <body>
        {html}
        </body>
        </html>
    """
    # print(template)
     # URL 编码 HTML 内容
    encoded_html = urllib.parse.quote(template)
    driver.get('data:text/html;charset=UTF-8,'+ encoded_html)
     # 获取页面高度并设置窗口高度
    total_height = driver.execute_script("return document.body.scrollHeight")+100

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
    * 项目 2
https://p19-flow-sign-sg.ciciai.com/ocean-cloud-tos-sg/0c0d85ddcadf4e5e94d80ca1bcf02320.png~tplv-0es2k971ck-image.png?rk3s=18ea6f23&x-expires=1747747029&x-signature=7T%2BRGfV9KQkV8Gclrip1J5Q897I%3D
![Image](https://p19-flow-sign-sg.ciciai.com/ocean-cloud-tos-sg/0c0d85ddcadf4e5e94d80ca1bcf02320.png~tplv-0es2k971ck-image.png?rk3s=18ea6f23&x-expires=1747747029&x-signature=7T%2BRGfV9KQkV8Gclrip1J5Q897I%3D)

    """
    screenshot_path = build_image_from_markdown(markdown, 'screenshot.png')
    print('Screenshot saved to', screenshot_path)

if __name__ == '__main__':
    main()
