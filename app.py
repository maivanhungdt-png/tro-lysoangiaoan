import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# Cấu hình giao diện và tiêu đề
st.set_page_config(page_title="Trợ lý Soạn Giáo án AI", layout="wide")
st.title("📘 TRỢ LÝ SOẠN GIÁO ÁN THÔNG MINH")

# Sidebar để nhập API Key
with st.sidebar:
    st.header("⚙️ Cấu hình")
    api_key = st.text_input("Nhập Gemini API Key (AIza...):", type="password")
    st.info("Lấy Key tại: https://aistudio.google.com/")

# Khu vực tải tệp tài liệu
st.subheader("📁 1. Tải lên tài liệu bài dạy")
uploaded_file = st.file_uploader("Kéo và thả file PDF bài giảng vào đây", type="pdf")

if st.button("Bắt đầu soạn giáo án"):
    if not api_key:
        st.error("Vui lòng nhập API Key ở cột bên trái!")
    elif uploaded_file is not None:
        try:
            with st.spinner('AI đang soạn thảo giáo án...'):
                reader = PdfReader(uploaded_file)
                text_content = "".join([page.extract_text() for page in reader.pages])

                # Kết nối AI với bản thư viện mới nhất
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Tạo yêu cầu
                response = model.generate_content(f"Nội dung: {text_content}. Hãy soạn giáo án 5512.")
                st.markdown(response.text)
                st.success("Đã hoàn thành!")
        except Exception as e:
            st.error(f"Lỗi hệ thống: {str(e)}")
    else:
        st.warning("Vui lòng tải lên file PDF.")
