"""Demo Streamlit: nhan dang benh la sau rieng (mo hinh gop Kaggle + Mendeley, 7 lop).

Chay:  cd demo  &&  python -m streamlit run streamlit_app.py
Can: streamlit torch torchvision pillow pandas. Lan dau can mang de tai MobileNetV2 (~14 MB)
neu may chua co trong cache; checkpoint (model.pt) da chua day du trong so.
"""
import glob
import os
from datetime import datetime

import pandas as pd
import streamlit as st
import torch
import torch.nn as nn
import torchvision.models as tvm
import torchvision.transforms as T
from PIL import Image

APP_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(APP_DIR, "model.pt")
SAMPLES = os.path.join(APP_DIR, "samples")
CLASSES = ["Algal", "Allocaridara", "Blight", "Colletotrichum", "Healthy", "Phomopsis", "Rhizoctonia"]
INFO = {
    "Algal": ("Đốm tảo / rong", "🟢"),
    "Allocaridara": ("Bị rầy Allocaridara tấn công (côn trùng)", "🐛"),
    "Blight": ("Cháy lá (Blight)", "🟤"),
    "Colletotrichum": ("Thán thư (Colletotrichum)", "🟠"),
    "Healthy": ("Lá khỏe mạnh", "✅"),
    "Phomopsis": ("Đốm lá Phomopsis", "🟡"),
    "Rhizoctonia": ("Cháy lá Rhizoctonia", "🔴"),
}
TF = T.Compose([T.Resize((224, 224)), T.ToTensor(), T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])


@st.cache_resource
def load_model():
    m = tvm.mobilenet_v2(weights=None)
    m.classifier[1] = nn.Linear(m.last_channel, len(CLASSES))
    m.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    return m.eval()


def predict(img):
    with torch.no_grad():
        p = torch.softmax(load_model()(TF(img.convert("RGB")).unsqueeze(0)), 1)[0]
    return sorted(zip(CLASSES, p.tolist()), key=lambda t: -t[1])


def fmt(c):
    vi, em = INFO[c]
    return f"{em} {c} — {vi}"


st.set_page_config(page_title="Durian Leaf AI", page_icon="🍃", layout="wide")
st.title("🍃 Durian Leaf AI — Nhận diện bệnh lá sầu riêng")
st.caption("Mô hình MobileNetV2 huấn luyện trên hai bộ dữ liệu lá sầu riêng (Kaggle + Mendeley), 7 lớp.")
st.session_state.setdefault("history", [])

with st.sidebar:
    st.header("Cài đặt")
    thr = st.slider("Ngưỡng cảnh báo độ tin cậy", 0.3, 0.95, 0.7, 0.05,
                    help="Dưới ngưỡng này, ứng dụng hiện cảnh báo 'không chắc chắn'.")
    st.divider()
    st.subheader("7 lớp nhận diện")
    for c in CLASSES:
        st.markdown(f"{INFO[c][1]} **{c}** — {INFO[c][0]}")

tab_run, tab_gallery, tab_hist, tab_about = st.tabs(["🔍 Nhận diện", "🖼️ Ảnh mẫu", "📊 Lịch sử", "ℹ️ Giới hạn & kết quả"])

with tab_run:
    if not os.path.exists(MODEL_PATH):
        st.error("Thiếu file model.pt trong thư mục demo.")
    else:
        up = st.file_uploader("Upload ảnh lá sầu riêng (jpg/png)", type=["jpg", "jpeg", "png"])
        image = Image.open(up) if up else None
        name = up.name if up else None
        if image is not None:
            a, b = st.columns([1, 2])
            ranked = predict(image)
            top, p = ranked[0]
            with a:
                st.image(image, caption=name, width="stretch")
            with b:
                st.subheader(fmt(top))
                st.metric("Độ tin cậy", f"{p*100:.1f}%")
                if p < thr:
                    st.warning("Độ tin cậy thấp. Ảnh có thể không rõ, hoặc không phải lá sầu riêng, hoặc thuộc bệnh khác.")
                st.bar_chart(pd.DataFrame({"Xác suất": [x for _, x in ranked]}, index=[c for c, _ in ranked]), height=240)
            key = f"{up.file_id}"
            if st.session_state.get("last") != key:
                st.session_state.history.append({"Thời gian": datetime.now().strftime("%H:%M:%S"), "Ảnh": name,
                                                 "Dự đoán": top, "Tin cậy %": round(p * 100, 1)})
                st.session_state["last"] = key
        else:
            st.info("Hãy upload một ảnh lá. Có thể lấy ảnh thử ở tab 'Ảnh mẫu'.")

with tab_gallery:
    st.write("Ảnh lấy từ **tập test** (mô hình chưa dùng để huấn luyện), mỗi lớp 3 ảnh mỗi nguồn. Tải về rồi upload ở tab Nhận diện.")
    src = st.radio("Nguồn", ["kaggle", "mendeley"], horizontal=True)
    for cdir in sorted(glob.glob(os.path.join(SAMPLES, src, "*"))):
        st.markdown(f"**{os.path.basename(cdir)}**")
        ims = sorted(glob.glob(os.path.join(cdir, "*.jpg")))
        for col, f in zip(st.columns(3), ims):
            col.image(f, width="stretch", caption=os.path.basename(f))

with tab_hist:
    if st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history), hide_index=True, width="stretch")
        if st.button("Xóa lịch sử"):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("Chưa có lần nhận diện nào.")

with tab_about:
    st.subheader("Kết quả đánh giá")
    st.table(pd.DataFrame({
        "Phép đánh giá": ["Test Kaggle (5 lớp)", "Test Mendeley (6 lớp)", "Mô hình chỉ Mendeley, test trên Kaggle (4 lớp chung)",
                          "Mô hình chỉ Kaggle, test trên Mendeley (4 lớp chung)"],
        "Mô hình": ["Gộp 2 bộ", "Gộp 2 bộ", "Riêng Mendeley", "Riêng Kaggle"],
        "Accuracy": ["94,7%", "94,0%", "32,0%", "76,2%"],
    }))
    st.subheader("Giới hạn cần biết")
    st.markdown("""
- Hai kết quả đầu là **trong miền** (ảnh test cùng nguồn chụp với dữ liệu huấn luyện). Hai kết quả sau cho thấy khi gặp
  ảnh từ nguồn khác, mô hình huấn luyện trên một nguồn giảm mạnh; mô hình gộp chưa được kiểm tra trên nguồn thứ ba.
- Ứng dụng **không có cơ chế phát hiện ảnh ngoài phạm vi** đáng tin cậy. Ngưỡng cảnh báo chỉ là ngưỡng độ tin cậy: trong thử nghiệm,
  nhiều ảnh lá cây khác (ớt, cà chua) vẫn được gán nhãn bệnh sầu riêng với độ tin cậy trên 0,9. Chỉ dùng cho ảnh lá sầu riêng.
- Lớp Allocaridara là tổn thương do côn trùng (rầy), không phải bệnh nấm. Colletotrichum và Rhizoctonia chỉ có trong một bộ dữ liệu.
- Đây là công cụ nghiên cứu, không thay thế chẩn đoán của chuyên gia nông nghiệp.
    """)
