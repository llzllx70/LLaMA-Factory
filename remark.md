
# Fork version for LLama-Factory

- fork at 20241122
- main for qwen2-vl
- source code analyse

# version

- 18: (m_llama-factory) ~/llama_factory/LLaMA-Factory for test lora merge, marked in notion
- 49: (llama_factory) ~/anaconda3/envs/llama_factory/LLaMA-Factory for train


# 18 steps

## train
~/anaconda3/envs/llama_factory_1122/bin/llamafactory-cli train examples/train_lora/qwen2vl_lora_sft.yaml

## merge
llamafactory-cli export examples/merge_lora/qwen2vl_lora_sft.yaml

# inference
1. python -m vllm.entrypoints.openai.api_server --dtype auto --max-model-len 1000 --served-model-name Qwen2-VL-7B-Instruct --model models/qwen2_vl_lora_sft
2. (llama_factory_1122) ~/PycharmProjects/LLaMA-Factory/tests/lsj$ python ./local_infer.py
 

# conclusion

Using the following data, the result is good

  {
    "messages": [
      {
        "content": "<image>他取得过什么成就？",
        "role": "user"
      },
      {
        "content": "他于2022年6月被任命为神舟十六号任务的有效载荷专家，从而成为2023年5月30日进入太空的首位平民宇航员。他负责在轨操作空间科学实验有效载荷。",
        "role": "assistant"
      }
    ],
    "images": [
      "mllm_demo_data/3.jpg"
    ]
  }
  
# gpu use

1. load Qwen2-VL-7B-Instruct use max-model-len=1000, GPU=21536M, when max-model-len=2000, GPU also 21536M
2. inference table.png, error 1662 > 1000
3. use mx-model-len=2000, using 22152MB
4. support two columns for paper, result is good
5. add <table_begin> ... </table_end> is ok, but not <table> ... </table>
6. about one image / 5s
7. not suggest change it to json



| 姓名   | 年龄 | 城市   |
|--------|------|--------|
| 张三   | 28   | 北京   |
| 李四   | 34   | 上海   |
| 王五   | 22   | 广州   |

|dd|dd| 
|----|----| 
|dd|

# 九、学生奖励条例\n\n浙农商院（2017）233 号\n\n## 第一章 总则\n\n第一条 为了贯彻党和国家的教育方针，建设优良校风学风，鼓励学生努力学习，奋发进取，促进学生德、智、体等方面全面发展，根据国家有关文件精神，结合我院实际情况，特制定本条例。\n\n第二条 学校对学生的奖励坚持精神奖励和物质奖励相结合，精神奖励为主的原则。\n\n## 第二章 奖项的设置\n\n### 第三条 学校设立以下若干个人奖和集体奖。\n\n| 奖项名称     | 奖励类型   | 评选比例 | 评选方式        |\n|-------------|-----------|---------|----------------|\n| 综合奖       |            |          |                 |\n| 一等奖学金   | 1500 元 / 学年 | 4%以内 | 每学年评选一次，由学校发文表彰、奖励 |\n| 二等奖学金   | 800 元 / 学年 | 6%以内 |                 |\n| 三等奖学金   | 500 元 / 学年 | 10%以内 |                 |\n| 国家奖学金   | 8000 元 / 年 | 根据下达名额评定 | 根据上级文件评选 |\n| 省政府奖学金 | 6000 元 / 年 | 根据下达名额评定 |                '