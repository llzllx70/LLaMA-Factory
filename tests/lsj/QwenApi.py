

import os
import base64
from openai import OpenAI
from MyPrompt import *


class QwenApi:
    
    def __init__(self):

        self.client = OpenAI(
            api_key='sk-3dee2593925641dc98bb16de1ce80938',
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

    def base64(self, image_path):
        
        with open(image_path, "rb") as f:

            encoded_image = base64.b64encode(f.read())

            encoded_image_text = encoded_image.decode("utf-8")
            base64_qwen = f"data:image;base64,{encoded_image_text}"

            return base64_qwen

    def batch_inference(self, messages):
        
        completion = self.client.chat.completions.create(
            model="qwen-vl-max-latest", # 此处以qwen-vl-max-latest为例，可按需更换模型名称。模型列表：https://help.aliyun.com/model-studio/getting-started/models
            messages=messages
        )

        r = completion.choices[0].message.content
        
        print(r)
        return r
        

    def classify_info(self, classify, files):

        messages = [
            {
                "role":"system",
                "content": [
                    {
                        "type": "text", 
                        "text": "You are a helpful assistant."
                    }
                ]
            },

            {
                "role": "user", 
                "content": [ 
                    {
                        "type": "image_url", 
                        "image_url": {"url": self.base64(file)}
                    } 
                    for file in files
                ]
            }
        ]

        messages[-1]["content"].append({
            "type": "text", 
            "text": INFO_EXTRACT_PROMPT.format(classify=classify)
        })  

        return self.batch_inference(messages=messages)


    def image_info(self, classify, file):

        try:

            messages = [
                {
                    "role":"system",
                    "content": [
                        {
                            "type": "text", 
                            "text": "You are a helpful assistant."
                        }
                    ]
                },

                {
                    "role": "user", 
                    "content": [ 
                        {
                            "type": "image_url", 
                            "image_url": {"url": self.base64(file)}
                        } 
                    ]
                }
            ]

            messages[-1]["content"].append({
                "type": "text", 
                "text": IMAGE_EXTRACT_PROMPT.format(classify=classify)
            })  

            return self.batch_inference(messages=messages)

        except Exception as e:
            return 'None'

