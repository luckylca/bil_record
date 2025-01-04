import requests
import re
from urllib.parse import urlparse
from pathlib import Path
import os

def extract_video_info(content):
        pattern = re.compile(r'<h1[^>]*data-title="([^"]*)"')
        match = re.search(pattern, content)
        html_snippet = match.group(0)
        start_index = html_snippet.find('data-title="') + len('data-title="')
        end_index = html_snippet.find('"', start_index)
        return html_snippet[start_index:end_index]
def get_BV(url):
    pattern = r"(?:https?:\/\/)?(?:www\.)?bilibili\.com\/video\/(BV\w+)(?:\/|\?|$)"
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
def replace_bv_link(bv_number, new_url, file_path='收藏.md'):
    try:
        # 正则表达式模式，用于匹配包含特定BV号的Markdown格式的超链接
        pattern = re.compile(r'$.*?$$(https?://www\.bilibili\.com/video/{}[^)]*)$'.format(re.escape(bv_number)))

        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # 查找所有匹配项
        matches = pattern.findall(content)

        if not matches:
            print("添加成功。")
            return False

        # 假设我们只替换第一个找到的链接（如果有多个相同的BV号，可以根据需求调整逻辑）
        old_link = matches[0]
        # 构造新的Markdown格式链接字符串
        new_link = re.sub(r'https?://www\.bilibili\.com/video/{}[^)]*'.format(re.escape(bv_number)), new_url, old_link)

        # 替换旧链接为新链接
        updated_content = content.replace(old_link, new_link)
        print("更新成功")
        # 写入更新后的内容回文件
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        return True
    except FileNotFoundError:
        print(f"错误：无法打开文件 {file_path}。")
        return False
    except Exception as e:
        print(f"发生了一个错误: {e}")
        return False
def update_or_add_bv_link(bv_number, title_content, bili_url, file_path='收藏.md'):
    link_template = f"[{title_content}]({bili_url})"
    # 确保文件存在
    is_new_file = not os.path.exists(file_path)
    if is_new_file:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write("# bilibili收藏列表\n")  # 添加一级标题

    # 正则表达式模式，用于匹配 Markdown 格式的超链接，确保 URL 包含 BV 号
    pattern = re.compile(rf'\[.*?\]\(https?://(?:www\.)?bilibili\.com/video/{re.escape(bv_number)}[^\)]*\)', re.IGNORECASE)

    try:
        with open(file_path, 'r+', encoding='utf-8') as file:
            content = file.read()
            is_empty = not content.strip()

            if is_empty:
                # 文件为空，直接写入新链接
                file.write(link_template)
                return "文件为空，已添加新链接。"

            # 查找匹配的旧链接
            match = pattern.search(content)

            if match:
                old_link = match.group(0)
                print(f"Found link to replace: {old_link}")
                # 替换旧链接为新链接
                updated_content = content.replace(old_link, link_template)
                # 写入更新后的内容回文件
                file.seek(0)
                file.write(updated_content)
                file.truncate()  # 确保文件大小与写入内容匹配
                return f"成功将 BV 号为 {bv_number} 的链接更新为新链接。"
            else:
                # 如果没有匹配项，追加新链接
                file.write('\n' + link_template)
                return f"未找到 BV 号为 {bv_number} 的链接，已添加新链接。"

    except Exception as e:
        print(f"发生了一个错误: {e}")
        return "操作失败，请检查错误信息。"
def main():
    # 示例：假设这是用户输入的B站视频链接
    bili_url = input("请输入B站视频链接：").strip()
    parsed_url = urlparse(bili_url)
    if 'bilibili.com' not in parsed_url.netloc:
        print("这不是一个有效的B站链接，请检查后重试。")
    html_content = html_get(bili_url)
    title_content = extract_video_info(html_content)
    print(title_content)
    bv = get_BV(bili_url)
    result = update_or_add_bv_link(bv,title_content,bili_url)
    print(result)
def run():
    while True:
        main()
        # 用户选择是否重新执行程序
        choice = input("输入1继续添加链接，输入0退出程序: ").strip()
        if choice == '0':
            print("退出程序。")
            break
        elif choice != '1':
            print("无效输入，请输入0或1.")
            # 继续当前循环，让用户重新选择
            continue
        # 如果用户输入的是'1'，则循环会继续，因此不需要额外的语句


if __name__ == '__main__':
    run()