import gradio as gr
import base64
import io
from PIL import Image
from typing import Generator, List, Dict
import requests
import json
from openai import OpenAI
import logging
import asyncio
import aiofiles
from concurrent.futures import ThreadPoolExecutor
import zipfile
import os
import tempfile
from pathlib import Path
import random
import time

# 配置日志
logging.basicConfig(level=logging.INFO)

# 常量定义
LOGO_SRC = """data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjwhRE9DVFlQRSBzdmcgUFVCTElDICItLy9XM0MvL0RURCBTVkcgMS4xLy9FTiIgImh0dHA6Ly93d3cudzMub3JnL0dyYXBoaWNzL1NWRy8xLjEvRFREL3N2ZzExLmR0ZCI+Cjxzdmcgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgdmlld0JveD0iMCAwIDUzOCA1MzUiIHZlcnNpb249IjEuMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSIgeG1sbnM6c2VyaWY9Imh0dHA6Ly93d3cuc2VyaWYuY29tLyIgc3R5bGU9ImZpbGwtcnVsZTpldmVub2RkO2NsaXAtcnVsZTpldmVub2RkO3N0cm9rZS1saW5lam9pbjpyb3VuZDtzdHJva2UtbWl0ZXJsaW1pdDoyOyI+CiAgICA8ZyB0cmFuc2Zvcm09Im1hdHJpeCgxLDAsMCwxLC0xNDcuODcxLDAuMDAxOTA4NjMpIj4KICAgICAgICA8cGF0aCBkPSJNMTk1LjY3LDIyMS42N0MxOTYuNzMsMjA1LjM3IDIwMC4yOCwxODkuNzYgMjA3LjkxLDE3NS4zN0MyMjcuOTgsMTM3LjUxIDI1OS4zMywxMTQuODggMzAyLjAxLDExMS42M0MzMzQuMTUsMTA5LjE4IDM2Ni41OSwxMTAuNiAzOTguODksMTEwLjNDNDAwLjUzLDExMC4yOCA0MDIuMTYsMTEwLjMgNDA0LjQsMTEwLjNDNDA0LjQsMTAxLjk5IDQwNC41Niw5NC4wNSA0MDQuMjMsODYuMTJDNDA0LjE4LDg0Ljg0IDQwMi4xNSw4My4xMyA0MDAuNjYsODIuNDlDMzgzLjIzLDc1LjAyIDM3My4wNSw1OS43OSAzNzMuOTYsNDAuOTZDMzc1LjA5LDE3LjU0IDM5MS40NywyLjY2IDQxMC42NSwwLjM3QzQzNy44OSwtMi44OSA0NTUuNTYsMTUuODQgNDU5LjI2LDM0LjY5QzQ2Mi45Niw1My41NyA0NTIuMTgsNzYuOTMgNDMyLjgxLDgyLjY2QzQzMS42NCw4My4wMSA0MzAuMzMsODUuMjMgNDMwLjI4LDg2LjYyQzQzMC4wMyw5NC4yNiA0MzAuMTYsMTAxLjkyIDQzMC4xNiwxMTAuM0w0MzUuNjMsMTEwLjNDNDYzLjc5LDExMC4zIDQ5MS45NiwxMTAuMjggNTIwLjEyLDExMC4zQzU3NC44NCwxMTAuMzYgNjIzLjA0LDE0OC4zNSA2MzUuNjcsMjAxLjU1QzYzNy4yMywyMDguMTMgNjM3LjgzLDIxNC45MyA2MzguODksMjIxLjY3QzY2MC40MywyMjQuOTQgNjc1LjE5LDIzNi42MiA2ODIuMzYsMjU3LjRDNjgzLjU5LDI2MC45NyA2ODQuNjUsMjY0LjgyIDY4NC42NywyNjguNTRDNjg0Ljc3LDI4My4zNCA2ODUuNzYsMjk4LjMxIDY4My45NCwzMTIuOTFDNjgwLjg5LDMzNy4yOSA2NjIuODYsMzUzLjM2IDYzOC40NywzNTUuODJDNjM1LjE0LDM4NS4wOCA2MjEuOTEsNDA5LjQxIDYwMC40NSw0MjkuMjFDNTgxLjYsNDQ2LjYxIDU1OS4xNCw0NTcuNSA1MzMuNTcsNDU5LjE4QzUwOC4xOCw0NjAuODQgNDgyLjY0LDQ2MC4yIDQ1Ny4xNiw0NjAuMzhDNDM1LjE2LDQ2MC41MyA0MTMuMTcsNDYwLjM0IDM5MS4xNyw0NjAuNTNDMzg4Ljc2LDQ2MC41NSAzODUuOTUsNDYxLjU2IDM4NC4wMyw0NjMuMDRDMzcxLjU0LDQ3Mi42MiAzNTkuMTMsNDgyLjMxIDM0Ni45Miw0OTIuMjVDMzM4Ljk0LDQ5OC43NSAzMzEuMzksNTA1Ljc3IDMyMy41Niw1MTIuNDZDMzE3LjQ1LDUxNy42OCAzMTAuOTMsNTIyLjQ0IDMwNS4xMSw1MjcuOTVDMzAxLjE5LDUzMS42NiAyOTYuNTIsNTMzLjE3IDI5MS42OSw1MzQuMzZDMjg1LjY1LDUzNS44NSAyNzkuMjIsNTI5LjEzIDI3OS4wMSw1MjEuMTlDMjc4LjgsNTEyLjg2IDI3OC45NSw1MDQuNTMgMjc4Ljk0LDQ5Ni4xOUwyNzguOTQsNDU2LjY5QzIzMi44Miw0MzguMTYgMjAzLjU2LDQwNi4yMyAxOTUuMDcsMzU2LjA4QzE5My4yNiwzNTUuNzUgMTkwLjg0LDM1NS40MSAxODguNDgsMzU0Ljg2QzE2Ny40NiwzNDkuOTEgMTU1LjA0LDMzNi4wMiAxNTAuNzIsMzE1LjYyQzE0Ni45OCwyOTcuOTkgMTQ2LjksMjc5LjY3IDE1MC42MSwyNjIuMDlDMTU1LjU1LDIzOC42OCAxNzEuNDIsMjI1LjU5IDE5NS42NiwyMjEuNjdMMTk1LjY3LDIyMS42N1pNMzA4LjA3LDQ4Ny44MkMzMTUuOTQsNDgxLjEzIDMyMi44NSw0NzUuMTMgMzI5LjksNDY5LjNDMzQ0LjM5LDQ1Ny4zMSAzNTguOSw0NDUuMzYgMzczLjU0LDQzMy41NkMzNzUuMTcsNDMyLjI1IDM3Ny42OCw0MzEuNCAzNzkuNzksNDMxLjM5QzQxNC43OCw0MzEuMjYgNDQ5Ljc4LDQzMS4zOCA0ODQuNzcsNDMxLjI0QzUwMC4zOSw0MzEuMTggNTE2LjEzLDQzMS43NiA1MzEuNjIsNDMwLjE2QzU3Ni45Miw0MjUuNDkgNjA5LjI0LDM4Ny43NyA2MDguOTUsMzQ0Ljg0QzYwOC42OCwzMDUuNTIgNjA4LjkzLDI2Ni4xOSA2MDguODcsMjI2Ljg2QzYwOC44NywyMjMuMjIgNjA4LjU4LDIxOS41NSA2MDcuOTksMjE1Ljk2QzYwMy4xMSwxODYuMjkgNTg4LjYxLDE2My4zMyA1NjEuMzIsMTQ5LjMyQzU0OS4wNCwxNDMuMDIgNTM2LjE1LDEzOS4yOSA1MjIuMjIsMTM5LjI5QzQ1My45LDEzOS4zMiAzODUuNTgsMTM5LjIgMzE3LjI2LDEzOS4zNUMzMDkuMiwxMzkuMzcgMzAwLjk2LDEzOS44OSAyOTMuMTEsMTQxLjZDMjU0LjE5LDE1MC4wNyAyMjUuMzMsMTg1LjY5IDIyNS4wMywyMjUuNDJDMjI0LjgsMjU2LjA4IDIyNC44NiwyODYuNzQgMjI0Ljk5LDMxNy40QzIyNS4wNSwzMzAuNTMgMjI0Ljc0LDM0My43NiAyMjYuMTgsMzU2Ljc3QzIyOC43NCwzODAuMDUgMjQwLjYsMzk4LjYyIDI1OC43OSw0MTIuOTNDMjczLjA0LDQyNC4xNCAyODkuNjMsNDMwLjAyIDMwNy42MSw0MzEuNTVDMzA3LjgyLDQzMi4wMyAzMDguMDYsNDMyLjMzIDMwOC4wNiw0MzIuNjNDMzA4LjA4LDQ1MC42IDMwOC4wOCw0NjguNTcgMzA4LjA4LDQ4Ny44MUwzMDguMDcsNDg3LjgyWk00MzUuNzksNDMuMzNDNDM1Ljk1LDMzLjQyIDQyNy42MSwyNC42NSA0MTcuOCwyNC40QzQwNi43NiwyNC4xMiAzOTguMjUsMzIuMDUgMzk4LjEzLDQyLjc0QzM5OC4wMSw1My4wNCA0MDYuNiw2Mi4xMiA0MTYuNDIsNjIuMDhDNDI3LjExLDYyLjA0IDQzNS42MSw1My44MSA0MzUuNzgsNDMuMzNMNDM1Ljc5LDQzLjMzWiIgc3R5bGU9ImZpbGw6cmdiKDczLDQ3LDExOCk7ZmlsbC1ydWxlOm5vbnplcm87Ii8+CiAgICAgICAgPHBhdGggZD0iTTQxOS4zLDM5MS42M0MzNzQuNDYsMzkwLjQgMzQxLjUxLDM3Mi42MyAzMTguMDEsMzM3LjcxQzMxNS42NywzMzQuMjMgMzEzLjc3LDMzMC4wNCAzMTMuMSwzMjUuOTVDMzExLjg0LDMxOC4yOCAzMTYuNTMsMzExLjcgMzIzLjcyLDMwOS40NkMzMzAuNjYsMzA3LjI5IDMzOC4zMiwzMTAuMSAzNDEuOTgsMzE3LjAzQzM0OS4xNSwzMzAuNjMgMzU5LjE2LDM0MS4zNSAzNzIuMywzNDkuMzFDNDAxLjMyLDM2Ni44OSA0NDQuNTYsMzYzLjcgNDcwLjYxLDM0Mi4zNUM0NzkuMSwzMzUuMzkgNDg2LjA4LDMyNy40MSA0OTEuNTUsMzE3Ljk3QzQ5NS4wNSwzMTEuOTMgNTAwLjIsMzA4LjE4IDUwNy40NywzMDguOTVDNTEzLjczLDMwOS42MSA1MTguODYsMzEyLjg4IDUyMC4xMiwzMTkuMjFDNTIwLjksMzIzLjEzIDUyMC43MywzMjguMjIgNTE4LjgzLDMzMS41NUM1MDAuNjMsMzYzLjMyIDQ3My41NSwzODIuOTUgNDM3LjI5LDM4OS4zN0M0MzAuNDQsMzkwLjU4IDQyMy40OCwzOTEuMTIgNDE5LjI5LDM5MS42M0w0MTkuMywzOTEuNjNaIiBzdHlsZT0iZmlsbDpyZ2IoMjUwLDEzOSwxKTtmaWxsLXJ1bGU6bm9uemVybzsiLz4KICAgICAgICA8cGF0aCBkPSJNNDYyLjcxLDI0MC4xOUM0NjIuOCwyMTYuOTEgNDgwLjI0LDE5OS43OSA1MDQuMDEsMTk5LjY3QzUyNi41NywxOTkuNTUgNTQ0Ljg5LDIxOC4wNyA1NDQuNTEsMjQxLjM0QzU0NC4xOCwyNjEuODUgNTMwLjA5LDI4MS45NiA1MDEuOTEsMjgxLjIzQzQ4MC42OCwyODAuNjggNDYyLjE1LDI2My44IDQ2Mi43MSwyNDAuMkw0NjIuNzEsMjQwLjE5WiIgc3R5bGU9ImZpbGw6cmdiKDI1MCwxMzksMSk7ZmlsbC1ydWxlOm5vbnplcm87Ii8+CiAgICAgICAgPHBhdGggZD0iTTM3MC45OSwyNDAuMDhDMzcxLDI2Mi43OSAzNTIuNTMsMjgxLjM1IDMyOS44OSwyODEuMzdDMzA3LjA1LDI4MS40IDI4OC45NiwyNjMuNDIgMjg4Ljk2LDI0MC42OEMyODguOTYsMjE4LjE0IDMwNi43MywyMDAgMzI5LjE2LDE5OS42MkMzNTIuMDIsMTk5LjI0IDM3MC45OCwyMTcuNTcgMzcwLjk5LDI0MC4wOFoiIHN0eWxlPSJmaWxsOnJnYigyNTAsMTM5LDEpO2ZpbGwtcnVsZTpub256ZXJvOyIvPgogICAgPC9nPgo8L3N2Zz4K"""

# 优化的标题样式
TITLE = f"""<style>
  .joy-header {{
    display: flex; 
    align-items: center; 
    justify-content: center;
    gap: 24px; 
    margin: 0 0 24px;
    padding: 28px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.25);
    color: white;
  }}
  .joy-header h1 {{
    margin: 0; 
    font-size: 2.4rem; 
    line-height: 1.2;
    font-weight: 700;
    text-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }}
  .joy-header p {{
    margin: 6px 0 0; 
    font-size: 1.1rem; 
    opacity: 0.95;
  }}
  .joy-header img {{
    height: 72px;
    filter: brightness(0) invert(1) drop-shadow(0 2px 4px rgba(0,0,0,0.1));
  }}
  
  /* 简化的状态框样式 */
  .status-box {{
    padding: 12px 20px;
    border-radius: 12px;
    margin: 12px 0;
    text-align: center;
    font-weight: 500;
    transition: all 0.3s ease;
  }}
  .status-success {{
    background-color: #d1fae5;
    color: #065f46;
    border: 1px solid #6ee7b7;
  }}
  .status-error {{
    background-color: #fee2e2;
    color: #991b1b;
    border: 1px solid #fca5a5;
  }}
  .status-info {{
    background-color: #dbeafe;
    color: #1e40af;
    border: 1px solid #93c5fd;
  }}
  
  /* 权重显示优化 */
  .weight-display {{
    font-size: 1.05em;
    font-weight: 600;
    color: #667eea;
    text-align: left;
    margin: 8px 0;
    padding: 8px;
    background: #f0f4f8;
    border-radius: 8px;
  }}
  
  /* 表格样式 */
  .caption-table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin: 16px 0;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 0 0 1px #e2e8f0;
  }}
  .caption-table th {{
    background: #f8fafc;
    color: #475569;
    font-weight: 600;
    padding: 12px 16px;
    text-align: left;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }}
  .caption-table td {{
    padding: 12px 16px;
    border-top: 1px solid #e2e8f0;
    color: #334155;
    font-size: 0.95rem;
    line-height: 1.5;
  }}
  .caption-table tr:hover td {{
    background-color: #f8fafc;
  }}
  .caption-table strong {{
    color: #1e293b;
    font-weight: 600;
  }}
  .caption-table em {{
    color: #ef4444;
    font-style: normal;
    font-size: 0.875rem;
  }}
  
  /* 信息卡片 */
  .info-card {{
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px;
    margin: 16px 0;
  }}
  .info-card h3 {{
    color: #1e293b;
    font-size: 1.1rem;
    font-weight: 600;
    margin: 0 0 12px;
  }}
  .info-card p {{
    color: #475569;
    font-size: 0.95rem;
    line-height: 1.6;
    margin: 8px 0;
  }}
  .info-card ul {{
    margin: 8px 0;
    padding-left: 20px;
  }}
  .info-card li {{
    color: #475569;
    font-size: 0.95rem;
    line-height: 1.6;
    margin: 4px 0;
  }}
  
  /* 提示词组样式 */
  .prompt-group {{
    background: #f8fafc;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px;
    margin: 12px 0;
    transition: all 0.3s ease;
  }}
  .prompt-group:hover {{
    border-color: #cbd5e1;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  }}
  .prompt-group.active {{
    border-color: #667eea;
    background: #f0f4ff;
  }}
  
  /* 按钮美化 */
  .gr-button-primary {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
    transition: all 0.3s ease !important;
  }}
  .gr-button-primary:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
  }}
</style>
<div class="joy-header">
  <img src="{LOGO_SRC}" alt="JoyCaption logo">
  <div>
    <h1>JoyCaption <span style="font-weight:400;opacity:0.9">混合模式版本</span></h1>
    <p>智能图像描述生成器 | 支持批量处理与混合模式</p>
  </div>
</div>"""

# Caption类型参考表格
CAPTION_TYPE_TABLE = """
<table class="caption-table">
  <tr><th style="width:25%">模式</th><th>描述</th></tr>
  <tr><td><strong>详细描述</strong></td>
      <td>正式、详细的散文描述。</td></tr>
  <tr><td><strong>随意描述</strong></td>
      <td>类似详细描述，但语调更友好、对话式。</td></tr>
  <tr><td><strong>直接描述</strong></td>
      <td>客观、无修饰，比详细描述更简洁。</td></tr>
  <tr><td><strong>Stable Diffusion提示词</strong></td>
      <td>逆向工程可能在SD/T2I模型中生成该图像的提示词。<br><em>⚠︎ 实验性功能 - 约3%的失败率。</em></td></tr>
  <tr><td><strong>MidJourney提示词</strong></td>
      <td>与上述类似，但调整为MidJourney的提示词风格。<br><em>⚠︎ 实验性功能 - 约3%的失败率。</em></td></tr>
  <tr><td><strong>Danbooru标签</strong></td>
      <td>严格遵循Danbooru约定的逗号分隔标签（artist:, copyright:等）。仅小写下划线。<br><em>⚠︎ 实验性功能 - 约3%的失败率。</em></td></tr>
  <tr><td><strong>e621标签</strong></td>
      <td>e621风格的字母顺序、命名空间标签 - 包括相关的物种/元标签。<br><em>⚠︎ 实验性功能 - 约3%的失败率。</em></td></tr>
  <tr><td><strong>Rule34标签</strong></td>
      <td>Rule34风格的字母顺序标签转储；artist/copyright/character前缀优先。<br><em>⚠︎ 实验性功能 - 约3%的失败率。</em></td></tr>
  <tr><td><strong>Booru-like标签</strong></td>
      <td>当您需要标签但不需要特定Booru格式时的宽松标签列表。<br><em>⚠︎ 实验性功能 - 约3%的失败率。</em></td></tr>
  <tr><td><strong>艺术评论</strong></td>
      <td>艺术历史评论段落：构图、象征意义、风格、光线、运动等。</td></tr>
  <tr><td><strong>产品文案</strong></td>
      <td>简短的营销文案，就像在销售所描绘的物品。</td></tr>
  <tr><td><strong>社媒文案</strong></td>
      <td>针对Instagram或BlueSky等平台的吸引人的标题。</td></tr>
</table>
<p style="margin-top:12px;color:#64748b;font-size:0.9rem">
  <strong>Booru模式注意事项：</strong>它们针对动漫风格/插画图像进行了调整；在真实世界照片或高度抽象的艺术作品上准确性会下降。
</p>
"""

# 保持英文的提示词模板（保持不变）
CAPTION_TYPE_MAP = {
    "详细描述": [
        "Write a detailed description for this image.",
        "Write a detailed description for this image in {word_count} words or less.",
        "Write a {length} detailed description for this image.",
    ],
    "随意描述": [
        "Write a descriptive caption for this image in a casual tone.",
        "Write a descriptive caption for this image in a casual tone within {word_count} words.",
        "Write a {length} descriptive caption for this image in a casual tone.",
    ],
    "直接描述": [
        "Write a straightforward caption for this image. Begin with the main subject and medium. Mention pivotal elements—people, objects, scenery—using confident, definite language. Focus on concrete details like color, shape, texture, and spatial relationships. Show how elements interact. Omit mood and speculative wording. If text is present, quote it exactly. Note any watermarks, signatures, or compression artifacts. Never mention what's absent, resolution, or unobservable details. Vary your sentence structure and keep the description concise, without starting with \"This image is…\" or similar phrasing.",
        "Write a straightforward caption for this image within {word_count} words. Begin with the main subject and medium. Mention pivotal elements—people, objects, scenery—using confident, definite language. Focus on concrete details like color, shape, texture, and spatial relationships. Show how elements interact. Omit mood and speculative wording. If text is present, quote it exactly. Note any watermarks, signatures, or compression artifacts. Never mention what's absent, resolution, or unobservable details. Vary your sentence structure and keep the description concise, without starting with \"This image is…\" or similar phrasing.",
        "Write a {length} straightforward caption for this image. Begin with the main subject and medium. Mention pivotal elements—people, objects, scenery—using confident, definite language. Focus on concrete details like color, shape, texture, and spatial relationships. Show how elements interact. Omit mood and speculative wording. If text is present, quote it exactly. Note any watermarks, signatures, or compression artifacts. Never mention what's absent, resolution, or unobservable details. Vary your sentence structure and keep the description concise, without starting with \"This image is…\" or similar phrasing.",
    ],
    "Stable Diffusion提示词": [
        "Output a stable diffusion prompt that is indistinguishable from a real stable diffusion prompt.",
        "Output a stable diffusion prompt that is indistinguishable from a real stable diffusion prompt. {word_count} words or less.",
        "Output a {length} stable diffusion prompt that is indistinguishable from a real stable diffusion prompt.",
    ],
    "MidJourney提示词": [
        "Write a MidJourney prompt for this image.",
        "Write a MidJourney prompt for this image within {word_count} words.",
        "Write a {length} MidJourney prompt for this image.",
    ],
    "Danbooru标签": [
		"Generate only comma-separated Danbooru tags (lowercase_underscores). Strict order: `artist:`, `copyright:`, `character:`, `meta:`, then general tags. Include counts (1girl), appearance, clothing, accessories, pose, expression, actions, background. Use precise Danbooru syntax. No extra text.",
		"Generate only comma-separated Danbooru tags (lowercase_underscores). Strict order: `artist:`, `copyright:`, `character:`, `meta:`, then general tags. Include counts (1girl), appearance, clothing, accessories, pose, expression, actions, background. Use precise Danbooru syntax. No extra text. {word_count} words or less.",
		"Generate only comma-separated Danbooru tags (lowercase_underscores). Strict order: `artist:`, `copyright:`, `character:`, `meta:`, then general tags. Include counts (1girl), appearance, clothing, accessories, pose, expression, actions, background. Use precise Danbooru syntax. No extra text. {length} length.",
	],
	"e621标签": [
		"Write a comma-separated list of e621 tags in alphabetical order for this image. Start with the artist, copyright, character, species, meta, and lore tags (if any), prefixed by 'artist:', 'copyright:', 'character:', 'species:', 'meta:', and 'lore:'. Then all the general tags.",
		"Write a comma-separated list of e621 tags in alphabetical order for this image. Start with the artist, copyright, character, species, meta, and lore tags (if any), prefixed by 'artist:', 'copyright:', 'character:', 'species:', 'meta:', and 'lore:'. Then all the general tags. Keep it under {word_count} words.",
		"Write a {length} comma-separated list of e621 tags in alphabetical order for this image. Start with the artist, copyright, character, species, meta, and lore tags (if any), prefixed by 'artist:', 'copyright:', 'character:', 'species:', 'meta:', and 'lore:'. Then all the general tags.",
	],
	"Rule34标签": [
		"Write a comma-separated list of rule34 tags in alphabetical order for this image. Start with the artist, copyright, character, and meta tags (if any), prefixed by 'artist:', 'copyright:', 'character:', and 'meta:'. Then all the general tags.",
		"Write a comma-separated list of rule34 tags in alphabetical order for this image. Start with the artist, copyright, character, and meta tags (if any), prefixed by 'artist:', 'copyright:', 'character:', and 'meta:'. Then all the general tags. Keep it under {word_count} words.",
		"Write a {length} comma-separated list of rule34 tags in alphabetical order for this image. Start with the artist, copyright, character, and meta tags (if any), prefixed by 'artist:', 'copyright:', 'character:', and 'meta:'. Then all the general tags.",
	],
	"Booru-like标签": [
		"Write a list of Booru-like tags for this image.",
		"Write a list of Booru-like tags for this image within {word_count} words.",
		"Write a {length} list of Booru-like tags for this image.",
	],
    "艺术评论": [
        "Analyze this image like an art critic would with information about its composition, style, symbolism, the use of color, light, any artistic movement it might belong to, etc.",
        "Analyze this image like an art critic would with information about its composition, style, symbolism, the use of color, light, any artistic movement it might belong to, etc. Keep it within {word_count} words.",
        "Analyze this image like an art critic would with information about its composition, style, symbolism, the use of color, light, any artistic movement it might belong to, etc. Keep it {length}.",
    ],
    "产品文案": [
        "Write a caption for this image as though it were a product listing.",
        "Write a caption for this image as though it were a product listing. Keep it under {word_count} words.",
        "Write a {length} caption for this image as though it were a product listing.",
    ],
    "社媒文案": [
        "Write a caption for this image as if it were being used for a social media post.",
        "Write a caption for this image as if it were being used for a social media post. Limit the caption to {word_count} words.",
        "Write a {length} caption for this image as if it were being used for a social media post.",
    ],
}

# 保持英文的额外选项
EXTRA_OPTIONS_MAP = {
    "包含光照信息": "Include information about lighting.",
    "包含拍摄角度信息": "Include information about camera angle.",
    "包含水印信息": "Include information about whether there is a watermark or not.",
    "包含JPEG压缩痕迹信息": "Include information about whether there are JPEG artifacts or not.",
    "包含相机参数信息": "If it is a photo you MUST include information about what camera was likely used and details such as aperture, shutter speed, ISO, etc.",
    "保持内容健康": "Do NOT include anything sexual; keep it PG.",
    "不提及图片分辨率": "Do NOT mention the image's resolution.",
    "包含美学质量评价": "You MUST include information about the subjective aesthetic quality of the image from low to very high.",
    "包含构图风格信息": "Include information on the image's composition style, such as leading lines, rule of thirds, or symmetry.",
    "不提及图片中的文字": "Do NOT mention any text that is in the image.",
    "包含景深信息": "Specify the depth of field and whether the background is in focus or blurred.",
    "包含光源类型信息": "If applicable, mention the likely use of artificial or natural lighting sources.",
    "避免模糊语言": "Do NOT use any ambiguous language.",
    "包含内容分级": "Include whether the image is sfw, suggestive, or nsfw.",
    "只描述重要元素": "ONLY describe the most important elements of the image.",
    "不包含艺术家信息": "If it is a work of art, do not include the artist's name or the title of the work.",
    "包含图片方向信息": "Identify the image orientation (portrait, landscape, or square) and aspect ratio if obvious.",
    "包含拍摄距离信息": "Mention whether the image depicts an extreme close-up, close-up, medium close-up, medium shot, cowboy shot, medium wide shot, wide shot, or extreme wide shot.",
    "不描述情感氛围": "Do not mention the mood/feeling/etc of the image.",
    "包含拍摄角度高度": "Explicitly specify the vantage height (eye-level, low-angle worm's-eye, bird's-eye, drone, rooftop, etc.).",
    "避免无用的描述开头": "Your response will be used by a text-to-image model, so avoid useless meta phrases like \"This image shows…\", \"You are looking at...\", etc.",
}

# 🔥 新增：分批文件处理器
class BatchFileProcessor:
    def __init__(self, batch_size=50):
        self.batch_size = batch_size
        
    def create_batches(self, files):
        """创建批次，避免内存溢出"""
        batches = []
        for i in range(0, len(files), self.batch_size):
            batches.append(files[i:i + self.batch_size])
        return batches
    
def create_openai_client(api_key: str, base_url: str) -> OpenAI:
    """创建OpenAI客户端"""
    return OpenAI(api_key=api_key, base_url=base_url)


def build_prompt(caption_type: str, caption_length: str | int, extra_options: list[str]) -> str:
    """构建英文提示词"""
    if caption_length == "any":
        map_idx = 0
    elif isinstance(caption_length, str) and caption_length.isdigit():
        map_idx = 1
    else:
        map_idx = 2
    
    prompt = CAPTION_TYPE_MAP[caption_type][map_idx]

    if extra_options:
        # 将中文选项转换为对应的英文提示词
        english_options = [EXTRA_OPTIONS_MAP.get(option, option) for option in extra_options]
        prompt += " " + " ".join(english_options)
    
    return prompt.format(
        length=caption_length,
        word_count=caption_length,
    )


def test_api_connection(base_url: str, api_key: str) -> tuple[bool, str]:
    """测试API连接"""
    try:
        client = create_openai_client(api_key, base_url)
        models = client.models.list()
        if models.data:
            return True, f"✅ 连接成功！可用模型: {models.data[0].id}"
        else:
            return False, "❌ 连接失败：没有可用的模型"
    except Exception as e:
        return False, f"❌ 连接失败：{str(e)}"


def image_to_base64(image: Image.Image) -> str:
    """将PIL图像转换为base64"""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    image_bytes = buffer.getvalue()
    return base64.b64encode(image_bytes).decode("utf-8")


def get_safe_filename(filename: str) -> str:
    """获取安全的文件名，移除非法字符"""
    # 移除路径部分，只保留文件名
    filename = os.path.basename(filename)
    # 替换非法字符
    illegal_chars = '<>:"/\\|?*'
    for char in illegal_chars:
        filename = filename.replace(char, '_')
    return filename


def generate_single_caption(
    image: Image.Image,
    prompt: str,
    base_url: str,
    api_key: str,
    temperature: float,
    top_p: float,
    max_tokens: int
) -> str:
    """生成单个图像描述（用于批量处理）"""
    try:
        base64_image = image_to_base64(image)
        image_data = f"data:image/png;base64,{base64_image}"
        
        client = create_openai_client(api_key, base_url)
        model_name = client.models.list().data[0].id
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a helpful image captioner.',
                },
                {
                    'role': 'user',
                    'content': [
                        {'type': 'text', 'text': prompt},
                        {'type': 'image_url', 'image_url': {'url': image_data}}
                    ],
                }
            ],
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logging.error(f"生成描述时出错: {str(e)}")
        return f"Error: {str(e)}"


def generate_caption(
    image: Image.Image,
    prompt: str,
    base_url: str,
    api_key: str,
    temperature: float,
    top_p: float,
    max_tokens: int
) -> Generator[str, None, None]:
    """生成图像描述（单图处理用）"""
    if image is None:
        yield "❌ 请先上传图片"
        return
    
    if not base_url or not api_key:
        yield "❌ 请配置API地址和密钥"
        return

    try:
        yield "🔄 正在处理图片..."
        
        caption = generate_single_caption(
            image, prompt, base_url, api_key, temperature, top_p, max_tokens
        )
        
        if caption.startswith("Error:"):
            yield f"❌ 生成失败: {caption}"
        else:
            yield f"✅ 生成完成！\n\n{caption}"
        
    except Exception as e:
        logging.error(f"生成描述时出错: {str(e)}")
        yield f"❌ 生成失败: {str(e)}"


def select_prompt_by_weight(prompt_configs: List[Dict]) -> str:
    """根据权重随机选择一个提示词"""
    if not prompt_configs:
        return ""
    
    # 计算总权重
    total_weight = sum(config['weight'] for config in prompt_configs if config['weight'] > 0)
    if total_weight == 0:
        # 如果所有权重都为0，则均匀选择
        return random.choice(prompt_configs)['prompt']
    
    # 生成随机数
    rand_val = random.uniform(0, total_weight)
    
    # 选择对应的提示词
    current_weight = 0
    for config in prompt_configs:
        if config['weight'] > 0:
            current_weight += config['weight']
            if rand_val <= current_weight:
                return config['prompt']
    
    # 如果由于浮点精度问题没有选中，返回最后一个
    return prompt_configs[-1]['prompt']


def process_batch_images(
    files_info: List[tuple], 
    prompt: str,
    base_url: str, 
    api_key: str,
    temperature: float,
    top_p: float, 
    max_tokens: int,
    progress=gr.Progress()
) -> tuple[str, str]:
    """批量处理图片（单一提示词）"""
    if not files_info:
        return "❌ 请先上传图片", None
    
    if not base_url or not api_key:
        return "❌ 请配置API地址和密钥", None
    
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        results_dir = os.path.join(temp_dir, "results")
        os.makedirs(results_dir, exist_ok=True)
        
        total_images = len(files_info)
        success_count = 0
        error_count = 0
        processed_files = []
        
        progress(0, desc="开始批量处理...")
        
        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for i, (image, original_filename) in enumerate(files_info):
                future = executor.submit(
                    generate_single_caption,
                    image, prompt, base_url, api_key, 
                    temperature, top_p, max_tokens
                )
                futures.append((i, future, original_filename))
            
            # 收集结果
            for i, future, original_filename in futures:
                try:
                    caption = future.result(timeout=60)  # 60秒超时
                    
                    if caption.startswith("Error:"):
                        error_count += 1
                        caption = f"处理失败: {caption}"
                    else:
                        success_count += 1
                    
                    # 使用原始文件名
                    safe_filename = get_safe_filename(original_filename)
                    # 移除原始扩展名，添加.txt扩展名
                    base_name = os.path.splitext(safe_filename)[0]
                    txt_filename = f"{base_name}.txt"
                    
                    filepath = os.path.join(results_dir, txt_filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(caption)
                    
                    processed_files.append(txt_filename)
                    
                    # 更新进度
                    progress_val = (i + 1) / total_images
                    progress(progress_val, desc=f"已处理 {i+1}/{total_images} 张图片")
                    
                except Exception as e:
                    error_count += 1
                    safe_filename = get_safe_filename(original_filename)
                    base_name = os.path.splitext(safe_filename)[0]
                    txt_filename = f"{base_name}.txt"
                    
                    filepath = os.path.join(results_dir, txt_filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(f"处理出错: {str(e)}")
                    
                    processed_files.append(txt_filename)
        
        # 创建ZIP文件
        zip_path = os.path.join(temp_dir, "caption_results.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(results_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, results_dir)
                    zipf.write(file_path, arcname)
        
        # 生成摘要
        summary = f"""
## 📊 批量处理完成！

### 📈 处理统计
- **总图片数**: {total_images}
- **成功处理**: {success_count} 张 
- **处理失败**: {error_count} 张
- **成功率**: {success_count/total_images*100:.1f}%

### 📁 处理的文件
{chr(10).join([f"- {filename}" for filename in processed_files[:10]])}
{f"... 还有 {len(processed_files)-10} 个文件" if len(processed_files) > 10 else ""}

### 📥 下载说明
点击下方下载按钮获取包含所有描述文件的ZIP包。每个图片对应一个同名的`.txt`文件。
        """
        
        return summary, zip_path
        
    except Exception as e:
        logging.error(f"批量处理时出错: {str(e)}")
        return f"❌ 批量处理失败: {str(e)}", None


def process_mix_batch_images(
    files_info: List[tuple], 
    prompt_configs: List[Dict],
    base_url: str, 
    api_key: str,
    temperature: float,
    top_p: float, 
    max_tokens: int,
    progress=gr.Progress()
) -> tuple[str, str]:
    """混合模式批量处理图片"""
    if not files_info:
        return "❌ 请先上传图片", None
    
    if not prompt_configs or all(config['weight'] <= 0 for config in prompt_configs):
        return "❌ 请至少添加一个权重大于0的提示词", None
    
    if not base_url or not api_key:
        return "❌ 请配置API地址和密钥", None
    
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        results_dir = os.path.join(temp_dir, "results")
        os.makedirs(results_dir, exist_ok=True)
        
        total_images = len(files_info)
        success_count = 0
        error_count = 0
        processed_files = []
        prompt_usage_stats = {i: 0 for i in range(len(prompt_configs))}
        
        progress(0, desc="开始混合模式处理...")
        
        # 为每张图片预先分配提示词
        image_prompt_assignments = []
        for i, (image, original_filename) in enumerate(files_info):
            selected_prompt = select_prompt_by_weight(prompt_configs)
            # 找到选中提示词的索引
            prompt_idx = None
            for idx, config in enumerate(prompt_configs):
                if config['prompt'] == selected_prompt:
                    prompt_idx = idx
                    break
            if prompt_idx is not None:
                prompt_usage_stats[prompt_idx] += 1
            image_prompt_assignments.append((image, original_filename, selected_prompt, prompt_idx))
        
        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for i, (image, original_filename, prompt, prompt_idx) in enumerate(image_prompt_assignments):
                future = executor.submit(
                    generate_single_caption,
                    image, prompt, base_url, api_key, 
                    temperature, top_p, max_tokens
                )
                futures.append((i, future, original_filename, prompt_idx))
            
            # 收集结果
            for i, future, original_filename, prompt_idx in futures:
                try:
                    caption = future.result(timeout=60)  # 60秒超时
                    
                    if caption.startswith("Error:"):
                        error_count += 1
                        caption = f"处理失败: {caption}"
                    else:
                        success_count += 1
                    
                    # 添加元信息到结果中
                    prompt_name = f"提示词{prompt_idx + 1}" if prompt_idx is not None else "未知"
                    caption_with_meta = f"{caption}\n\n<!-- 使用提示词: {prompt_name} -->"
                    
                    # 使用原始文件名
                    safe_filename = get_safe_filename(original_filename)
                    # 移除原始扩展名，添加.txt扩展名
                    base_name = os.path.splitext(safe_filename)[0]
                    txt_filename = f"{base_name}.txt"
                    
                    filepath = os.path.join(results_dir, txt_filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(caption)
                    
                    processed_files.append(txt_filename)
                    
                    # 更新进度
                    progress_val = (i + 1) / total_images
                    progress(progress_val, desc=f"已处理 {i+1}/{total_images} 张图片")
                    
                except Exception as e:
                    error_count += 1
                    safe_filename = get_safe_filename(original_filename)
                    base_name = os.path.splitext(safe_filename)[0]
                    txt_filename = f"{base_name}.txt"
                    
                    filepath = os.path.join(results_dir, txt_filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(f"处理出错: {str(e)}")
                    
                    processed_files.append(txt_filename)
        
        # 创建ZIP文件
        zip_path = os.path.join(temp_dir, "mix_caption_results.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(results_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, results_dir)
                    zipf.write(file_path, arcname)
        
        # 生成摘要，包含提示词使用统计
        prompt_stats = []
        for i, config in enumerate(prompt_configs):
            usage_count = prompt_usage_stats.get(i, 0)
            usage_percent = (usage_count / total_images * 100) if total_images > 0 else 0
            weight_percent = (config['weight'] / sum(c['weight'] for c in prompt_configs if c['weight'] > 0) * 100) if sum(c['weight'] for c in prompt_configs if c['weight'] > 0) > 0 else 0
            prompt_stats.append(f"- **提示词{i+1}**: 权重 {config['weight']:.1f} ({weight_percent:.1f}%) → 实际使用 {usage_count} 次 ({usage_percent:.1f}%)")
        
        summary = f"""
## 🎭 混合模式处理完成！

### 📈 处理统计
- **总图片数**: {total_images}
- **成功处理**: {success_count} 张 
- **处理失败**: {error_count} 张
- **成功率**: {success_count/total_images*100:.1f}%

### 🎯 提示词使用统计
{chr(10).join(prompt_stats)}

### 📁 处理的文件
{chr(10).join([f"- {filename}" for filename in processed_files[:10]])}
{f"... 还有 {len(processed_files)-10} 个文件" if len(processed_files) > 10 else ""}

### 📥 下载说明
点击下方下载按钮获取包含所有描述文件的ZIP包。
        """
        
        return summary, zip_path
        
    except Exception as e:
        logging.error(f"混合模式处理时出错: {str(e)}")
        return f"❌ 混合模式处理失败: {str(e)}", None


# 创建Gradio界面
with gr.Blocks(
    theme=gr.themes.Soft(
        primary_hue="purple",
        secondary_hue="purple",
        neutral_hue="slate",
        spacing_size="md",
        radius_size="lg",
    ),
    title="🎨 JoyCaption 混合模式",
    css="""
        .gradio-container {
            max-width: 1400px !important;
            margin: auto !important;
        }
        .gr-group {
            border-radius: 12px !important;
            border-color: #e2e8f0 !important;
        }
        .gr-button {
            border-radius: 8px !important;
            font-weight: 500 !important;
        }
        .gr-input, .gr-dropdown {
            border-radius: 8px !important;
        }
        .gr-form {
            border-radius: 12px !important;
            background: #f8fafc !important;
        }
        .gr-panel {
            border-radius: 12px !important;
        }
        footer {
            display: none !important;
        }
    """
) as demo:
    gr.HTML(TITLE)
    
    # API配置区域
    with gr.Group():
        gr.Markdown("### 🔧 API配置")
        with gr.Row():
            with gr.Column(scale=2):
                api_base_url = gr.Textbox(
                    label="🌐 API地址",
                    value="http://192.168.5.212:8000/v1",
                    placeholder="http://your-api-server:port/v1"
                )
            with gr.Column(scale=2):
                api_key = gr.Textbox(
                    label="🔑 API密钥",
                    value="your-api-key",
                    type="password"
                )
            with gr.Column(scale=1):
                test_btn = gr.Button("🔍 测试连接", variant="secondary", size="sm")
        
        connection_status = gr.HTML("")
    
    # 创建标签页
    with gr.Tabs():
        # 单图处理标签页
        with gr.TabItem("🖼️ 单图处理"):
            with gr.Row():
                with gr.Column(scale=1):
                    # 图片上传区域
                    input_image = gr.Image(
                        type="pil",
                        label="📷 上传图片",
                        height=400,
                    )
                    
                    # 基础设置
                    with gr.Group():
                        gr.Markdown("### 🎯 生成设置")
                        caption_type = gr.Dropdown(
                            choices=list(CAPTION_TYPE_MAP.keys()),
                            value="详细描述",
                            label="📝 描述类型",
                        )
                        
                        caption_length = gr.Dropdown(
                            choices=["any", "very short", "short", "medium-length", "long", "very long"] +
                                    [str(i) for i in range(20, 261, 10)],
                            label="📏 描述长度",
                            value="short",
                        )
                    
                    # 高级选项
                    with gr.Accordion("⚙️ 高级选项", open=False):
                        extra_options = gr.CheckboxGroup(
                            choices=list(EXTRA_OPTIONS_MAP.keys()),
                            label="选择额外选项",
                        )
                        
                        # 额外选项说明
                        gr.HTML("""
                        <div class="info-card" style="margin-top:12px">
                            <p style="margin:0;font-size:0.9rem;color:#64748b">
                                这些复选框用于微调模型应该或不应该提及的内容：照明、相机角度、美学评级、不当内容等。
                                在点击<b>生成描述</b>之前切换它们；提示词框将立即更新。
                            </p>
                        </div>
                        """)
                    
                    # 生成参数
                    with gr.Accordion("🎛️ 生成参数", open=False):
                        temperature_slider = gr.Slider(
                            minimum=0.0, maximum=2.0, value=0.6, step=0.05,
                            label="🌡️ Temperature",
                            info="随机性。0 = 确定性；更高 = 更多变化"
                        )
                        top_p_slider = gr.Slider(
                            minimum=0.0, maximum=1.0, value=0.9, step=0.01,
                            label="🎯 Top-p",
                            info="核采样截止。更低 = 更安全，更高 = 更自由"
                        )
                        max_tokens_slider = gr.Slider(
                            minimum=1, maximum=1024, value=512, step=1,
                            label="📊 最大Token数",
                            info="模型输出长度的硬性停止"
                        )
                
                with gr.Column(scale=1):
                    # 提示词显示
                    prompt_box = gr.Textbox(
                        lines=8,
                        label="📋 发送给API的英文提示词",
                        interactive=True,
                        show_copy_button=True,
                        info="这是实际发送给模型的英文提示词，可以手动编辑"
                    )
                    
                    # 生成按钮
                    generate_btn = gr.Button(
                        "🚀 生成描述",
                        variant="primary",
                        size="lg"
                    )
                    
                    # 输出结果
                    output_caption = gr.Textbox(
                        lines=10,
                        label="📝 生成的描述",
                        show_copy_button=True
                    )
        
        # 批量处理标签页  
        with gr.TabItem("📁 批量处理"):
            # 添加使用说明卡片
            gr.HTML("""
            <div class="info-card">
                <h3>📋 批量处理说明</h3>
                <ul>
                    <li>支持 jpg, jpeg, png, webp 等图片格式</li>
                    <li>所有图片将使用相同的提示词进行处理</li>
                    <li>生成的文本文件将使用原始图片的文件名（扩展名改为.txt）</li>
                    <li>处理完成后可下载包含所有描述的ZIP文件</li>
                </ul>
            </div>
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    # 批量上传
                    batch_images = gr.File(
                        label="📷 批量上传图片",
                        file_count="multiple",
                        file_types=["image"],
                        height=300
                    )
                    
                    # 批量处理设置  
                    with gr.Group():
                        gr.Markdown("### 🎯 批量处理设置")
                        batch_caption_type = gr.Dropdown(
                            choices=list(CAPTION_TYPE_MAP.keys()),
                            value="详细描述",
                            label="📝 描述类型",
                        )
                        
                        batch_caption_length = gr.Dropdown(
                            choices=["any", "very short", "short", "medium-length", "long", "very long"] +
                                    [str(i) for i in range(20, 261, 10)],
                            label="📏 描述长度", 
                            value="short",
                        )
                        
                        with gr.Accordion("⚙️ 高级选项", open=False):
                            batch_extra_options = gr.CheckboxGroup(
                                choices=list(EXTRA_OPTIONS_MAP.keys()),
                                label="额外选项",
                            )
                
                with gr.Column(scale=1):
                    # 批量提示词显示
                    batch_prompt_box = gr.Textbox(
                        lines=8,
                        label="📋 批量处理提示词",
                        interactive=True,
                        show_copy_button=True
                    )
                    
                    # 批量处理按钮
                    batch_generate_btn = gr.Button(
                        "🚀 开始批量处理", 
                        variant="primary",
                        size="lg"
                    )
                    
                    # 处理状态和结果
                    batch_status = gr.Markdown("等待开始处理...")
                    
                    # 下载区域
                    download_file = gr.File(
                        label="📥 下载处理结果",
                        visible=False
                    )
        
        # ⭐ 混合模式批量处理标签页
        with gr.TabItem("🎭 混合模式批量处理"):
            # 添加混合模式说明
            gr.HTML("""
            <div class="info-card">
                <h3>🎭 混合模式说明</h3>
                <ul>
                    <li><b>多样化处理</b>：为每张图片随机选择不同的提示词模板</li>
                    <li><b>权重分配</b>：根据设置的权重比例随机分配提示词</li>
                    <li><b>统计反馈</b>：处理完成后显示各提示词的实际使用情况</li>
                    <li><b>最多支持5个不同的提示词配置</b></li>
                </ul>
                <p><b>💡 提示</b>：权重越高的提示词被选择的概率越大，权重为0的提示词不会被使用</p>
            </div>
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    # 混合模式上传
                    mix_batch_images = gr.File(
                        label="📷 批量上传图片",
                        file_count="multiple",
                        file_types=["image"],
                        height=200
                    )
                    
                with gr.Column(scale=2):
                    # 提示词配置区域  
                    with gr.Group():
                        gr.Markdown("### 🎯 提示词配置")
                        
                        # 提示词1
                        with gr.Group(elem_classes=["prompt-group"]):
                            gr.Markdown("#### 📝 提示词 1")
                            with gr.Row():
                                mix_type_1 = gr.Dropdown(
                                    choices=list(CAPTION_TYPE_MAP.keys()),
                                    value="详细描述",
                                    label="类型",
                                    scale=2
                                )
                                mix_length_1 = gr.Dropdown(
                                    choices=["any", "very short", "short", "medium-length", "long", "very long"],
                                    value="short",
                                    label="长度",
                                    scale=1
                                )
                                mix_weight_1 = gr.Slider(
                                    minimum=0, maximum=10, value=2.0, step=0.1,
                                    label="权重", scale=1
                                )
                            mix_extra_1 = gr.CheckboxGroup(
                                choices=list(EXTRA_OPTIONS_MAP.keys())[:5],
                                label="额外选项", value=[]
                            )
                            mix_prompt_1 = gr.Textbox(
                                lines=2, label="生成的提示词", interactive=True, show_copy_button=True
                            )
                            mix_weight_display_1 = gr.Markdown("**🎯 当前权重**: 2.0", elem_classes=["weight-display"])
                        
                        # 提示词2
                        with gr.Group(elem_classes=["prompt-group"]):
                            gr.Markdown("#### 📝 提示词 2") 
                            with gr.Row():
                                mix_type_2 = gr.Dropdown(
                                    choices=list(CAPTION_TYPE_MAP.keys()),
                                    value="随意描述",
                                    label="类型",
                                    scale=2
                                )
                                mix_length_2 = gr.Dropdown(
                                    choices=["any", "very short", "short", "medium-length", "long", "very long"],
                                    value="short",
                                    label="长度",
                                    scale=1
                                )
                                mix_weight_2 = gr.Slider(
                                    minimum=0, maximum=10, value=1.5, step=0.1,
                                    label="权重", scale=1
                                )
                            mix_extra_2 = gr.CheckboxGroup(
                                choices=list(EXTRA_OPTIONS_MAP.keys())[:5],
                                label="额外选项", value=[]
                            )
                            mix_prompt_2 = gr.Textbox(
                                lines=2, label="生成的提示词", interactive=True, show_copy_button=True
                            )
                            mix_weight_display_2 = gr.Markdown("**🎯 当前权重**: 1.5", elem_classes=["weight-display"])
                        
                        # 提示词3-5（默认折叠）
                        with gr.Accordion("➕ 更多提示词配置 (3-5)", open=False):
                            # 提示词3
                            with gr.Group(elem_classes=["prompt-group"]):
                                gr.Markdown("#### 📝 提示词 3")
                                with gr.Row():
                                    mix_type_3 = gr.Dropdown(
                                        choices=list(CAPTION_TYPE_MAP.keys()),
                                        value="Stable Diffusion提示词",
                                        label="类型",
                                        scale=2
                                    )
                                    mix_length_3 = gr.Dropdown(
                                        choices=["any", "very short", "short", "medium-length", "long", "very long"],
                                        value="short",
                                        label="长度",
                                        scale=1
                                    )
                                    mix_weight_3 = gr.Slider(
                                        minimum=0, maximum=10, value=0, step=0.1,
                                        label="权重", scale=1
                                    )
                                mix_extra_3 = gr.CheckboxGroup(
                                    choices=list(EXTRA_OPTIONS_MAP.keys())[:5],
                                    label="额外选项", value=[]
                                )
                                mix_prompt_3 = gr.Textbox(
                                    lines=2, label="生成的提示词", interactive=True, show_copy_button=True
                                )
                                mix_weight_display_3 = gr.Markdown("**🎯 当前权重**: 0 (未启用)", elem_classes=["weight-display"])
                            
                            # 提示词4
                            with gr.Group(elem_classes=["prompt-group"]):
                                gr.Markdown("#### 📝 提示词 4")
                                with gr.Row():
                                    mix_type_4 = gr.Dropdown(
                                        choices=list(CAPTION_TYPE_MAP.keys()),
                                        value="艺术评论",
                                        label="类型",
                                        scale=2
                                    )
                                    mix_length_4 = gr.Dropdown(
                                        choices=["any", "very short", "short", "medium-length", "long", "very long"],
                                        value="medium-length",
                                        label="长度",
                                        scale=1
                                    )
                                    mix_weight_4 = gr.Slider(
                                        minimum=0, maximum=10, value=0, step=0.1,
                                        label="权重", scale=1
                                    )
                                mix_extra_4 = gr.CheckboxGroup(
                                    choices=list(EXTRA_OPTIONS_MAP.keys())[:5],
                                    label="额外选项", value=[]
                                )
                                mix_prompt_4 = gr.Textbox(
                                    lines=2, label="生成的提示词", interactive=True, show_copy_button=True
                                )
                                mix_weight_display_4 = gr.Markdown("**🎯 当前权重**: 0 (未启用)", elem_classes=["weight-display"])
                            
                            # 提示词5
                            with gr.Group(elem_classes=["prompt-group"]):
                                gr.Markdown("#### 📝 提示词 5")
                                with gr.Row():
                                    mix_type_5 = gr.Dropdown(
                                        choices=list(CAPTION_TYPE_MAP.keys()),
                                        value="社媒文案",
                                        label="类型",
                                        scale=2
                                    )
                                    mix_length_5 = gr.Dropdown(
                                        choices=["any", "very short", "short", "medium-length", "long", "very long"],
                                        value="short",
                                        label="长度",
                                        scale=1
                                    )
                                    mix_weight_5 = gr.Slider(
                                        minimum=0, maximum=10, value=0, step=0.1,
                                        label="权重", scale=1
                                    )
                                mix_extra_5 = gr.CheckboxGroup(
                                    choices=list(EXTRA_OPTIONS_MAP.keys())[:5],
                                    label="额外选项", value=[]
                                )
                                mix_prompt_5 = gr.Textbox(
                                    lines=2, label="生成的提示词", interactive=True, show_copy_button=True
                                )
                                mix_weight_display_5 = gr.Markdown("**🎯 当前权重**: 0 (未启用)", elem_classes=["weight-display"])
                        
                        # 权重统计
                        with gr.Group():
                            total_weight_display = gr.Markdown(
                                "### 📊 权重统计\n**总权重**: 3.5 | **启用的提示词**: 2/5",
                                elem_classes=["info-card"]
                            )
                            
                            mix_generate_btn = gr.Button(
                                "🎲 开始混合模式处理",
                                variant="primary",
                                size="lg"
                            )
            
            # 混合模式处理状态和结果
            mix_batch_status = gr.Markdown("等待开始处理...")
            
            # 混合模式下载区域
            mix_download_file = gr.File(
                label="📥 下载混合模式处理结果",
                visible=False
            )
    
    # 添加Caption类型参考表格
    with gr.Accordion("📚 Caption类型参考", open=False):
        gr.HTML(CAPTION_TYPE_TABLE)
    
    # 权重显示更新函数
    def update_weight_display(w):
        if w <= 0:
            return f"**🎯 当前权重**: {w} (未启用)"
        else:
            return f"**🎯 当前权重**: {w}"
    
    def update_total_weight(w1, w2, w3, w4, w5):
        total = w1 + w2 + w3 + w4 + w5
        active_count = sum(1 for w in [w1, w2, w3, w4, w5] if w > 0)
        return f"### 📊 权重统计\n**总权重**: {total:.1f} | **启用的提示词**: {active_count}/5"
    
    # 事件绑定
    test_btn.click(
        test_api_connection,
        inputs=[api_base_url, api_key],
        outputs=connection_status
    ).then(
        lambda success_msg: f'<div class="status-box status-{"success" if "✅" in success_msg else "error"}">{success_msg}</div>',
        inputs=[connection_status],
        outputs=[connection_status]
    )
    
    # 单图处理 - 自动更新提示词
    for ctrl in (caption_type, caption_length, extra_options):
        ctrl.change(
            build_prompt,
            inputs=[caption_type, caption_length, extra_options],
            outputs=prompt_box,
        )
    
    # 批量处理 - 自动更新提示词
    for ctrl in (batch_caption_type, batch_caption_length, batch_extra_options):
        ctrl.change(
            build_prompt,
            inputs=[batch_caption_type, batch_caption_length, batch_extra_options],
            outputs=batch_prompt_box,
        )
    
    # 混合模式 - 自动更新提示词和权重显示
    mix_components = [
        (mix_type_1, mix_length_1, mix_extra_1, mix_prompt_1, mix_weight_1, mix_weight_display_1),
        (mix_type_2, mix_length_2, mix_extra_2, mix_prompt_2, mix_weight_2, mix_weight_display_2), 
        (mix_type_3, mix_length_3, mix_extra_3, mix_prompt_3, mix_weight_3, mix_weight_display_3),
        (mix_type_4, mix_length_4, mix_extra_4, mix_prompt_4, mix_weight_4, mix_weight_display_4),
        (mix_type_5, mix_length_5, mix_extra_5, mix_prompt_5, mix_weight_5, mix_weight_display_5),
    ]
    
    for mix_type, mix_length, mix_extra, mix_prompt, mix_weight, mix_weight_display in mix_components:
        # 更新提示词
        for ctrl in (mix_type, mix_length, mix_extra):
            ctrl.change(
                build_prompt,
                inputs=[mix_type, mix_length, mix_extra],
                outputs=[mix_prompt],
            )
        
        # 更新权重显示
        mix_weight.change(
            update_weight_display,
            inputs=[mix_weight],
            outputs=[mix_weight_display]
        )
    
    # 更新总权重显示
    all_weights = [mix_weight_1, mix_weight_2, mix_weight_3, mix_weight_4, mix_weight_5]
    for weight in all_weights:
        weight.change(
            update_total_weight,
            inputs=all_weights,
            outputs=[total_weight_display]
        )
    
    # 单图生成描述
    generate_btn.click(
        generate_caption,
        inputs=[
            input_image,
            prompt_box,
            api_base_url,
            api_key,
            temperature_slider,
            top_p_slider,
            max_tokens_slider
        ],
        outputs=output_caption,
    )
    
    # 批量处理
    def process_batch_wrapper(files, prompt, base_url, api_key, temp, top_p, max_tokens):
        """包装批量处理函数以处理文件输入"""
        if not files:
            return "❌ 请先上传图片", gr.update(visible=False)
        
        files_info = []
        for file in files:
            try:
                # 获取原始文件名
                original_filename = os.path.basename(file.name)
                image = Image.open(file.name)
                files_info.append((image, original_filename))
            except Exception as e:
                logging.error(f"无法打开图片 {file.name}: {str(e)}")
                continue
        
        if not files_info:
            return "❌ 没有有效的图片", gr.update(visible=False)
        
        status, zip_path = process_batch_images(
            files_info, prompt, base_url, api_key, temp, top_p, max_tokens
        )
        
        if zip_path:
            return status, gr.update(value=zip_path, visible=True)
        else:
            return status, gr.update(visible=False)
    
    batch_generate_btn.click(
        process_batch_wrapper,
        inputs=[
            batch_images,
            batch_prompt_box,
            api_base_url, 
            api_key,
            temperature_slider,
            top_p_slider,
            max_tokens_slider
        ],
        outputs=[batch_status, download_file],
    )
    
    def process_mix_batch_wrapper(files, base_url, api_key, temp, top_p, max_tokens,
                                t1, l1, w1, e1, t2, l2, w2, e2, t3, l3, w3, e3, t4, l4, w4, e4, t5, l5, w5, e5):
        """优化的混合模式批量处理函数"""
        if not files:
            return "❌ 请先上传图片", gr.update(visible=False)
        
        # 🚀 限制单次上传数量
        if len(files) > 5000:
            return f"❌ 单次最多支持5000张图片，您上传了{len(files)}张，请分批处理", gr.update(visible=False)
        
        # 构建提示词配置
        prompt_configs = []
        configs_data = [
            (t1, l1, w1, e1), (t2, l2, w2, e2), (t3, l3, w3, e3), (t4, l4, w4, e4), (t5, l5, w5, e5)
        ]
        
        for i, (prompt_type, prompt_length, weight, extra_options) in enumerate(configs_data):
            if weight > 0:
                prompt = build_prompt(prompt_type, prompt_length, extra_options)
                prompt_configs.append({
                    'prompt': prompt,
                    'weight': weight,
                    'type': prompt_type,
                    'index': i + 1
                })
        
        if not prompt_configs:
            return "❌ 请至少设置一个权重大于0的提示词", gr.update(visible=False)
        
        # 📦 分批加载图片
        processor = BatchFileProcessor(batch_size=50)
        file_batches = processor.create_batches(files)
        
        all_files_info = []
        failed_files = []
        
        for batch_idx, file_batch in enumerate(file_batches):
            for file in file_batch:
                try:
                    original_filename = os.path.basename(file.name)
                    image = Image.open(file.name)
                    # 🔧 调整图片大小
                    if max(image.size) > 1024:
                        image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                    all_files_info.append((image, original_filename))
                except Exception as e:
                    failed_files.append(f"{os.path.basename(file.name)}: {str(e)}")
                    continue
        
        if not all_files_info:
            error_msg = "❌ 没有有效的图片\n" + "\n".join(failed_files[:10])
            return error_msg, gr.update(visible=False)
        
        # 处理图片
        status, zip_path = process_mix_batch_images(
            all_files_info, prompt_configs, base_url, api_key, temp, top_p, max_tokens
        )
        
        if zip_path:
            return status, gr.update(value=zip_path, visible=True)
        else:
            return status, gr.update(visible=False)
    
    mix_generate_btn.click(
        process_mix_batch_wrapper,
        inputs=[
            mix_batch_images, api_base_url, api_key, temperature_slider, top_p_slider, max_tokens_slider,
            mix_type_1, mix_length_1, mix_weight_1, mix_extra_1,
            mix_type_2, mix_length_2, mix_weight_2, mix_extra_2,
            mix_type_3, mix_length_3, mix_weight_3, mix_extra_3,
            mix_type_4, mix_length_4, mix_weight_4, mix_extra_4,
            mix_type_5, mix_length_5, mix_weight_5, mix_extra_5,
        ],
        outputs=[mix_batch_status, mix_download_file],
    )
    
    # 初始化提示词
    demo.load(
        build_prompt,
        inputs=[caption_type, caption_length, extra_options],
        outputs=prompt_box,
    )
    demo.load(
        build_prompt,
        inputs=[batch_caption_type, batch_caption_length, batch_extra_options],
        outputs=batch_prompt_box,
    )
    
    # 初始化混合模式提示词
    for mix_type, mix_length, mix_extra, mix_prompt, _, _ in mix_components:
        demo.load(
            build_prompt,
            inputs=[mix_type, mix_length, mix_extra],
            outputs=[mix_prompt],
        )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="JoyCaption 混合模式 API Demo")
    parser.add_argument("--port", type=int, default=7860, help="服务端口")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="服务主机")
    parser.add_argument("--share", action="store_true", help="创建公共链接")
    
    args = parser.parse_args()
    
    print(f"🚀 启动JoyCaption 混合模式 API Demo...")
    print(f"🌐 访问地址: http://{args.host}:{args.port}")
    
    demo.launch(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        show_error=True
    )
