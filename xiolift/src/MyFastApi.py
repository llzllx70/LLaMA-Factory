
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import JSONResponse
import uvicorn
import os
import shutil

from MyTrainer import MyTrainer
from Retrieval import Retrierer
from Test import Infer

trainer = MyTrainer('xiolift/xiolift_img_aug', 'xiolift/infos')

retriever = Retrierer()

infer = Infer(
    type_2_images=trainer.type_2_images, 
    img_aug_dir=trainer.img_aug_dir,
    local_qwen_api=trainer.local_qwen_api,
    retrieval=retriever
)


app = FastAPI()

UPLOAD_DIR = "uploads"


@app.post("/identification")
async def predict(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    content = await file.read()

    with open(file_path, "wb") as f:
        f.write(content)

    type_ = infer.get_type(file_path)

    return {
        "result": {
            "filename": file_path,
            "type": type_
        }
    }

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5001)
