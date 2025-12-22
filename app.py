import streamlit as st
import google.generativeai as genai

# 1. CẤU HÌNH TRANG WEB
st.set_page_config(page_title="Trợ lý Soạn Giáo Án 5512", page_icon="📚")
st.title("📚 Trợ lý Soạn Giáo Án - Chuẩn 5512")

# 2. THANH BÊN (SIDEBAR)
with st.sidebar:
    st.header("⚙️ Cài đặt")
    api_key = st.text_input("Nhập Google API Key:", type="password")
    st.markdown("[👉 Lấy API Key miễn phí tại đây](https://aistudio.google.com/app/apikey)")
    st.divider()
    if st.button("🗑️ Xóa hội thoại"):
        st.session_state.messages = []
        st.rerun()

# 3. LỜI NHẮC HỆ THỐNG (SYSTEM PROMPT)
# Đây là phần "bộ não" hướng dẫn AI cách soạn bài
system_prompt = """
Bạn là một chuyên gia giáo dục Việt Nam. Nhiệm vụ của bạn là soạn Kế hoạch bài dạy (Giáo án) theo công văn 5512.

CẤU TRÚC BẮT BUỘC:
I. MỤC TIÊU (Kiến thức, Năng lực, Phẩm chất).
II. THIẾT BỊ DẠY HỌC.
III. TIẾN TRÌNH DẠY HỌC (Gồm 4 hoạt động):
   1. Hoạt động mở đầu (Xác định vấn đề).
   2. Hoạt động hình thành kiến thức mới.
   3. Hoạt động luyện tập.
   4. Hoạt động vận dụng.

Trong mỗi hoạt động phải có đủ 4 mục: a) Mục tiêu, b) Nội dung, c) Sản phẩm, d) Tổ chức thực hiện.
Trình bày bằng Markdown, rõ ràng, đẹp mắt.
"""

# 4. KHỞI TẠO LỊCH SỬ CHAT
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Chào Thầy/Cô! Mời Thầy/Cô nhập tên bài học, môn và lớp để em soạn giáo án ạ."}
    ]

# 5. HIỂN THỊ HỘI THOẠI
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 6. XỬ LÝ KHI NHẬP LIỆU
if prompt := st.chat_input("Ví dụ: Soạn bài 'Sóng' - Ngữ văn 12, 2 tiết"):
    if not api_key:
        st.info("⚠️ Vui lòng nhập API Key ở cột bên trái trước.")
        st.stop()

    # Hiển thị tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    try:
        # Cấu hình API
        genai.configure(api_key=api_key)
        
        # --- SỬ DỤNG MODEL GEMINI-PRO (ỔN ĐỊNH HƠN) ---
        model = genai.GenerativeModel('gemini-pro')
        
        # Tạo lịch sử chat để gửi cho AI
        # Mẹo: Đưa System Prompt vào đầu lịch sử để AI hiểu nhiệm vụ
        history_for_ai = [
            {'role': 'user', 'parts': [system_prompt]},
            {'role': 'model', 'parts': ['Dạ, tôi đã hiểu nhiệm vụ soạn giáo án 5512. Mời thầy cô ra đề bài.']}
        ]
        
        # Thêm các tin nhắn cũ vào lịch sử
        for msg in st.session_state.messages:
            if msg['role'] == 'user':
                history_for_ai.append({'role': 'user', 'parts': [msg['content']]})
            else:
                history_for_ai.append({'role': 'model', 'parts': [msg['content']]})

        # Gọi AI
        with st.chat_message("assistant"):
            with st.spinner("Đang soạn giáo án..."):
                chat = model.start_chat(history=history_for_ai[:-1])
                response = chat.send_message(history_for_ai[-1]['parts'][0])
                st.markdown(response.text)
                
        # Lưu kết quả
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Lỗi: {e}")
