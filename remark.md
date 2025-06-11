
# Fork version for LLama-Factory

- fork at 20241122
- main for qwen2-vl
- source code analyse

# git 
1. git fetch upstream
2. git merge upstream/main
3. git push origin main

# version

- 18: (m_llama-factory) ~/llama_factory/LLaMA-Factory for test lora merge, marked in notion
- 49: (llama_factory) ~/anaconda3/envs/llama_factory/LLaMA-Factory for train (old)
- 49: (LLaMA-Factory) (base) double@CP-001:~/vsproject/LLaMA-Factory$  for train xiolift and learn source code

# install
1. pip install git+https://github.com/huggingface/transformers@21fac7abba2a37fae86106f87fcf9974fd1e3830 accelerate
    for assert "factor" in rope_scaling

2. ValueError: Processor was not found, please check and update your model file.
    (LLaMA-Factory) double@CP-001:~/vsproject/LLaMA-Factory$ pip install git+https://github.com/huggingface/transformers@f3f6c86582611976e72be054675e2bf0abb5f775

# sft

## train
~/anaconda3/envs/llama_factory_1122/bin/llamafactory-cli train examples/train_lora/qwen2vl_lora_sft.yaml

## merge
llamafactory-cli export examples/merge_lora/qwen2vl_lora_sft.yaml

# inference
1. python -m vllm.entrypoints.openai.api_server --dtype auto --max-model-len 1000 --served-model-name Qwen2-VL-7B-Instruct --model models/qwen2_vl_lora_sft
2. (llama_factory_1122) ~/PycharmProjects/LLaMA-Factory/tests/lsj$ python ./local_infer.py

nohup python -m vllm.entrypoints.openai.api_server --dtype auto --max-model-len 10000 --served-model-name Qwen2-VL-7B-Instruct-AWQ --model ~/models/Qwen2-VL-7B-Instruct-AWQ > a.out 2>&1 &

# sft result

## 无 {"role": "system", "content": "你是一个分类器."},
## train_epoch 3

1. origin models:  ok: 13, err: 13
2. models + lora (not merge), ok: 13, err: 13 vLLM currently only supports adding LoRA to language model
3. models + lora (merge), ok: 16, err: 10

 
## 有 {"role": "system", "content": "你是一个分类器."},
## train_epoch 3
3. models + lora (merge), ok: 17, err: 9

## train_epoch 30
4. models + lora (merge), ok: 22, err: 4

## train_epoch_100
1. 添加 desc 后， ok: 22, err: 4, 变化是有一个 限速器钢丝绳张紧装置 识别正确
2. 添加 desc 后， xiolift_sft.json 中 复制限速器钢丝绳张紧装置(增加负样本用例) 后进行训练 ok: 23, err: 3, 变化是有一个 限速器钢丝绳张紧装置 识别正确
3. 添加 desc 后，再加上 各类别的描述，使用GPT + baidu 进行多个图片共同点提取， ok: 25, err: 1


# dpo result
1. epoch3, ok: 13, err: 13, 所有的错误都误识别为 "限速器钢丝绳张紧装置"
2. epoch30, ok: 19, err: 7, 所有错误都和"限速器钢丝绳张紧装置"有关
3. epoch30, add desc, ok: 15, err: 11, 训练语料的组织不合理，应该加上 描述: [], 类别: [], 
   因为如果在生成时不加会直接输出类别信息，而没有训练语料的描述过程, 说明训练语料和生成结果没有对齐

# dpo+sft
1. epoch3, ok: 22, err: 4, 所有的错误都是"限速器钢丝绳张紧装置"没识别出来

限速器钢丝绳张紧装置 样本数量为4， 可能是太少了，不确定和类别长度有没有关系？

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
