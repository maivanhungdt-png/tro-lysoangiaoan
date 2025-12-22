import streamlit as st
import google.generativeai as genai

# 1. CẤU HÌNH TRANG WEB
st.set_page_config(page_title="Trợ lý Soạn Giáo Án", page_icon="📚")
st.title("📚 Trợ lý Soạn Giáo Án 5512")

# 2. THANH BÊN (SIDEBAR)
with st.sidebar:
    st.header("⚙️ Cài đặt")
    api_key = st.text_input("Nhập Google API Key:", type="password")
    st.markdown("[👉 Lấy API Key tại đây](https://aistudio.google.com/app/apikey)")
    st.divider()
    if st.button("🗑️ Xóa hội thoại"):
        st.session_state.messages = []
        st.rerun()

# 3. LỊCH SỬ CHAT
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Chào Thầy/Cô! Mời nhập tên bài dạy để em soạn giáo án ạ."}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 4. XỬ LÝ
if prompt := st.chat_input("Ví dụ: Toán 6 bài Phân số, 2 tiết"):
    if not api_key:
        st.info("⚠️ Vui lòng nhập API Key trước.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # CẤU HÌNH AI
    genai.configure(api_key=api_key)
    
    # System Prompt chuẩn 5512
    sys_prompt = """Bạn là chuyên gia giáo dục. Hãy soạn giáo án theo công văn 5512 gồm:
    I. Mục tiêu (Kiến thức, Năng lực, Phẩm chất)
    II. Thiết bị
    III. Tiến trình (4 hoạt động: Mở đầu, Kiến thức mới, Luyện tập, Vận dụng).
    Mỗi hoạt động cần: Mục tiêu, Nội dung, Sản phẩm, Tổ chức thực hiện.
    """

    try:
        # Dùng model flash chạy cho nhanh
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=sys_prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Đang soạn..."):
                # Gửi tin nhắn
                response = model.generate_content(prompt)
                st.markdown(response.text)
                
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Lỗi: {e}")
