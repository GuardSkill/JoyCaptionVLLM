# JoyCaption VLLM API 工具集

[English](#english) | [中文](#chinese)

---

## <a id="chinese">🎨 JoyCaption VLLM API 工具集</a>

基于 VLLM 的 JoyCaption 模型 API 服务和客户端工具集，提供图像描述生成、标签提取等功能。

![](./test_imgs/example.png)
### 📋 目录

- [功能特性](#功能特性)
- [环境要求](#环境要求)
- [安装部署](#安装部署)
- [使用教程](#使用教程)
  - [1. 启动模型服务](#1-启动模型服务)
  - [2. 可视化Web界面](#2-可视化web界面)
  - [3. 命令行批量处理](#3-命令行批量处理)
  - [4. 代码调用示例](#4-代码调用示例)
- [配置说明](#配置说明)
- [注意事项](#注意事项)

### 🎯 功能特性

- **🖼️ 智能图像描述**：支持多种描述风格（详细、随意、直接等）
- **🏷️ 图像标签生成**：生成 Booru 风格标签
- **🎭 混合模式处理**：支持多个提示词模板随机组合
- **📁 批量处理**：支持大批量图像文件处理
- **🌐 Web界面**：友好的可视化操作界面
- **🔧 API调用**：基于 OpenAI 兼容的 API 接口
- **⚡ 高性能**：基于 VLLM 引擎，支持 GPU 加速

### 💻 环境要求

- **系统**：Linux / Windows / macOS
- **Python**：>= 3.8
- **GPU**：NVIDIA GPU（推荐显存 >= 8GB）
- **CUDA**：>= 11.8
- **依赖**：
  - vllm
  - gradio
  - openai
  - PIL/Pillow
  - requests

### 🚀 安装部署

#### 1. 克隆项目
```bash
git clone https://github.com/GuardSkill/JoyCaptionVLLM.git
cd JoyCaptionVLLM
```

#### 2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或者
venv\Scripts\activate     # Windows
```

#### 3. 安装依赖
```bash
pip install vllm gradio openai pillow requests
```

#### 4. 下载模型
```bash
# 使用 Hugging Face Hub
pip install huggingface_hub
huggingface-cli download fancyfeast/llama-joycaption-beta-one-hf-llava --local-dir ./llama-joycaption-beta-one-hf-llava

# 或者使用 git lfs
git lfs install
git clone https://huggingface.co/fancyfeast/llama-joycaption-beta-one-hf-llava ./llama-joycaption-beta-one-hf-llava
```

### 📖 使用教程

#### 1. 启动模型服务

使用提供的启动脚本：

```bash
chmod +x start_command.sh
./start_command.sh
```

或者手动启动：

```bash
CUDA_VISIBLE_DEVICES=0 vllm serve llama-joycaption-beta-one-hf-llava \
    --max-model-len 4096 \
    --enable-prefix-caching \
    --port 8000
```

**参数说明**：
- `CUDA_VISIBLE_DEVICES=0`：指定使用的 GPU 编号
- `--max-model-len 4096`：最大序列长度
- `--enable-prefix-caching`：启用前缀缓存（提升性能）
- `--port 8000`：API 服务端口

服务启动成功后，API 将在 `http://localhost:8000` 可用。

#### 2. 可视化Web界面

启动 Gradio Web 界面：

```bash
python app.py --port 8888 --host 0.0.0.0      # 新版界面和新版的VLLM默认参数
```

**功能模块**：

##### 🔧 API 配置
1. **API地址**：输入模型服务地址（如：`http://192.168.5.212:8000/v1`）
2. **API密钥**：输入 API 密钥（可使用任意字符串）
3. **测试连接**：点击测试按钮验证连接

##### 🖼️ 单图处理
1. 上传图片文件
2. 选择描述类型：
   - **详细描述**：正式、详细的散文描述
   - **随意描述**：友好、对话式的描述风格
   - **直接描述**：客观、简洁的要点描述
   - **Stable Diffusion提示词**：生成 SD 风格的提示词
   - **MidJourney提示词**：生成 MJ 风格的提示词
   - **艺术评论**：艺术史风格的专业分析
   - **产品文案**：营销风格的产品描述
   - **社媒文案**：适合社交媒体的吸引人文案
3. 设置描述长度
4. 配置高级选项（可选）
5. 点击"生成描述"

##### 📁 批量处理
1. 上传多张图片
2. 配置相同的处理参数
3. 点击"开始批量处理"
4. 下载包含所有结果的 ZIP 文件

##### 🎭 混合模式批量处理
1. 上传多张图片
2. 配置多个不同的提示词模板
3. 为每个提示词设置权重
4. 系统根据权重随机分配提示词
5. 查看处理统计和下载结果

#### 3. 命令行批量处理

使用 `image_captioning.py` 进行批量处理：

##### 基础用法

```bash
# 生成标签模式
python image_captioning.py --input "/path/to/images" --mode tag

# 生成描述模式
python image_captioning.py --input "/path/to/images" --mode des

# 自定义提示词模式
python image_captioning.py \
    --input "/path/to/images" \
    --mode custom \
    --custom_prompt "Write a detailed analysis of this image."
```

##### 完整参数

```bash
python image_captioning.py \
    --input "/path/to/images" \          # 输入文件夹路径（必需）
    --output "/path/to/output" \         # 输出文件夹路径（可选，默认为输入路径）
    --api_key "your-api-key" \           # API 密钥（可选）
    --base_url "http://ip:8000/v1" \     # API 基础地址（可选）
    --mode tag \                         # 处理模式（必需）
    --custom_prompt "prompt" \           # 自定义提示词（仅 custom 模式）
    --max_retries 3                      # 最大重试次数（可选）
```

**支持的图像格式**：`.png`, `.jpg`, `.jpeg`, `.bmp`, `.gif`, `.webp`

### ⚙️ 配置说明

#### 模型服务配置

编辑 `start_command.sh` 自定义启动参数：

```bash
#!/bin/bash
CUDA_VISIBLE_DEVICES=0 vllm serve llama-joycaption-beta-one-hf-llava \
    --max-model-len 4096 \           # 最大序列长度
    --enable-prefix-caching \        # 启用前缀缓存
    --port 8000 \                    # API 端口
    --host 0.0.0.0 \                # 监听地址
    --tensor-parallel-size 1 \       # 张量并行大小（多GPU时使用）
    --gpu-memory-utilization 0.9     # GPU 内存使用率
```

#### Web 界面配置

在 `app_mix.py` 中修改默认配置：

```python
# 默认 API 配置
DEFAULT_API_URL = "http://192.168.5.212:8000/v1"
DEFAULT_API_KEY = "your-api-key"

# 启动参数
demo.launch(
    server_name="0.0.0.0",    # 监听地址
    server_port=7860,         # Web 界面端口
    share=False,              # 是否创建公网链接
    show_error=True           # 显示错误信息
)
```

### ⚠️ 注意事项

1. **GPU 内存**：模型需要约 8GB 显存，确保 GPU 资源充足
2. **网络配置**：如需从其他机器访问，请确保防火墙允许相应端口
3. **文件权限**：确保程序对输入/输出文件夹有读写权限
4. **批量处理**：大批量处理时建议分批进行，避免内存溢出
5. **API 限制**：注意 API 的并发限制和超时设置
6. **模型更新**：定期检查模型更新，获取最新功能

### 🐛 故障排查

#### 常见问题

1. **模型加载失败**
   ```bash
   # 检查模型文件是否完整
   ls -la ./llama-joycaption-beta-one-hf-llava
   
   # 重新下载模型
   rm -rf ./llama-joycaption-beta-one-hf-llava
   huggingface-cli download fancyfeast/llama-joycaption-beta-one-hf-llava --local-dir ./llama-joycaption-beta-one-hf-llava
   ```

2. **GPU 内存不足**
   ```bash
   # 减少最大序列长度
   vllm serve llama-joycaption-beta-one-hf-llava --max-model-len 2048
   
   # 或调整 GPU 内存使用率
   vllm serve llama-joycaption-beta-one-hf-llava --gpu-memory-utilization 0.8
   ```

3. **API 连接失败**
   - 检查模型服务是否正常启动
   - 确认 IP 地址和端口配置正确
   - 验证防火墙设置

4. **批量处理ZIP文件为空**
   - 检查 `app.py` 中的文件写入代码是否被注释
   - 确保输出目录有写入权限

---

## <a id="english">🎨 JoyCaption VLLM API Toolkit</a>

A comprehensive toolkit for JoyCaption model API service based on VLLM, providing image captioning, tag extraction, and other AI-powered image analysis features.

### 📋 Table of Contents

- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
  - [1. Start Model Service](#1-start-model-service)
  - [2. Visual Web Interface](#2-visual-web-interface)
  - [3. Command Line Batch Processing](#3-command-line-batch-processing)
  - [4. Code Examples](#4-code-examples)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

### 🎯 Features

- **🖼️ Intelligent Image Captioning**: Multiple caption styles (detailed, casual, formal, etc.)
- **🏷️ Image Tag Generation**: Booru-style tag generation
- **🎭 Mixed Mode Processing**: Random combination of multiple prompt templates
- **📁 Batch Processing**: Support for large-scale image processing
- **🌐 Web Interface**: User-friendly visual interface
- **🔧 API Integration**: OpenAI-compatible API interface
- **⚡ High Performance**: VLLM-powered with GPU acceleration

### 💻 System Requirements

- **OS**: Linux / Windows / macOS
- **Python**: >= 3.8
- **GPU**: NVIDIA GPU (recommended VRAM >= 8GB)
- **CUDA**: >= 11.8
- **Dependencies**:
  - vllm
  - gradio
  - openai
  - PIL/Pillow
  - requests

### 🚀 Installation

#### 1. Clone Repository
```bash
git clone https://github.com/GuardSkill/JoyCaptionVLLM.git
cd joycaptionVLLM
```

#### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

#### 3. Install Dependencies
```bash
pip install vllm gradio openai pillow requests
```

#### 4. Download Model
```bash
# Using Hugging Face Hub
pip install huggingface_hub
huggingface-cli download fancyfeast/llama-joycaption-beta-one-hf-llava --local-dir ./llama-joycaption-beta-one-hf-llava

# Or using git lfs
git lfs install
git clone https://huggingface.co/fancyfeast/llama-joycaption-beta-one-hf-llava ./llama-joycaption-beta-one-hf-llava
```

### 📖 Usage Guide

#### 1. Start Model Service

Using the provided startup script:

```bash
chmod +x start_command.sh
./start_command.sh
```

Or start manually:

```bash
CUDA_VISIBLE_DEVICES=0 vllm serve llama-joycaption-beta-one-hf-llava \
    --max-model-len 4096 \
    --enable-prefix-caching \
    --port 8000
```

**Parameter Explanation**:
- `CUDA_VISIBLE_DEVICES=0`: Specify GPU device number
- `--max-model-len 4096`: Maximum sequence length
- `--enable-prefix-caching`: Enable prefix caching for better performance
- `--port 8000`: API service port

After successful startup, the API will be available at `http://localhost:8000`.

#### 2. Visual Web Interface

Launch Gradio Web interface:

```bash
python app.py --port 7860 --host 0.0.0.0
```

**Interface Modules**:

##### 🔧 API Configuration
1. **API URL**: Enter model service address (e.g., `http://192.168.5.212:8000/v1`)
2. **API Key**: Enter API key (any string works)
3. **Test Connection**: Click test button to verify connection

##### 🖼️ Single Image Processing
1. Upload image file
2. Select caption type:
   - **Detailed Description**: Formal, comprehensive prose description
   - **Casual Description**: Friendly, conversational style
   - **Direct Description**: Objective, concise point-based description
   - **Stable Diffusion Prompts**: Generate SD-style prompts
   - **MidJourney Prompts**: Generate MJ-style prompts
   - **Art Critique**: Art history style professional analysis
   - **Product Copy**: Marketing-style product description
   - **Social Media Copy**: Social media friendly engaging content
3. Set caption length
4. Configure advanced options (optional)
5. Click "Generate Caption"

##### 📁 Batch Processing
1. Upload multiple images
2. Configure processing parameters
3. Click "Start Batch Processing"
4. Download ZIP file with all results

##### 🎭 Mixed Mode Batch Processing
1. Upload multiple images
2. Configure multiple prompt templates
3. Set weights for each prompt
4. System randomly assigns prompts based on weights
5. View processing statistics and download results

#### 3. Command Line Batch Processing

Use `image_captioning.py` for batch processing:

##### Basic Usage

```bash
# Tag generation mode
python image_captioning.py --input "/path/to/images" --mode tag

# Description generation mode
python image_captioning.py --input "/path/to/images" --mode des

# Custom prompt mode
python image_captioning.py \
    --input "/path/to/images" \
    --mode custom \
    --custom_prompt "Write a detailed analysis of this image."
```

##### Full Parameters

```bash
python image_captioning.py \
    --input "/path/to/images" \          # Input folder path (required)
    --output "/path/to/output" \         # Output folder path (optional, defaults to input path)
    --api_key "your-api-key" \           # API key (optional)
    --base_url "http://ip:8000/v1" \     # API base URL (optional)
    --mode tag \                         # Processing mode (required)
    --custom_prompt "prompt" \           # Custom prompt (custom mode only)
    --max_retries 3                      # Maximum retry attempts (optional)
```

**Supported Image Formats**: `.png`, `.jpg`, `.jpeg`, `.bmp`, `.gif`, `.webp`

#### 4. Code Examples

Reference implementation from `openai_client.py`:

```python
from openai import OpenAI
import base64

# Create client
client = OpenAI(
    api_key='your-api-key',
    base_url='http://192.168.5.212:8000/v1'
)

# Process local image
def process_local_image(image_path, prompt):
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    
    image_data = f"data:image/jpeg;base64,{base64_image}"
    
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
        temperature=0.9,
        top_p=0.7,
        max_tokens=256
    )
    
    return response.choices[0].message.content.strip()

# Process image from URL
def process_url_image(image_url, prompt):
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
                    {'type': 'image_url', 'image_url': {'url': image_url}}
                ],
            }
        ],
        temperature=0.9,
        top_p=0.7,
        max_tokens=256
    )
    
    return response.choices[0].message.content.strip()

# Usage example
prompt = "Write a descriptive caption for this image in a casual tone."
result = process_local_image("/path/to/image.jpg", prompt)
print(result)
```

### ⚙️ Configuration

#### Model Service Configuration

Edit `start_command.sh` to customize startup parameters:

```bash
#!/bin/bash
CUDA_VISIBLE_DEVICES=0 vllm serve llama-joycaption-beta-one-hf-llava \
    --max-model-len 4096 \           # Maximum sequence length
    --enable-prefix-caching \        # Enable prefix caching
    --port 8000 \                    # API port
    --host 0.0.0.0 \                # Listen address
    --tensor-parallel-size 1 \       # Tensor parallel size (for multi-GPU)
    --gpu-memory-utilization 0.9     # GPU memory utilization
```

#### Web Interface Configuration

Modify default settings in `app_mix.py`:

```python
# Default API configuration
DEFAULT_API_URL = "http://192.168.5.212:8000/v1"
DEFAULT_API_KEY = "your-api-key"

# Launch parameters
demo.launch(
    server_name="0.0.0.0",    # Listen address
    server_port=7860,         # Web interface port
    share=False,              # Create public link
    show_error=True           # Show error messages
)
```

### 🐛 Troubleshooting

#### Common Issues

1. **Model Loading Failed**
   ```bash
   # Check if model files are complete
   ls -la ./llama-joycaption-beta-one-hf-llava
   
   # Re-download model
   rm -rf ./llama-joycaption-beta-one-hf-llava
   huggingface-cli download fancyfeast/llama-joycaption-beta-one-hf-llava --local-dir ./llama-joycaption-beta-one-hf-llava
   ```

2. **GPU Memory Insufficient**
   ```bash
   # Reduce maximum sequence length
   vllm serve llama-joycaption-beta-one-hf-llava --max-model-len 2048
   
   # Or adjust GPU memory utilization
   vllm serve llama-joycaption-beta-one-hf-llava --gpu-memory-utilization 0.8
   ```

3. **API Connection Failed**
   - Check if model service is running properly
   - Verify IP address and port configuration
   - Check firewall settings

4. **Empty ZIP File in Batch Processing**
   - Check if file writing code in `app_mix.py` is commented out
   - Ensure output directory has write permissions

### 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### 📞 Support

If you encounter any issues, please:
1. Check the troubleshooting section
2. Search existing issues
3. Create a new issue with detailed information

---

**Keywords**: JoyCaption, VLLM, Image Captioning, Computer Vision, AI, Machine Learning, Image Analysis, Batch Processing