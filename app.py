import gradio as gr
import base64
import io
from PIL import Image
from typing import Generator, List
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

# 配置日志
logging.basicConfig(level=logging.INFO)

# 常量定义
LOGO_SRC = """data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjwhRE9DVFlQRSBzdmcgUFVCTElDICItLy9XM0MvL0RURCBTVkcgMS4xLy9FTiIgImh0dHA6Ly93d3cudzMub3JnL0dyYXBoaWNzL1NWRy8xLjEvRFREL3N2ZzExLmR0ZCI+Cjxzdmcgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgdmlld0JveD0iMCAwIDUzOCA1MzUiIHZlcnNpb249IjEuMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayIgeG1sOnNwYWNlPSJwcmVzZXJ2ZSIgeG1sbnM6c2VyaWY9Imh0dHA6Ly93d3cuc2VyaWYuY29tLyIgc3R5bGU9ImZpbGwtcnVsZTpldmVub2RkO2NsaXAtcnVsZTpldmVub2RkO3N0cm9rZS1saW5lam9pbjpyb3VuZDtzdHJva2UtbWl0ZXJsaW1pdDoyOyI+CiAgICA8ZyB0cmFuc2Zvcm09Im1hdHJpeCgxLDAsMCwxLC0xNDcuODcxLDAuMDAxOTA4NjMpIj4KICAgICAgICA8cGF0aCBkPSJNMTk1LjY3LDIyMS42N0MxOTYuNzMsMjA1LjM3IDIwMC4yOCwxODkuNzYgMjA3LjkxLDE3NS4zN0MyMjcuOTgsMTM3LjUxIDI1OS4zMywxMTQuODggMzAyLjAxLDExMS42M0MzMzQuMTUsMTA5LjE4IDM2Ni41OSwxMTAuNiAzOTguODksMTEwLjNDNDAwLjUzLDExMC4yOCA0MDIuMTYsMTEwLjMgNDA0LjQsMTEwLjNDNDA0LjQsMTAxLjk5IDQwNC41Niw5NC4wNSA0MDQuMjMsODYuMTJDNDA0LjE4LDg0Ljg0IDQwMi4xNSw4My4xMyA0MDAuNjYsODIuNDlDMzgzLjIzLDc1LjAyIDM3My4wNSw1OS43OSAzNzMuOTYsNDAuOTZDMzc1LjA5LDE3LjU0IDM5MS40NywyLjY2IDQxMC42NSwwLjM3QzQzNy44OSwtMi44OSA0NTUuNTYsMTUuODQgNDU5LjI2LDM0LjY5QzQ2Mi45Niw1My41NyA0NTIuMTgsNzYuOTMgNDMyLjgxLDgyLjY2QzQzMS42NCw4My4wMSA0MzAuMzMsODUuMjMgNDMwLjI4LDg2LjYyQzQzMC4wMyw5NC4yNiA0MzAuMTYsMTAxLjkyIDQzMC4xNiwxMTAuM0w0MzUuNjMsMTEwLjNDNDYzLjc5LDExMC4zIDQ5MS45NiwxMTAuMjggNTIwLjEyLDExMC4zQzU3NC44NCwxMTAuMzYgNjIzLjA0LDE0OC4zNSA2MzUuNjcsMjAxLjU1QzYzNy4yMywyMDguMTMgNjM3LjgzLDIxNC45MyA2MzguODksMjIxLjY3QzY2MC40MywyMjQuOTQgNjc1LjE5LDIzNi42MiA2ODIuMzYsMjU3LjRDNjgzLjU5LDI2MC45NyA2ODQuNjUsMjY0LjgyIDY4NC42NywyNjguNTRDNjg0Ljc3LDI4My4zNCA2ODUuNzYsMjk4LjMxIDY4My45NCwzMTIuOTFDNjgwLjg5LDMzNy4yOSA2NjIuODYsMzUzLjM2IDYzOC40NywzNTUuODJDNjM1LjE0LDM4NS4wOCA2MjEuOTEsNDA5LjQxIDYwMC40NSw0MjkuMjFDNTgxLjYsNDQ2LjYxIDU1OS4xNCw0NTcuNSA1MzMuNTcsNDU5LjE4QzUwOC4xOCw0NjAuODQgNDgyLjY0LDQ2MC4yIDQ1Ny4xNiw0NjAuMzhDNDM1LjE2LDQ2MC41MyA0MTMuMTcsNDYwLjM0IDM5MS4xNyw0NjAuNTNDMzg4Ljc2LDQ2MC41NSAzODUuOTUsNDYxLjU2IDM4NC4wMyw0NjMuMDRDMzcxLjU0LDQ3Mi42MiAzNTkuMTMsNDgyLjMxIDM0Ni45Miw0OTIuMjVDMzM4Ljk0LDQ5OC43NSAzMzEuMzksNTA1Ljc3IDMyMy41Niw1MTIuNDZDMzE3LjQ1LDUxNy42OCAzMTAuOTMsNTIyLjQ0IDMwNS4xMSw1MjcuOTVDMzAxLjE5LDUzMS42NiAyOTYuNTIsNTMzLjE3IDI5MS42OSw1MzQuMzZDMjg1LjY1LDUzNS44NSAyNzkuMjIsNTI5LjEzIDI3OS4wMSw1MjEuMTlDMjc4LjgsNTEyLjg2IDI3OC45NSw1MDQuNTMgMjc4Ljk0LDQ5Ni4xOUwyNzguOTQsNDU2LjY5QzIzMi44Miw0MzguMTYgMjAzLjU2LDQwNi4yMyAxOTUuMDcsMzU2LjA4QzE5My4yNiwzNTUuNzUgMTkwLjg0LDM1NS40MSAxODguNDgsMzU0Ljg2QzE2Ny40NiwzNDkuOTEgMTU1LjA0LDMzNi4wMiAxNTAuNzIsMzE1LjYyQzE0Ni45OCwyOTcuOTkgMTQ2LjksMjc5LjY3IDE1MC42MSwyNjIuMDlDMTU1LjU1LDIzOC42OCAxNzEuNDIsMjI1LjU5IDE5NS42NiwyMjEuNjdMMTk1LjY3LDIyMS42N1pNMzA4LjA3LDQ4Ny44MkMzMTUuOTQsNDgxLjEzIDMyMi44NSw0NzUuMTMgMzI5LjksNDY5LjNDMzQ0LjM5LDQ1Ny4zMSAzNTguOSw0NDUuMzYgMzczLjU0LDQzMy41NkMzNzUuMTcsNDMyLjI1IDM3Ny42OCw0MzEuNCAzNzkuNzksNDMxLjM5QzQxNC43OCw0MzEuMjYgNDQ5Ljc4LDQzMS4zOCA0ODQuNzcsNDMxLjI0QzUwMC4zOSw0MzEuMTggNTE2LjEzLDQzMS43NiA1MzEuNjIsNDMwLjE2QzU3Ni45Miw0MjUuNDkgNjA5LjI0LDM4Ny43NyA2MDguOTUsMzQ0Ljg0QzYwOC42OCwzMDUuNTIgNjA4LjkzLDI2Ni4xOSA2MDguODcsMjI2Ljg2QzYwOC44NywyMjMuMjIgNjA4LjU4LDIxOS41NSA2MDcuOTksMjE1Ljk2QzYwMy4xMSwxODYuMjkgNTg4LjYxLDE2My4zMyA1NjEuMzIsMTQ5LjMyQzU0OS4wNCwxNDMuMDIgNTM2LjE1LDEzOS4yOSA1MjIuMjIsMTM5LjI5QzQ1My45LDEzOS4zMiAzODUuNTgsMTM5LjIgMzE3LjI2LDEzOS4zNUMzMDkuMiwxMzkuMzcgMzAwLjk2LDEzOS44OSAyOTMuMTEsMTQxLjZDMjU0LjE5LDE1MC4wNyAyMjUuMzMsMTg1LjY5IDIyNS4wMywyMjUuNDJDMjI0LjgsMjU2LjA4IDIyNC44NiwyODYuNzQgMjI0Ljk5LDMxNy40QzIyNS4wNSwzMzAuNTMgMjI0Ljc0LDM0My43NiAyMjYuMTgsMzU2Ljc3QzIyOC43NCwzODAuMDUgMjQwLjYsMzk4LjYyIDI1OC43OSw0MTIuOTNDMjczLjA0LDQyNC4xNCAyODkuNjMsNDMwLjAyIDMwNy42MSw0MzEuNTVDMzA3LjgyLDQzMi4wMyAzMDguMDYsNDMyLjMzIDMwOC4wNiw0MzIuNjNDMzA4LjA4LDQ1MC42IDMwOC4wOCw0NjguNTcgMzA4LjA4LDQ4Ny44MUwzMDguMDcsNDg3LjgyWk00MzUuNzksNDMuMzNDNDM1Ljk1LDMzLjQyIDQyNy42MSwyNC42NSA0MTcuOCwyNC40QzQwNi43NiwyNC4xMiAzOTguMjUsMzIuMDUgMzk4LjEzLDQyLjc0QzM5OC4wMSw1My4wNCA0MDYuNiw2Mi4xMiA0MTYuNDIsNjIuMDhDNDI3LjExLDYyLjA0IDQzNS42MSw1My44MSA0MzUuNzgsNDMuMzNMNDM1Ljc5LDQzLjMzWiIgc3R5bGU9ImZpbGw6cmdiKDczLDQ3LDExOCk7ZmlsbC1ydWxlOm5vbnplcm87Ii8+CiAgICAgICAgPHBhdGggZD0iTTQxOS4zLDM5MS42M0MzNzQuNDYsMzkwLjQgMzQxLjUxLDM3Mi42MyAzMTguMDEsMzM3LjcxQzMxNS42NywzMzQuMjMgMzEzLjc3LDMzMC4wNCAzMTMuMSwzMjUuOTVDMzExLjg0LDMxOC4yOCAzMTYuNTMsMzExLjcgMzIzLjcyLDMwOS40NkMzMzAuNjYsMzA3LjI5IDMzOC4zMiwzMTAuMSAzNDEuOTgsMzE3LjAzQzM0OS4xNSwzMzAuNjMgMzU5LjE2LDM0MS4zNSAzNzIuMywzNDkuMzFDNDAxLjMyLDM2Ni44OSA0NDQuNTYsMzYzLjcgNDcwLjYxLDM0Mi4zNUM0NzkuMSwzMzUuMzkgNDg2LjA4LDMyNy40MSA0OTEuNTUsMzE3Ljk3QzQ5NS4wNSwzMTEuOTMgNTAwLjIsMzA4LjE4IDUwNy40NywzMDguOTVDNTEzLjczLDMwOS42MSA1MTguODYsMzEyLjg4IDUyMC4xMiwzMTkuMjFDNTIwLjksMzIzLjEzIDUyMC43MywzMjguMjIgNTE4LjgzLDMzMS41NUM1MDAuNjMsMzYzLjMyIDQ3My41NSwzODIuOTUgNDM3LjI5LDM4OS4zN0M0MzAuNDQsMzkwLjU4IDQyMy40OCwzOTEuMTIgNDE5LjI5LDM5MS42M0w0MTkuMywzOTEuNjNaIiBzdHlsZT0iZmlsbDpyZ2IoMjUwLDEzOSwxKTtmaWxsLXJ1bGU6bm9uemVybzsiLz4KICAgICAgICA8cGF0aCBkPSJNNDYyLjcxLDI0MC4xOUM0NjIuOCwyMTYuOTEgNDgwLjI0LDE5OS43OSA1MDQuMDEsMTk5LjY3QzUyNi41NywxOTkuNTUgNTQ0Ljg5LDIxOC4wNyA1NDQuNTEsMjQxLjM0QzU0NC4xOCwyNjEuODUgNTMwLjA5LDI4MS45NiA1MDEuOTEsMjgxLjIzQzQ4MC42OCwyODAuNjggNDYyLjE1LDI2My44IDQ2Mi43MSwyNDAuMkw0NjIuNzEsMjQwLjE5WiIgc3R5bGU9ImZpbGw6cmdiKDI1MCwxMzksMSk7ZmlsbC1ydWxlOm5vbnplcm87Ii8+CiAgICAgICAgPHBhdGggZD0iTTM3MC45OSwyNDAuMDhDMzcxLDI2Mi43OSAzNTIuNTMsMjgxLjM1IDMyOS44OSwyODEuMzdDMzA3LjA1LDI4MS40IDI4OC45NiwyNjMuNDIgMjg4Ljk2LDI0MC42OEMyODguOTYsMjE4LjE0IDMwNi43MywyMDAgMzI5LjE2LDE5OS42MkMzNTIuMDIsMTk5LjI0IDM3MC45OCwyMTcuNTcgMzcwLjk5LDI0MC4wOFoiIHN0eWxlPSJmaWxsOnJnYigyNTAsMTM5LDEpO2ZpbGwtcnVsZTpub256ZXJvOyIvPgogICAgPC9nPgo8L3N2Zz4K"""


# 修改标题样式，使其更现代
TITLE = f"""<style>
  .joy-header {{
    display: flex; 
    align-items: center; 
    justify-content: center;
    gap: 20px; 
    margin: 8px 0 16px;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    color: white;
  }}
  .joy-header h1 {{
    margin: 0; 
    font-size: 2.2rem; 
    line-height: 1.2;
    font-weight: 700;
  }}
  .joy-header p {{
    margin: 4px 0 0; 
    font-size: 1rem; 
    opacity: 0.9;
  }}
  .joy-header img {{
    height: 64px;
    filter: brightness(0) invert(1);
  }}
  .status-box {{
    padding: 10px;
    border-radius: 8px;
    margin: 10px 0;
    text-align: center;
    font-weight: 500;
  }}
  .status-success {{
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
  }}
  .status-error {{
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
  }}
  .status-info {{
    background-color: #cce5ff;
    color: #004085;
    border: 1px solid #b3d7ff;
  }}
  .progress-bar {{
    width: 100%;
    height: 20px;
    background-color: #f0f0f0;
    border-radius: 10px;
    overflow: hidden;
    margin: 10px 0;
  }}
  .progress-fill {{
    height: 100%;
    background: linear-gradient(90deg, #4CAF50, #45a049);
    transition: width 0.3s ease;
  }}
</style>
<div class="joy-header">
  <img src="{LOGO_SRC}" alt="JoyCaption logo">
  <div>
    <h1>🎨 JoyCaption <span style="font-weight:400">API版本</span></h1>
    <p>智能图像描述生成器 | API调用版本 | 支持批量处理</p>
  </div>
</div>"""

# 简化的描述文本
DESCRIPTION = """
## 📖 使用指南

### 🔥 单图处理
1. **🔧 配置API**: 设置API服务器地址和密钥
2. **📷 上传图片**: 拖拽或点击上传要分析的图像  
3. **🎯 选择模式**: 选择合适的描述类型和长度
4. **🚀 开始生成**: 点击"生成描述"按钮

### ⚡ 批量处理
1. **📁 上传多图**: 在批量处理标签页中上传多张图片
2. **⚙️ 配置参数**: 设置相同的描述类型和长度
3. **🚀 批量处理**: 点击"开始批量处理"按钮  
4. **📥 下载结果**: 处理完成后下载包含所有描述文件的ZIP包

**📝 文件命名**: 生成的文本文件将使用原始图片的文件名（扩展名改为.txt）

### 🎨 描述模式
- **📝 详细描述**: 正式、详细的散文描述
- **💬 随意描述**: 友好、对话式的描述风格  
- **📊 直接描述**: 客观、简洁的要点描述
- **🎭 艺术评论**: 艺术史风格的专业分析
- **🛍️ 产品文案**: 营销风格的产品描述
- **📱 社媒文案**: 适合社交媒体的吸引人文案
- **🎯 Stable Diffusion提示词**: 生成SD风格的提示词
- **🎪 MidJourney提示词**: 生成MJ风格的提示词
"""

# 保持英文的提示词模板
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
    """批量处理图片
    
    Args:
        files_info: List of (image, original_filename) tuples
    """
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
                    
                    # **修复：使用原始文件名**
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

### 🔧 使用的配置
- **API地址**: {base_url}
- **处理参数**: Temperature={temperature}, Top-p={top_p}, Max-tokens={max_tokens}
        """
        
        return summary, zip_path
        
    except Exception as e:
        logging.error(f"批量处理时出错: {str(e)}")
        return f"❌ 批量处理失败: {str(e)}", None


# 创建Gradio界面
with gr.Blocks(theme=gr.themes.Soft(), title="🎨 JoyCaption API") as demo:
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
                test_btn = gr.Button("🔍 测试连接", variant="secondary")
        
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
                            label="选择一个或多个选项",
                        )
                    
                    # 生成参数
                    with gr.Accordion("🎛️ 生成参数", open=False):
                        temperature_slider = gr.Slider(
                            minimum=0.0, maximum=2.0, value=0.9, step=0.05,
                            label="🌡️ Temperature",
                            info="数值越高生成越随机"
                        )
                        top_p_slider = gr.Slider(
                            minimum=0.0, maximum=1.0, value=0.7, step=0.01,
                            label="🎯 Top-p"
                        )
                        max_tokens_slider = gr.Slider(
                            minimum=1, maximum=512, value=256, step=1,
                            label="📊 最大Token数"
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
            with gr.Row():
                with gr.Column(scale=1):
                    # 批量上传
                    batch_images = gr.File(
                        label="📷 批量上传图片",
                        file_count="multiple",
                        file_types=["image"],
                        height=300
                    )
                    
                    gr.Markdown("""
                    ### 📋 使用说明
                    1. **选择多张图片**: 支持jpg, jpeg, png, webp等格式
                    2. **配置参数**: 使用上方的API配置和下方的处理参数
                    3. **开始处理**: 点击"开始批量处理"按钮
                    4. **下载结果**: 处理完成后下载ZIP文件
                    
                    ⚠️ **注意**: 批量处理会使用相同的提示词处理所有图片
                    💡 **文件命名**: 文本文件将使用原始图片的文件名（扩展名改为.txt）
                    """)
                    
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
                        
                        batch_extra_options = gr.CheckboxGroup(
                            choices=list(EXTRA_OPTIONS_MAP.keys()),
                            label="高级选项",
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
    
    gr.Markdown(DESCRIPTION)
    
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


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="JoyCaption API Demo")
    parser.add_argument("--port", type=int, default=7860, help="服务端口")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="服务主机")
    parser.add_argument("--share", action="store_true", help="创建公共链接")
    
    args = parser.parse_args()
    
    print(f"🚀 启动JoyCaption API Demo...")
    print(f"🌐 访问地址: http://{args.host}:{args.port}")
    
    demo.launch(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        show_error=True
    )
