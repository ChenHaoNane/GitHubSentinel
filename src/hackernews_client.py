import requests
from bs4 import BeautifulSoup
import os  # 导入os模块用于文件和目录操作
from datetime import datetime  # 导入日期处理模块
from logger import LOG  # 导入日志模块


class HackernewsClient:
    def __init__(self, base_url='https://news.ycombinator.com/news'):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; HaonanBot/1.0; +https://news.ycombinator.com)'
        }

    def fetch_page(self, url=None):
        LOG.debug(f"准备获取 Hacker News 页面。")
        target_url = url or self.base_url
        response = requests.get(target_url, headers=self.headers)
        response.raise_for_status()
        return response.text

    def parse_stories(self, html):
        LOG.debug(f"解析 Hacker News 页面。")
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.select('.athing')
        subtexts = soup.select('.subtext')

        stories = []
        for idx, item in enumerate(items):
            title_elem = item.select_one('.titleline > a')
            if not title_elem:
                continue

            title = title_elem.get_text(strip=True)
            link = title_elem['href']
            score_elem = subtexts[idx].select_one('.score') if idx < len(subtexts) else None
            score = score_elem.get_text() if score_elem else '0 points'

            stories.append({
                'title': title,
                'link': link,
                'score': score
            })
        return stories

    def get_top_stories(self):
        LOG.debug(f"获取 Hacker News 首页新闻列表。")
        html = self.fetch_page()
        return self.parse_stories(html)
    
    def export_top_stories(self):
        LOG.debug(f"导出 Hacker News 首页新闻列表。")
        stories = self.get_top_stories()

        today = datetime.now().date().isoformat()  # 获取今天的日期
        repo_dir = os.path.join('hackernews', 'top_stories')  # 构建目录路径
        os.makedirs(repo_dir, exist_ok=True)  # 确保目录存在

        file_path = os.path.join(repo_dir, f'{today}.md')
        with open(file_path, 'w') as file:
            file.write(f"# Hacker News Top Stories ({today})\n\n")
            for i, story in enumerate(stories, 1):
                file.write(f"{i}. {story['title']} ({story['score']})\n")
                file.write(f"   {story['link']}\n\n")
        
        LOG.info(f"Hacker News 首页新闻列表导出成功：{file_path}")
        return file_path
    
if __name__ == '__main__':
    client = HackernewsClient()
    client.export_top_stories()
