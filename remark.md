
# Fork version for LLama-Factory

- fork at 20241122
- main for qwen2-vl
- source code analyse

# git 
1. git fetch upstream
2. git merge upstream/main

# version

- 18: (m_llama-factory) ~/llama_factory/LLaMA-Factory for test lora merge, marked in notion
- 49: (llama_factory) ~/anaconda3/envs/llama_factory/LLaMA-Factory for train (old)
- 49: (LLaMA-Factory) (base) double@CP-001:~/vsproject/LLaMA-Factory$  for train xiolift and learn source code

# install
1. pip install git+https://github.com/huggingface/transformers@21fac7abba2a37fae86106f87fcf9974fd1e3830 accelerate
    for assert "factor" in rope_scaling
 
# 18 steps

## train
~/anaconda3/envs/llama_factory_1122/bin/llamafactory-cli train examples/train_lora/qwen2vl_lora_sft.yaml

## merge
llamafactory-cli export examples/merge_lora/qwen2vl_lora_sft.yaml

# inference
1. python -m vllm.entrypoints.openai.api_server --dtype auto --max-model-len 1000 --served-model-name Qwen2-VL-7B-Instruct --model models/qwen2_vl_lora_sft
2. (llama_factory_1122) ~/PycharmProjects/LLaMA-Factory/tests/lsj$ python ./local_infer.py

nohup python -m vllm.entrypoints.openai.api_server --dtype auto --max-model-len 10000 --served-model-name Qwen2-VL-7B-Instruct-AWQ --model ~/models/Qwen2-VL-7B-Instruct-AWQ > a.out 2>&1 &
 

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

# 效果
1. 完整的一页，整体效果也不错，会对里面的内容进行适当的调整。
2. p38, 使用dpi=200, 为365k=1654*2339; 截图为160k=616*882
3. max_model_len=10000 + 选取_16.png = 12.79s
4. max_model_len=10000 + page_44.png(200dpi, 367K) = 16.87s
4. max_model_len=10000 + page_1.png(200dpi, 2M) = 14.91
4. max_model_len=10000 + page_8.png(200dpi, 3M, 纯图，无内容) = 4.3
5. max_model_len=5000 + page_44.png(200dpi) = (total length 5042) is too long
6. max_model_len=5000 + 选取_16.png = 12.53s
7. max_model_len=5000 + 选取_13.png = 4.85s
8. max_model_len=10000 + 选取_13.png = 4.82s
9. At most 1 image(s) may be provided in one request.
10. 复杂的图，中文prompt好一点

由上可知，max_model_len 长度的设置和处理时间没有关系，主要是输入图片的大小和输出的文本长度

- 使用Qwen2-VL-2B-Instruct 问题输出(105,133),(894,829), 而不是正常的数据
- 
- page_1.png Qwen2-VL-7B-Instruct-AWQ time: 16.731144666671753, out len: 570, ratio: 34.068201032021044
- page_1.png Qwen2-VL-7B-Instruct time: 15.292883157730103, out len: 570, ratio: 37.2722392580291
- page_1.png Qwen2-VL-7B-Instruct-GPTQ-Int4 time: 16.891932487487793, out len: 570, ratio: 33.743918904613835

- 
- page_44.png Qwen2-VL-7B-Instruct-AWQ time: 9.348883867263794, out len: 921, ratio: 98.51443370956706
- page_44.png Qwen2-VL-7B-Instruct time: 17.044695138931274, out len: 1066, ratio: 62.54145300405999
- page_44.png Qwen2-VL-7B-Instruct-GPTQ-Int4 time: 9.16063642501831, out len: 988, ratio: 107.85276853709705

- 

# Int4最快
[
    'page_44.png Qwen2-VL-7B-Instruct-GPTQ-Int4 time: 9.407812595367432, out len: 971, ratio: 103.21208996851585', 
    '选区_44.png Qwen2-VL-7B-Instruct-GPTQ-Int4 time: 5.632200241088867, out len: 827, ratio: 146.83426806574565', 
    'page_8.png Qwen2-VL-7B-Instruct-GPTQ-Int4 time: 3.9514098167419434, out len: 122, ratio: 30.87505615921982', 
    'page_1.png Qwen2-VL-7B-Instruct-GPTQ-Int4 time: 16.922221422195435, out len: 570, ratio: 33.68352096211078'
]


[
    'page_44.png Qwen2-VL-7B-Instruct time: 22.819846630096436, out len: 1066, ratio: 46.71372324624143', 
    '选区_44.png Qwen2-VL-7B-Instruct time: 12.982621431350708, out len: 827, ratio: 63.70054032407838', 
    'page_8.png Qwen2-VL-7B-Instruct time: 4.3634655475616455, out len: 109, ratio: 24.980144523178474', 
    'page_1.png Qwen2-VL-7B-Instruct time: 15.210984945297241, out len: 570, ratio: 37.47291855523308'
]


[
    'page_44.png Qwen2-VL-7B-Instruct-AWQ time: 11.63092303276062, out len: 921, ratio: 79.18546081044774', 
    '选区_44.png Qwen2-VL-7B-Instruct-AWQ time: 5.729761123657227, out len: 827, ratio: 144.33411483516392', 
    'page_8.png Qwen2-VL-7B-Instruct-AWQ time: 3.6018755435943604, out len: 72, ratio: 19.989585739031455', 
    'page_1.png Qwen2-VL-7B-Instruct-AWQ time: 29.750414609909058, out len: 570, ratio: 19.15939685123408'
]

page_44.png Qwen2-VL-7B-Instruct-AWQ time: 8.938807010650635, out len: 921, ratio: 103.03388348161268
选区_44.png Qwen2-VL-7B-Instruct-AWQ time: 5.571082353591919, out len: 827, ratio: 148.445122062645

dpi: 200 -> 100 -> 144 

175/22M -> 15分钟

page_44.png Qwen2-VL-7B-Instruct-AWQ time: 8.879101753234863, out len: 921, ratio: 103.72670857887829
选区_44.png Qwen2-VL-7B-Instruct-AWQ time: 5.651404142379761, out len: 827, ratio: 146.3353140502454
page_44.png Qwen2-VL-7B-Instruct-AWQ time: 8.929320573806763, out len: 921, ratio: 103.14334583323821
选区_44.png Qwen2-VL-7B-Instruct-AWQ time: 5.5972511768341064, out len: 827, ratio: 147.75109672097372
page_8.png Qwen2-VL-7B-Instruct-AWQ time: 3.5665605068206787, out len: 72, ratio: 20.187516758038292
page_1.png Qwen2-VL-7B-Instruct-AWQ time: 17.312552213668823, out len: 570, ratio: 32.92408842816176


# 选区的会额外的加标题数字序号，导致重复, 但是另外又会维持原有文本和格式 , 建议使用AWQ方式
page_44.png Qwen2-VL-7B-Instruct-AWQ time: 8.983469724655151, out len: 921, ratio: 102.5216345386364
选区_44.png Qwen2-VL-7B-Instruct-AWQ time: 5.567578554153442, out len: 827, ratio: 148.5385418375559
page_8.png Qwen2-VL-7B-Instruct-AWQ time: 3.5534567832946777, out len: 72, ratio: 20.26196022376931
选区_8.png Qwen2-VL-7B-Instruct-AWQ time: 0.5989162921905518, out len: 60, ratio: 100.18094478703937
page_1.png Qwen2-VL-7B-Instruct-AWQ time: 16.79210638999939, out len: 570, ratio: 33.944520524206894
选区_1.png Qwen2-VL-7B-Instruct-AWQ time: 4.48297381401062, out len: 563, ratio: 125.58627896519457


page_44.png Qwen2-VL-7B-Instruct-GPTQ-Int4 time: 11.98793911933899, out len: 988, ratio: 82.4161676301938
选区_44.png Qwen2-VL-7B-Instruct-GPTQ-Int4 time: 5.9749157428741455, out len: 827, ratio: 138.4119936730997
page_8.png Qwen2-VL-7B-Instruct-GPTQ-Int4 time: 3.85823917388916, out len: 122, ratio: 31.620642086069086
选区_8.png Qwen2-VL-7B-Instruct-GPTQ-Int4 time: 0.6893215179443359, out len: 78, ratio: 113.15474414988255
page_1.png Qwen2-VL-7B-Instruct-GPTQ-Int4 time: 17.063364505767822, out len: 570, ratio: 33.40490088032325
选区_1.png Qwen2-VL-7B-Instruct-GPTQ-Int4 time: 3.917076349258423, out len: 564, ratio: 143.98493920262135


page_44.png Qwen2-VL-7B-Instruct time: 19.81186032295227, out len: 1066, ratio: 53.806153618245865
选区_44.png Qwen2-VL-7B-Instruct time: 13.13526725769043, out len: 827, ratio: 62.96027205048367
page_8.png Qwen2-VL-7B-Instruct time: 4.708644866943359, out len: 109, ratio: 23.148910797079903
选区_8.png Qwen2-VL-7B-Instruct time: 1.3555171489715576, out len: 95, ratio: 70.08395288254177
page_1.png Qwen2-VL-7B-Instruct time: 14.98937201499939, out len: 570, ratio: 38.02694331888081
选区_1.png Qwen2-VL-7B-Instruct time: 8.528743743896484, out len: 597, ratio: 69.99858571518665

暂定为 Qwen2-VL-7B-Instruct-AWQ, dpi 为144, prompt 去年markdown 相关的描述

| 姓名   | 年龄 | 城市   |
|--------|------|--------|
| 张三   | 28   | 北京   |
| 李四   | 34   | 上海   |
| 王五   | 22   | 广州   |

|dd|dd| 
|----|----| 
|dd|

# 九、学生奖励条例\n\n浙农商院（2017）233 号\n\n## 第一章 总则\n\n第一条 为了贯彻党和国家的教育方针，建设优良校风学风，鼓励学生努力学习，奋发进取，促进学生德、智、体等方面全面发展，根据国家有关文件精神，结合我院实际情况，特制定本条例。\n\n第二条 学校对学生的奖励坚持精神奖励和物质奖励相结合，精神奖励为主的原则。\n\n## 第二章 奖项的设置\n\n### 第三条 学校设立以下若干个人奖和集体奖。\n\n| 奖项名称     | 奖励类型   | 评选比例 | 评选方式        |\n|-------------|-----------|---------|----------------|\n| 综合奖       |            |          |                 |\n| 一等奖学金   | 1500 元 / 学年 | 4%以内 | 每学年评选一次，由学校发文表彰、奖励 |\n| 二等奖学金   | 800 元 / 学年 | 6%以内 |                 |\n| 三等奖学金   | 500 元 / 学年 | 10%以内 |                 |\n| 国家奖学金   | 8000 元 / 年 | 根据下达名额评定 | 根据上级文件评选 |\n| 省政府奖学金 | 6000 元 / 年 | 根据下达名额评定 |                '