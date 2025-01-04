import requests
import re
from urllib.parse import urlparse
from pathlib import Path

def extract_video_info(content):
        pattern = re.compile(r'<h1[^>]*data-title="([^"]*)"')
        match = re.search(pattern, content)
        html_snippet = match.group(0)
        start_index = html_snippet.find('data-title="') + len('data-title="')
        end_index = html_snippet.find('"', start_index)
        return html_snippet[start_index:end_index]
def get_BV(url):
    pattern = r"/video/(BV\w+)[/?#]"
    match = re.search(pattern, url)
    if match:
        return match.group(1)  # 返回捕获组中的BV号
    else:
        return None  # 如果没有找到匹配，则返回None
def html_get(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',  # 根据你的语言偏好调整
        'Accept-Encoding': 'gzip, deflate, br',  # 服务器可能使用压缩传输
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',  # 表明客户端愿意接受重定向到HTTPS
        'Cache-Control': 'max-age=0',  # 控制缓存策略
        'DNT': '1',  # Do Not Track: 请求不要跟踪用户行为
        'Referer': 'https://www.bilibili.com/',  # 指定来源页面，模拟从主页导航而来
    }
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    return response.text
def write(url,contest):
    # 定义文件路径
    file_path = Path('收藏.md')


    # 判断文件是否存在，不存在则创建
    if not file_path.exists():
        with open(file_path, 'w', encoding='utf-8') as f:
            pass  # 创建一个空文件

    # 打开文件并写入超链接
    with open(file_path, 'r+', encoding='utf-8') as f:
        content = f.read()

        # 如果文件已经有内容，则添加换行符
        if content:
            f.write('\n')

        # 写入超链接格式 [title](url)
        hyperlink = f'[{contest}]({url})'
        f.write(hyperlink)
def main():
    # 示例：假设这是用户输入的B站视频链接
    bili_url = input("请输入B站视频链接：").strip()

    # 确保链接是有效的B站链接
    parsed_url = urlparse(bili_url)
    if 'bilibili.com' not in parsed_url.netloc:
        print("这不是一个有效的B站链接，请检查后重试。")
    html_content = html_get(bili_url)
    title_content = extract_video_info(html_content)
    print(title_content)
    write(bili_url,title_content)
    bv = get_BV(bili_url)



if __name__ == '__main__':
    main()