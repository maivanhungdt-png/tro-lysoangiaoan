import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# Cấu hình giao diện
st.set_page_config(page_title="Trợ lý Soạn Giáo án AI", layout="wide")

with st.sidebar:
    st.header("⚙️ Cấu hình")
    # Ô nhập API Key (Mã AIza... bạn đã lấy thành công)
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
            with st.spinner('Đang kết nối với AI để soạn giáo án...'):
                # Đọc dữ liệu từ PDF
                reader = PdfReader(uploaded_file)
                text_content = "".join([page.extract_text() for page in reader.pages])

                # Cấu hình kết nối AI
                genai.configure(api_key=api_key)
                
                # Gọi mô hình 1.5 Flash theo cách mới nhất để tránh lỗi 404
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Gửi yêu cầu
                response = model.generate_content(f"Dựa trên nội dung: {text_content}. Hãy soạn giáo án 5512.")
                
                st.markdown(response.text)
                st.success("Đã hoàn thành!")
        except Exception as e:
            st.error(f"Lỗi hệ thống: {str(e)}")
            st.info("Nếu vẫn lỗi 404, hãy đảm bảo bạn đã lưu file requirements.txt mới nhất.")
    else:
        st.warning("Vui lòng tải lên file PDF.")
