# src/llm.py

import os
from openai import OpenAI

class LLM:
    def __init__(self):
        self.client = OpenAI()

    def generate_daily_report(self, markdown_content, dry_run=False):
        prompt = f"以下是项目的最新进展，根据功能合并同类项，形成一份简报 \n\n{markdown_content}"
        if dry_run:
            with open("daily_progress/prompt.txt", "w+") as f:
                f.write(prompt)
            return "DRY RUN"

        print("Before call GPT")
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的项目管理专家，擅长根据项目进展生成简报。你的职责是：1. 根据项目进展生成一份简报，内容至少包含：1）新增功能；2）主要改进；3）修复问题；2. 简报内容需要精炼，不要冗余。"},
                {"role": "user", "content": prompt}
            ]
        )
        print("After call GPT")
        print(response)
        return response.choices[0].message.content
