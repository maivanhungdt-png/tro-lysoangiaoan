import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# Cấu hình giao diện trang web
st.set_page_config(page_title="Trợ lý Soạn Giáo án AI", layout="wide")

# Sidebar để cấu hình
with st.sidebar:
    st.header("⚙️ Cấu hình")
    api_key = st.text_input("Nhập Gemini API Key (AIza...):", type="password")
    st.info("Lấy Key tại: https://aistudio.google.com/")

st.title("📘 TRỢ LÝ SOẠN GIÁO ÁN THÔNG MINH")
st.markdown("---")

# 1. Khu vực tải tài liệu
st.subheader("📁 1. Tải lên tài liệu bài dạy")
uploaded_file = st.file_uploader("Kéo và thả file PDF bài giảng vào đây", type="pdf")

# 2. Xử lý logic soạn giáo án
if st.button("Bắt đầu soạn giáo án"):
    if not api_key:
        st.error("Vui lòng nhập API Key ở cột bên trái để bắt đầu!")
    elif uploaded_file is not None:
        try:
            with st.spinner('AI đang đọc tài liệu và soạn thảo giáo án...'):
                # Đọc văn bản từ PDF
                reader = PdfReader(uploaded_file)
                text_content = ""
                for page in reader.pages:
                    text_content += page.extract_text()

                # Cấu hình AI Gemini với Model mới nhất
                genai.configure(api_key=api_key)
                # Sử dụng 'gemini-1.5-flash' để tốc độ nhanh và ổn định
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Bạn là một chuyên gia giáo dục tại Việt Nam. 
                Dựa trên nội dung sau: {text_content}
                
                Hãy soạn một giáo án chi tiết theo định hướng phát triển năng lực (Công văn 5512), bao gồm:
                1. Mục tiêu (Kiến thức, Năng lực, Phẩm chất).
                2. Thiết bị dạy học và học liệu.
                3. Tiến trình dạy học:
                   - Hoạt động 1: Xác định vấn đề/Nhiệm vụ học tập (Khởi động).
                   - Hoạt động 2: Hình thành kiến thức mới.
                   - Hoạt động 3: Luyện tập.
                   - Hoạt động 4: Vận dụng.
                Trình bày dưới dạng Markdown chuyên nghiệp.
                """
                
                response = model.generate_content(prompt)
                
                st.success("Đã soạn xong giáo án!")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Lỗi hệ thống: {str(e)}")
            st.info("Mẹo: Hãy kiểm tra lại API Key hoặc đảm bảo file PDF không bị khóa.")
    else:
        st.warning("Vui lòng tải lên một file PDF nội dung bài học.")
