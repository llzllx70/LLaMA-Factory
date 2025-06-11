
#!/bin/bash
set -x

nohup llamafactory-cli train examples/train_lora/qwen2_5vl_lora_sft.yaml > sft_train.out 2>&1 &

