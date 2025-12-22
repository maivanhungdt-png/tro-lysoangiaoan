import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

st.set_page_config(page_title="Trợ lý Soạn Giáo án AI", layout="wide")
st.title("📘 TRỢ LÝ SOẠN GIÁO ÁN THÔNG MINH")

with st.sidebar:
    st.header("⚙️ Cấu hình")
    # Nhập mã AIza... bạn đã lấy thành công
    api_key = st.text_input("Nhập Gemini API Key (AIza...):", type="password")

st.subheader("📁 1. Tải lên tài liệu bài dạy")
uploaded_file = st.file_uploader("Kéo và thả file PDF bài giảng vào đây", type="pdf")

if st.button("Bắt đầu soạn giáo án"):
    if not api_key:
        st.error("Vui lòng nhập API Key ở bên trái!")
    elif uploaded_file is not None:
        try:
            with st.spinner('AI đang soạn giáo án...'):
                reader = PdfReader(uploaded_file)
                text_content = "".join([page.extract_text() for page in reader.pages])
                genai.configure(api_key=api_key)
                # Gọi trực tiếp mô hình Flash ổn định
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"Nội dung bài dạy: {text_content}. Hãy soạn giáo án chi tiết theo Công văn 5512.")
                st.markdown(response.text)
                st.success("Đã hoàn thành!")
        except Exception as e:
            st.error(f"Lỗi hệ thống: {str(e)}")
    else:
        st.warning("Vui lòng tải lên file PDF.")
