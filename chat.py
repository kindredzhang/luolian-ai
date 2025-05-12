import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")

if not OPENAI_API_KEY or not OPENAI_API_BASE:
    raise ValueError("OPENAI_API_KEY 和 OPENAI_API_BASE 必须设置")

import base64
from openai import OpenAI
from pathlib import Path

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

default_prompt = """Generate a CSV string that exactly replicates the provided example output.

The CSV should represent data organized under three distinct section headers:

'FABRICATION MATERIALS': This header should occupy a full row, followed by four commas (e.g., "FABRICATION MATERIALS",,,,).
'ERECTION MATERIALS': This header should also occupy a full row, followed by four commas (e.g., "ERECTION MATERIALS",,,,).
'CUT PIPE LENGTH': This header should occupy a full row, followed by seven commas (e.g., "CUT PIPE LENGTH",,,,,,,).
Each section header should be followed by its respective column headers, and then the exact data rows as shown in the example.

The specific column headers for 'FABRICATION MATERIALS' and 'ERECTION MATERIALS' are: 'PT NO', 'COMPONENT DESCRIPTION', 'N.S. (MM)', 'ITEM CODE', 'QTY'.

The specific column headers for 'CUT PIPE LENGTH' are: 'PIECE NO', 'CUT LENGTH', 'N.S. (MM)', 'REMARKS', 'PIECE NO', 'CUT LENGTH', 'N.S. (MM)', 'REMARKS'.

Include an empty line (a single newline character) between the end of one section's data and the beginning of the next section's header.

All section headers and any data values containing spaces or special characters (like slashes or hyphens in descriptions) must be enclosed in double quotes.

Your response must contain ONLY the generated CSV string, without any additional text, explanations, or formatting."""

def chat_with_image(image_path: str, prompt: str = default_prompt):
    """
    使用图片进行对话
    :param image_path: 图片路径
    :param prompt: 对话提示词
    :return: AI的回复
    """
    # 检查文件是否存在
    if not Path(image_path).exists():
        raise FileNotFoundError(f"图片文件不存在: {image_path}")
    
    # 检查文件格式
    if not image_path.lower().endswith('.png'):
        raise ValueError("目前只支持PNG格式的图片")
    
    # 初始化客户端
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE
    )
    
    # 编码图片
    base64_image = encode_image(image_path)
    
    # 创建对话
    completion = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=1000
    )
    
    return completion.choices[0].message.content