
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