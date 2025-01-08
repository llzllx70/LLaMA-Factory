
import ipdb

import base64
from openai import OpenAI
# Set OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://localhost:8000/v1"
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

image_path = "testmarkdown.png"
# image_path = "shouju.png"
# image_path = "python.png"
# image_path = "3.jpg"
# image_path = 'table.png'
# image_path = 'paper_2_column.png'

with open(image_path, "rb") as f:
    encoded_image = base64.b64encode(f.read())

encoded_image_text = encoded_image.decode("utf-8")
base64_qwen = f"data:image;base64,{encoded_image_text}"
print(base64_qwen)

chat_response = client.chat.completions.create(
    model="Qwen2-VL-7B-Instruct",
    # model="Qwen2-VL-2B-Instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": [
                { "type": "image_url", "image_url": { "url": base64_qwen } },
                # {"type": "text", "text": "请描述这张图片"},
                # {"type": "text", "text": "他的成就？"},
                # {"type": "text", "text": "Output the markdown code for this table in the image"},
                # {"type": "text", "text": "Convert the content in the image to Markdown, don't add other info"},
                # {"type": "text", "text": "将图片中内容转为Markdown, 并在表格内容前添加<table_begin>作为开头，在表格内容结束后添加</table_end>作为结尾"},
                # {"type": "text", "text": "提取图片中内容的主要信息"},
                # {"type": "text", "text": "三好学生如何评选"},
                {"type": "text", "text": "Convert the content in the image to json, don't add other info"},
            ],
        },
    ],
)


print("Chat response:", chat_response)
