
#!/bin/bash

len=3000
name=Qwen2-VL-7B-Instruct
model=../../models/Qwen2-VL-7B-Instruct

echo python -m vllm.entrypoints.openai.api_server --dtype auto --max-model-len ${len} --served-model-name ${name} --model ${model}

