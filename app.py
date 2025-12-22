import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# 1. Cấu hình giao diện và tiêu đề
st.set_page_config(page_title="Trợ lý Soạn Giáo án AI", layout="wide")
st.title("📘 TRỢ LÝ SOẠN GIÁO ÁN THÔNG MINH")

# 2. Sidebar để cấu hình API Key
with st.sidebar:
    st.header("⚙️ Cấu hình")
    # Nhập mã AIza... đã lấy từ Google AI Studio
    api_key = st.text_input("Nhập Gemini API Key (AIza...):", type="password")
    st.info("Lấy Key tại: https://aistudio.google.com/")

# 3. Khu vực tải tệp tài liệu
st.subheader("📁 1. Tải lên tài liệu bài dạy")
uploaded_file = st.file_uploader("Kéo và thả file PDF bài giảng vào đây", type="pdf")

if st.button("Bắt đầu soạn giáo án"):
    if not api_key:
        st.error("Vui lòng nhập API Key ở bên trái để bắt đầu!")
    elif uploaded_file is not None:
        try:
            with st.spinner('Đang kết nối AI để soạn giáo án...'):
                # Đọc nội dung từ PDF
                reader = PdfReader(uploaded_file)
                text_content = ""
                for page in reader.pages:
                    text_content += page.extract_text()

                # Cấu hình AI với API Key người dùng nhập
                genai.configure(api_key=api_key)
                
                # Gọi mô hình 1.5 Flash (Bản ổn định nhất hiện tại)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Tạo nội dung giáo án
                prompt = f"Dựa trên nội dung bài giảng sau: {text_content}. Hãy soạn một giáo án chi tiết theo đúng cấu trúc Công văn 5512 của Bộ Giáo dục."
                response = model.generate_content(prompt)
                
                # Hiển thị kết quả
                st.success("Đã hoàn thành soạn thảo!")
                st.markdown(response.text)
        except Exception as e:
            st.error(f"Lỗi hệ thống: {str(e)}")
    else:
        st.warning("Vui lòng tải lên file PDF nội dung bài học.")
