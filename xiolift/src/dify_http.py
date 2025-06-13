
from flask import Flask, request, jsonify

from local_infer import XioLift, CLASSIFY_PROMPT

xiloift = XioLift("tests/lsj/xiolift_img")


app = Flask(__name__)

@app.route("/chat/completions", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return jsonify({
            "message": "这是一个 GET 请求。",
            "params": request.args.to_dict()
        })

    if request.method == "POST":
        data = request.get_json(force=True, silent=True) or {}

        classify_prompt = CLASSIFY_PROMPT.format(info=xiloift.info)

        base64_qwen = data['messages'][-1]['content'][0]['image_url']['url']

        r = xiloift.call(image_path=None, system_prompt='你是一个分类器.', text_prompt=f'{classify_prompt}', base64_qwen=base64_qwen)

        return {
            'text': r,
            'output': r
        }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8089)
