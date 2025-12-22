import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# --- Cấu hình trang ---
st.set_page_config(page_title="Trợ lý Soạn Giáo án", layout="centered")

# --- Giao diện Sidebar ---
with st.sidebar:
    st.title("⚙️ Cấu hình")
    api_key = st.text_input("Nhập Gemini API Key:", type="password")
    st.info("Lấy API Key tại: https://aistudio.google.com/")

# --- Giao diện Chính ---
st.title("📘 TRỢ LÝ SOẠN GIÁO ÁN THÔNG MINH")
st.write("Tải lên tài liệu và AI sẽ giúp bạn soạn giáo án theo khung năng lực.")

# 1. Khu vực tải file
st.subheader("📁 1. Tài liệu nguồn")
uploaded_file = st.file_uploader("Kéo và thả file PDF bài dạy vào đây", type="pdf")

# 2. Xử lý logic
if st.button("Bắt đầu soạn giáo án"):
    if not api_key:
        st.warning("Vui lòng nhập API Key ở cột bên trái!")
    elif uploaded_file is not None:
        try:
            # Đọc nội dung PDF
            reader = PdfReader(uploaded_file)
            text_content = ""
            for page in reader.pages:
                text_content += page.extract_text()

            # Cấu hình Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Câu lệnh gửi cho AI (Prompt)
            prompt = f"""
            Bạn là một chuyên gia sư phạm. Hãy dựa vào nội dung bài dạy sau đây:
            {text_content}
            
            Hãy soạn một giáo án chi tiết bao gồm:
            1. Mục tiêu bài học (Kiến thức, Kỹ năng, Thái độ).
            2. Thiết bị dạy học và học liệu.
            3. Tiến trình dạy học (Các hoạt động cụ thể).
            Hãy trình bày thật chuyên nghiệp và khoa học.
            """
            
            with st.spinner('AI đang suy nghĩ và soạn thảo...'):
                response = model.generate_content(prompt)
                st.subheader("📝 Kết quả giáo án:")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Có lỗi xảy ra: {e}")
    else:
        st.error("Vui lòng tải file lên trước!")