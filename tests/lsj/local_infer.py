
import time
import base64
from openai import OpenAI
# Set OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://172.16.2.49:8002/v1"
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

# image_path = "testmarkdown.png"
# image_path = "shouju.png"
# image_path = "python.png"
# image_path = "3.jpg"
# image_path = 'table.png'
# image_path = 'paper_2_column.png'
# image_path = "008.png"
# image_path = "009.png"
# image_path = "选区_011.png"
# image_path = "选区_018.png"
# image_path = "page_1.png"
# image_path = "page_44.png"
# image_path = "选区_44.png"
# image_path = "page_8.png"
# image_path = "page_1.png"



def f(image_path, model):

    print(f'----------------{image_path}------------------{model}-------------------------------------')

    with open(image_path, "rb") as f:
        encoded_image = base64.b64encode(f.read())

    encoded_image_text = encoded_image.decode("utf-8")
    base64_qwen = f"data:image;base64,{encoded_image_text}"
    # print(base64_qwen)

    a = time.time()
    chat_response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": [
                    { "type": "image_url", "image_url": { "url": base64_qwen } },
                    # {"type": "text", "text": "Extract all content from the image in detail and organize it into a more understandable format. The requirements are as follows: 1. If it's a table, convert it into Markdown table format. 2. If there are original numbered titles, retain the numbering. 3. Follow the original order of the text. 4. Do not repeatedly output characters like |."}
                    {"type": "text", "text": "Extract all content from the image in detail and organize it into a more understandable format. The requirements are as follows: 1. If there are original numbered titles, retain the numbering. 2. Follow the original order of the text. 3. Do not repeatedly output characters like |."}
                ]
            }
        ],

        temperature = 0.01,
        top_p = 0.1
    )


    r = chat_response.choices[0].message.content
    print("Chat response:\n", r)

    b = time.time()

    return f'{image_path} {model} time: {b-a}, out len: {len(r)}, ratio: {len(r)/(b-a)}'

images = [
    "page_6.png"
    # "page_44.png",
    # "选区_44.png",
    # "page_8.png",
    # "选区_8.png",
    # "page_1.png",
    # "选区_1.png"
]

ret = []

# model="Qwen2-VL-7B-Instruct-AWQ"
# model="Qwen2-VL-7B-Instruct"
# model='Qwen2-VL-7B-Instruct-GPTQ-Int4'
model = "Qwen2.5-VL-7B-Instruct"


for image_path in images:

    r = f(image_path, model)
    ret.append(r)

for i in ret:
    print(i)
