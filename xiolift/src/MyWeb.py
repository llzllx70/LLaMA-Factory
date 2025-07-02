
import streamlit as st
from PIL import Image
import requests
import io

st.set_page_config(page_title="西奥电梯部件识别", layout="centered")
st.title("西奥电梯部件识别")

# 上传图片
uploaded_file = st.file_uploader("请上传电梯部件图片", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # 显示图片

    file_bytes = uploaded_file.getvalue()  

    image = Image.open(uploaded_file)
    resized_image = image.resize((300, 300))  # 调整图片大小以适应显示
    st.image(resized_image, caption="上传的图片")

    # 按钮控制上传
    if st.button("开始识别"):
        with st.spinner("识别中..."):
            # 将图片发送给 FastAPI 服务
            files = {"file": (uploaded_file.name, io.BytesIO(file_bytes), uploaded_file.type)}

            try:
                res = requests.post("http://172.16.2.35:5001/identification", files=files)
                if res.status_code == 200:
                    result = res.json()["result"]
                    st.success(f"类别为: {result['type']}")

                else:
                    st.error("服务端返回错误")

            except Exception as e:
                st.error(f"请求失败：{e}")
