import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# Cấu hình giao diện
st.set_page_config(page_title="Trợ lý Soạn Giáo án Thông minh", layout="wide")

with st.sidebar:
    st.title("⚙️ Cấu hình")
    # Sử dụng mã API Key AIza... bạn đã lấy thành công
    api_key = st.text_input("Nhập API Key:", type="password")
    st.info("Tác giả: Mai Văn Hùng")

st.title("📘 TRỢ LÝ SOẠN GIÁO ÁN THÔNG MINH")

st.subheader("📁 1. Tải lên tài liệu bài dạy")
uploaded_file = st.file_uploader("Kéo và thả file PDF bài giảng vào đây", type=["pdf", "png", "jpg", "jpeg"])

if st.button("Bắt đầu soạn giáo án"):
    if not api_key:
        st.error("Vui lòng nhập API Key ở cột bên trái!")
    elif uploaded_file is not None:
        try:
            with st.spinner('AI đang soạn thảo giáo án...'):
                # Đọc nội dung PDF
                reader = PdfReader(uploaded_file)
                text_content = "".join([page.extract_text() for page in reader.pages])

                # Cấu hình AI Gemini
                genai.configure(api_key=api_key)
                
                # SỬA LỖI 404: Sử dụng đúng định danh mô hình ổn định
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                response = model.generate_content(f"Nội dung: {text_content}. Hãy soạn giáo án chi tiết theo Công văn 5512.")
                st.markdown(response.text)
                st.success("Đã hoàn thành!")
        except Exception as e:
            st.error(f"Lỗi hệ thống: {str(e)}")
    else:
        st.warning("Vui lòng tải lên tài liệu.")
