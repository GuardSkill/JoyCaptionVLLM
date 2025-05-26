import base64
import os
import logging
from typing import Dict, Any
from openai import OpenAI

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('image_captioning.log'),
        logging.StreamHandler()
    ]
)

# 定义支持的图像格式
SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif",".webp"}

def create_openai_client(api_key: str, base_url: str) -> OpenAI:
    """创建 OpenAI 客户端"""
    return OpenAI(api_key=api_key, base_url=base_url)

def generate_prompt(mode: str, custom_prompt: str = None) -> str:
    """生成提示词"""
    if mode == "tag":
        return "Write a medium-length list of Booru tags for this image."
    elif mode == "des":
        return "Write a descriptive caption for this image in a casual tone."
    elif mode == "custom":
        if custom_prompt:
            return custom_prompt
        else:
            raise ValueError("Custom mode requires a custom prompt string.")
    else:
        raise ValueError("Invalid mode. Available modes: 'tag', 'des', 'custom'.")

def process_image(
    client: OpenAI,
    image_path: str,
    output_folder: str,
    prompt: str,
    max_retries: int = 3
) -> bool:
    """处理单个图像文件"""
    try:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
        image_data = f"data:image/jpeg;base64,{base64_image}"
        
        model_name = client.models.list().data[0].id
        with open(image_path, 'rb') as image_file:
            response = client.chat.completions.create(
                model=model_name,
                # messages=[
                #     {"role": "user", "content": prompt},
                #     {"role": "assistant", "content": f"Image file: {image_file}"}
                # ],
                messages=[
                    {
                    'role':'system',
                    'content': 'You are a helpful image captioner.',
                    },
                    {
                    'role':'user',
                    'content': [
                        {'type': 'text','text': prompt,}, 
                        {'type': 'image_url', 'image_url': {'url': image_data}}
                    ],
                }],
                temperature=0.9,
                top_p=0.7,
                max_tokens=256
            )
            
            caption = response.choices[0].message.content.strip()
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = os.path.join(output_folder, f"{base_name}.txt")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(caption)
            
            logging.info(f"Successfully processed: {image_path}")
            return True
        
    except Exception as e:
        logging.error(f"Error processing {image_path}: {str(e)}")
        return False

def process_images(
    input_folder: str,
    output_folder: str,
    client: OpenAI,
    prompt: str,
    max_retries: int = 3
) -> None:
    """遍历文件夹处理所有图像"""
    output_folder=input_folder
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        logging.info(f"Created output folder: {output_folder}")
    
    total_processed = 0
    total_failed = 0
    
    for root, _, files in os.walk(input_folder):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in SUPPORTED_IMAGE_EXTENSIONS:
                image_path = os.path.join(root, file)
                success = process_image(client, image_path, output_folder, prompt, max_retries)
                
                if success:
                    total_processed += 1
                else:
                    total_failed += 1
    
    logging.info(f"Processing complete. Total processed: {total_processed}, Failed: {total_failed}")

ip_algo='192.168.5.212'
def main() -> None:
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description='Image Captioning Tool')
    parser.add_argument('--input', type=str, default=r"\\192.168.1.121\\dataset\\Ghibli",required=True, help='输入图像文件夹路径')
    parser.add_argument('--output', type=str, required=False, help='输出文件夹路径')
    parser.add_argument('--api_key', type=str, required=False, default="your-api-key",help='OpenAI API 密钥')
    parser.add_argument('--base_url', type=str, default=f'http://{ip_algo}:8000/v1', help='OpenAI API 基础 URL')
    # parser.add_argument('--model', type=str, required=True, help='模型名称')
    parser.add_argument('--mode', type=str, choices=['tag', 'des', 'custom'], required=True, help='模式选择：tag（标签）、des（描述）、custom（自定义）')
    parser.add_argument('--custom_prompt', type=str, default=None, help='自定义提示词（仅在 mode 为 custom 时使用）')
    parser.add_argument('--max_retries', type=int, default=3, help='最大重试次数')
    
    args = parser.parse_args()
    
    client = create_openai_client(args.api_key, args.base_url)
    
    if args.mode == 'custom':
        if not args.custom_prompt:
            raise ValueError("Custom mode requires a custom prompt string.")
        prompt = args.custom_prompt
    else:
        prompt = generate_prompt(args.mode)
    
    process_images(args.input, args.input, client, prompt, args.max_retries)

if __name__ == "__main__":
    main()
    
#### Tag 模式：
# python image_captioning.py --input "/Disk1/Pyprojects/JoyCaptionVLLM/test_imgs"  --mode tag

### 描述性模式：
# python image_captioning.py --input "path/to/images"   --mode des

### 自定义模式：
## python image_captioning.py --input "path/to/images" --mode custom --custom_prompt "Write a detailed analysis of this image."