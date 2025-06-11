
#!/bin/bash
set -x

#启动qwen2.5-vl 真正方式, 单独作为一个conda环境

# pip install git+https://github.com/huggingface/transformers@f3f6c86582611976e72be054675e2bf0abb5f775
# pip install accelerate
# pip install qwen-vl-utils
# pip install 'vllm>=0.7.2'

# len=17000
len=22000

# path=output/qwen2_5vl_lora_sft

models=models/Qwen2.5-VL-7B-Instruct

# 添加--enforce-eager会解决OOM问题

nohup vllm serve ${models} --served-model-name Qwen2.5-VL-7B-Instruct --port 8002 --host 0.0.0.0 --dtype bfloat16 --max-model-len $len --enforce-eager > a.out 2>&1 &

