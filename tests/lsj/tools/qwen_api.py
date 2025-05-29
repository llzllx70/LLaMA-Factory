#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/9 下午1:23
# @Author  : geyingke
# @File    : qwen_api.py
# @Software: PyCharm
import logging
import random
import re
from typing import List, Dict, Optional

import dashscope


dashscope.api_key = 'sk-3dee2593925641dc98bb16de1ce80938'

class QwenApi:

    def __init__(self, model_name: str = "qwen-max", **kwargs):

        self.model_name = model_name

        self.model_params = kwargs.get("model_params", {})

    def chat(self, messages: List) -> str:

        response = dashscope.Generation.call(
            model=self.model_name,
            messages=messages,
            seed=random.randint(1, 10000),
            result_format='message',  # 将返回结果格式设置为 message
            timeout=600
        )
        return response.output.choices[0].message.content
