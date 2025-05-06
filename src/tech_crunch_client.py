import json
import feedparser
from datetime import datetime, timedelta
import os  # 导入os模块用于文件和目录操作
from logger import LOG  # 导入日志模块

class TechCrunchRSSClient:
    def __init__(self, max_articles=30):
        self.max_articles = max_articles
        self.articles = []
        self.rss_sources = load_rss_sources()

    def fetch_articles(self, feed_url, since=None):
        feed = feedparser.parse(feed_url)
        entries = feed.entries

        # 如果指定了 from_date，则过滤发布日期
        if since:
            filtered = []
            for entry in entries:
                if hasattr(entry, 'published_parsed'):
                    published = datetime(*entry.published_parsed[:6])
                    if published >= since:
                        filtered.append(entry)
            entries = filtered

        # 截取 max_articles 篇
        entries = entries[:5]

        # 返回文章列表
        articles = []
        for entry in entries:
            articles.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.published if hasattr(entry, 'published') else "N/A",
                "summary": entry.summary if hasattr(entry, 'summary') else "N/A"
            })

        return articles
    
    def fetch_all_articles(self, since=None):
        for source in self.rss_sources:
            articles = self.fetch_articles(source["feed_url"], since)
            self.articles.extend(articles)
        return self.articles[:self.max_articles]

    def export_progress_by_date_range(self, days):
        today = datetime.now()
        since = today - timedelta(days=days)
        LOG.info(f"TechCrunch 从 {since.strftime('%Y-%m-%d')} 到 {today.strftime('%Y-%m-%d')} 的文章")
        articles = self.fetch_all_articles(since)

        repo_dir = os.path.join('tech_crunch')  # 构建目录路径
        os.makedirs(repo_dir, exist_ok=True)  # 确保目录存在
        
        # 更新文件名以包含日期范围
        date_str = f"{since.strftime('%Y-%m-%d')}_to_{today.strftime('%Y-%m-%d')}"
        file_path = os.path.join(repo_dir, f'{date_str}.md')  # 构建文件路径
        
        with open(file_path, 'w') as file:
            file.write(f"#  TechCrunch ({since} to {today})\n\n")
            for article in articles:
                file.write(f"- {article['title']}\n")
                file.write(f"- {article['summary'][:100]}\n")
                file.write(f"- link: {article['link']}\n\n")
        
        LOG.info(f"TechCrunch 最新进展文件生成： {file_path}")  # 记录日志
        return file_path

def load_rss_sources(file_path="techcrunch_rss_sources.json"):
    with open(file_path, "r") as file:
        return json.load(file)

if __name__ == "__main__":
    # 加载 RSS 源配置
    rss_sources = load_rss_sources()

    # 获取并显示每个源的文章

    client = TechCrunchRSSClient()
    articles = client.fetch_all_articles()
    client.export_progress_by_date_range(7)
