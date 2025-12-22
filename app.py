import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# Cấu hình giao diện ứng dụng
st.set_page_config(page_title="Trợ lý Soạn Giáo án AI", layout="wide")
st.title("📘 TRỢ LÝ SOẠN GIÁO ÁN THÔNG MINH")

with st.sidebar:
    st.header("⚙️ Cấu hình")
    # Ô nhập API Key (Mã AIza... bạn đã lấy thành công)
    api_key = st.text_input("Nhập Gemini API Key (AIza...):", type="password")

st.subheader("📁 1. Tải lên tài liệu bài giảng")
uploaded_file = st.file_uploader("Kéo và thả file PDF bài giảng vào đây", type="pdf")

if st.button("Bắt đầu soạn giáo án"):
    if not api_key:
        st.error("Vui lòng nhập API Key để bắt đầu!")
    elif uploaded_file is not None:
        try:
            with st.spinner('Đang kết nối với AI để soạn giáo án...'):
                reader = PdfReader(uploaded_file)
                text_content = "".join([page.extract_text() for page in reader.pages])

                # Cấu hình kết nối Google AI
                genai.configure(api_key=api_key)
                
                # SỬA LỖI 404: Gọi trực tiếp mô hình Flash ổn định
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Gửi yêu cầu soạn thảo
                response = model.generate_content(f"Dựa trên nội dung: {text_content}. Hãy soạn giáo án chi tiết theo Công văn 5512.")
                
                st.markdown(response.text)
                st.success("Đã hoàn thành!")
        except Exception as e:
            st.error(f"Lỗi hệ thống: {str(e)}")
    else:
        st.warning("Vui lòng tải lên file PDF nội dung bài học.")
