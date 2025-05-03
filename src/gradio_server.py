import gradio as gr  # 导入gradio库用于创建GUI

from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器
from hackernews_client import HackernewsClient  # 导入HackerNews客户端

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)
hackernews_client = HackernewsClient()  # 创建HackerNews客户端实例

def export_progress_by_date_range(repo, days):
    # 定义一个函数，用于导出和生成指定时间范围内项目的进展报告
    raw_file_path = github_client.export_progress_by_date_range(repo, days)  # 导出原始数据文件路径
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)  # 生成并获取报告内容及文件路径

    return report, report_file_path  # 返回报告内容和报告文件路径

def export_hackernews():
    # 定义一个函数，用于导出和生成HackerNews的报告
    raw_file_path = hackernews_client.export_top_stories()  # 导出HackerNews原始数据文件路径
    report, report_file_path = report_generator.generate_hackernews_report(raw_file_path)  # 生成并获取HackerNews报告内容及文件路径

    return report, report_file_path  # 返回报告内容和报告文件路径

# 创建GitHub项目进展报告Tab
with gr.Blocks() as github_tab:
    with gr.Row():
        repo_dropdown = gr.Dropdown(
            subscription_manager.list_subscriptions(), 
            label="订阅列表", 
            info="已订阅GitHub项目"
        )
        days_slider = gr.Slider(
            value=2, 
            minimum=1, 
            maximum=7, 
            step=1, 
            label="报告周期", 
            info="生成项目过去一段时间进展，单位：天"
        )
    
    export_button = gr.Button("导出报告")
    
    with gr.Row():
        report_markdown = gr.Markdown()
        report_file = gr.File(label="下载报告")
    
    export_button.click(
        fn=export_progress_by_date_range,
        inputs=[repo_dropdown, days_slider],
        outputs=[report_markdown, report_file]
    )

# 创建HackerNews报告Tab
with gr.Blocks() as hackernews_tab:
    export_hn_button = gr.Button("导出HackerNews热门文章")
    
    with gr.Row():
        hn_report_markdown = gr.Markdown()
        hn_report_file = gr.File(label="下载HackerNews报告")
    
    export_hn_button.click(
        fn=export_hackernews,
        inputs=[],
        outputs=[hn_report_markdown, hn_report_file]
    )

# 创建Gradio界面，使用Tab切换不同功能
demo = gr.TabbedInterface(
    [github_tab, hackernews_tab],
    ["GitHub项目进展", "HackerNews热门"]
)

if __name__ == "__main__":
    demo.launch()  # 启动界面并设置为公共可访问
    # 可选带有用户认证的启动方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))