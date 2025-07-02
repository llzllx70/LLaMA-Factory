

from flask import Flask, request

app = Flask(__name__)

from MyTrainer import MyTrainer
from Retrieval import Retrierer
from Test import Infer

trainer = MyTrainer('xiolift/xiolift_img_aug', 'xiolift/infos')

retriever = Retrierer()

test = Infer(
    type_2_images=trainer.type_2_images, 
    img_aug_dir=trainer.img_aug_dir,
    local_qwen_api=trainer.local_qwen_api,
    retrieval=retriever
)


# 支持 GET 和 POST 请求的接口
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':

        return '1111'

        try:

            file = request.files.get('file')

            if file:
                filename = file.filename

                file_path = f"./uploads/{filename}"
                file.save(file_path)

                # p_type = test.get_type(image=file_path)
                
                # return p_type

            return "You sent a POST request!"

        except Exception as e:
            return f"An error occurred: {str(e)}"

    else:
        return "You sent a GET request!"

# 启动服务器
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
