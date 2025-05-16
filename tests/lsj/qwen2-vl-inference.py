import base64
from pyexpat.errors import messages

from llamafactory.chat import ChatModel

args = dict(
    model_name_or_path ='models/Qwen2-VL-7B-Instruct',
    template = 'qwen2_vl',
    infer_backend = 'vllm',
    # model_max_length = 1000
    # vllm_maxlen = 104147,
    # rope_scaling = {
    #     "type": "mrope",
    #     "mrope_section": [
    #         16,
    #         24,
    #         24
    #     ],
    #     "factor": 1.0
    # },
)

chat_model = ChatModel(args)

image_path = "./tests/lsj/testmarkdown.png"


def msg():

    with open(image_path, "rb") as f:
        encoded_image = base64.b64encode(f.read())

    encoded_image_text = encoded_image.decode("utf-8")
    base64_qwen = f"data:image;base64,{encoded_image_text}"

    messages=[
        {
            "role": "assistant",
            "content": "You are a helpful assistant. Output the markdown code for this table in the image"
        },
        {
            "role": "user",
            "content": base64_qwen
        },
    ]

    return messages, base64_qwen

messages, image = msg()

args = dict(
    image = image_path,
    messages = messages,
    # max_model_len=1000
)

a = chat_model.chat(**args)

print(a)
