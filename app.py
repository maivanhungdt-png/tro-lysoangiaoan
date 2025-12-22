import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# Cấu hình giao diện và tiêu đề
st.set_page_config(page_title="Trợ lý Soạn Giáo án AI", layout="wide")
st.title("📘 TRỢ LÝ SOẠN GIÁO ÁN THÔNG MINH")

with st.sidebar:
    st.header("⚙️ Cấu hình")
    # Ô nhập API Key (Mã AIza... bạn đã lấy thành công)
    api_key = st.text_input("Nhập Gemini API Key (AIza...):", type="password")
    st.info("Tác giả: Mai Văn Hùng")

st.subheader("📁 1. Tải lên tài liệu bài dạy")
uploaded_file = st.file_uploader("Kéo và thả file PDF bài dạy vào đây", type=["pdf", "png", "jpg", "jpeg"])

if st.button("Bắt đầu soạn giáo án"):
    if not api_key:
        st.error("Vui lòng nhập API Key!")
    elif uploaded_file is not None:
        try:
            with st.spinner('AI đang soạn thảo giáo án...'):
                # Đọc dữ liệu từ file PDF
                reader = PdfReader(uploaded_file)
                text_content = "".join([page.extract_text() for page in reader.pages])

                # Cấu hình kết nối Google AI
                genai.configure(api_key=api_key)
                
                # SỬA LỖI 404: Sử dụng đúng định danh mô hình ổn định nhất
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Gửi yêu cầu soạn thảo
                response = model.generate_content(f"Dựa trên nội dung: {text_content}. Hãy soạn giáo án chi tiết theo Công văn 5512.")
                
                st.markdown(response.text)
                st.success("Đã hoàn thành!")
        except Exception as e:
            st.error(f"Lỗi hệ thống: {str(e)}")
    else:
        st.warning("Vui lòng tải lên file tài liệu.")
