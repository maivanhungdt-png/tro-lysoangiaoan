import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# Cấu hình giao diện chuẩn
st.set_page_config(page_title="Trợ lý Soạn Giáo án AI", layout="wide")
st.title("📘 TRỢ LÝ SOẠN GIÁO ÁN THÔNG MINH")

with st.sidebar:
    st.header("⚙️ Cấu hình")
    # Ô nhập API Key (Mã AIza... bạn đã lấy thành công)
    api_key = st.text_input("Nhập API Key:", type="password")
    st.info("Tác giả: Mai Văn Hùng")

st.subheader("📁 1. Tải lên tài liệu bài dạy")
uploaded_file = st.file_uploader("Kéo và thả file bài dạy vào đây", type=["pdf", "png", "jpg", "jpeg"])

if st.button("Bắt đầu soạn giáo án"):
    if not api_key:
        st.error("Vui lòng nhập API Key!")
    elif uploaded_file is not None:
        try:
            with st.spinner('Đang kết nối AI...'):
                reader = PdfReader(uploaded_file)
                text_content = "".join([page.extract_text() for page in reader.pages])

                # Cấu hình AI Gemini bản ổn định nhất
                genai.configure(api_key=api_key)
                # DÙNG ĐÚNG TÊN MÔ HÌNH SAU:
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                response = model.generate_content(f"Nội dung: {text_content}. Hãy soạn giáo án 5512.")
                st.markdown(response.text)
                st.success("Đã hoàn thành!")
        except Exception as e:
            st.error(f"Lỗi hệ thống: {str(e)}")
    else:
        st.warning("Vui lòng tải file lên.")
