import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# 1. Cấu hình giao diện giống trang mẫu
st.set_page_config(page_title="Trợ lý Soạn giáo án NLS - Streamlit", layout="wide")

# Sidebar cấu hình
with st.sidebar:
    st.title("⚙️ Cấu hình")
    api_key = st.text_input("Nhập API Key:", type="password", help="Lấy Key tại https://aistudio.google.com/")
    st.info("Tác giả: Mai Văn Hùng")

# Tiêu đề chính
st.title("📘 TRỢ LÝ SOẠN GIÁO ÁN")
st.markdown("---")

# 2. Khu vực Tài liệu nguồn
st.subheader("📁 1. TÀI LIỆU NGUỒN")

# Giả lập tính năng tích hợp khung năng lực như ảnh mẫu
st.success("✅ Đã tự động tích hợp: khungnanglucso.pdf")

uploaded_file = st.file_uploader("Tải Ảnh/PDF bài dạy (kéo thả vào đây):", type=["pdf", "png", "jpg", "jpeg"])

# 3. Hướng dẫn sử dụng (Expander)
with st.expander("📖 Hướng dẫn sử dụng Trợ lý soạn giáo án"):
    st.write("""
    1. **Bước 1:** Nhập mã API Key vào ô cấu hình bên trái.
    2. **Bước 2:** Tải lên tệp PDF hoặc ảnh chụp nội dung bài dạy của bạn.
    3. **Bước 3:** Nhấn nút 'Bắt đầu soạn giáo án'.
    4. **Bước 4:** Đợi AI xử lý và sao chép kết quả giáo án trả về.
    """)

# 4. Xử lý chính
if st.button("Bắt đầu soạn giáo án"):
    if not api_key:
        st.error("❌ Vui lòng nhập API Key để tiếp tục!")
    elif uploaded_file is not None:
        try:
            with st.spinner('🔄 Trợ lý đang phân tích nội dung và soạn giáo án...'):
                # Xử lý đọc nội dung (Ví dụ với PDF)
                text_content = ""
                if uploaded_file.type == "application/pdf":
                    reader = PdfReader(uploaded_file)
                    for page in reader.pages:
                        text_content += page.extract_text()
                else:
                    text_content = "Nội dung từ hình ảnh bài dạy."

                # Cấu hình AI Gemini
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Prompt tối ưu theo mẫu giáo án phổ thông
                prompt = f"""
                Bạn là một chuyên gia giáo dục. Dựa trên nội dung bài giảng: {text_content} 
                và Khung năng lực số, hãy soạn một giáo án chi tiết gồm:
                - Mục tiêu bài học (Kiến thức, Năng lực, Phẩm chất).
                - Thiết bị và học liệu.
                - Các hoạt động dạy học (Khởi động, Hình thành kiến thức mới, Luyện tập, Vận dụng).
                Trình bày chuyên nghiệp theo định hướng Công văn 5512.
                """
                
                response = model.generate_content(prompt)
                
                st.markdown("### 📝 KẾT QUẢ GIÁO ÁN:")
                st.markdown(response.text)
                st.success("✨ Soạn giáo án hoàn tất!")
        except Exception as e:
            st.error(f"Lỗi hệ thống: {str(e)}")
    else:
        st.warning("⚠️ Vui lòng tải tài liệu lên trước khi bắt đầu.")
