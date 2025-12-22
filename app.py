import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# Cấu hình giao diện
st.set_page_config(page_title="Trợ lý Soạn Giáo án AI", layout="wide")

with st.sidebar:
    st.header("⚙️ Cấu hình")
    # Sử dụng st.text_input để người dùng dán mã AIza... vào
    api_key = st.text_input("Nhập Gemini API Key (AIza...):", type="password")
    st.info("Lấy Key tại: https://aistudio.google.com/")

st.title("📘 TRỢ LÝ SOẠN GIÁO ÁN THÔNG MINH")

st.subheader("📁 1. Tải lên tài liệu bài dạy")
uploaded_file = st.file_uploader("Kéo và thả file PDF bài giảng vào đây", type="pdf")

if st.button("Bắt đầu soạn giáo án"):
    if not api_key:
        st.error("Vui lòng nhập API Key để bắt đầu!")
    elif uploaded_file is not None:
        try:
            with st.spinner('Đang soạn thảo giáo án...'):
                reader = PdfReader(uploaded_file)
                text_content = "".join([page.extract_text() for page in reader.pages])

                # Cấu hình API Gemini
                genai.configure(api_key=api_key)
                
                # SỬA LỖI 404: Sử dụng tên mô hình chuẩn xác
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"Dựa trên nội dung sau: {text_content}. Hãy soạn một giáo án chi tiết theo Công văn 5512."
                
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.success("Đã hoàn thành!")
        except Exception as e:
            # Hiển thị lỗi chi tiết để xử lý nếu vẫn còn vấn đề
            st.error(f"Lỗi hệ thống: {str(e)}")
    else:
        st.warning("Vui lòng tải lên file PDF.")
