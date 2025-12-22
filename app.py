import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(
    page_title="Trợ lý Soạn Giáo Án 5512",
    page_icon="📚",
    layout="centered"
)

st.title("📚 Trợ lý Soạn Giáo Án - Chuẩn 5512")
st.markdown("---")

# --- CẤU HÌNH SIDEBAR (CỘT BÊN TRÁI) ---
with st.sidebar:
    st.header("⚙️ Cấu hình")
    st.write("Để sử dụng, bạn cần có Google API Key (Miễn phí).")
    api_key = st.text_input("Nhập Google API Key:", type="password")
    st.markdown("[👉 Lấy API Key tại đây](https://aistudio.google.com/app/apikey)")
    
    st.divider()
    st.write("💡 **Mẹo:** Hãy cung cấp tên bài học, lớp, và thời lượng (số tiết) để có kết quả tốt nhất.")
    
    # Nút xóa lịch sử chat
    if st.button("🗑️ Xóa hội thoại"):
        st.session_state.messages = []
        st.rerun()

# --- KHỞI TẠO LỊCH SỬ CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Chào Thầy/Cô! Em là trợ lý ảo chuyên hỗ trợ soạn giáo án theo công văn 5512. Thầy/Cô muốn soạn bài nào hôm nay ạ?"}
    ]

# --- HIỂN THỊ LỊCH SỬ CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- XỬ LÝ KHI NGƯỜI DÙNG NHẬP LIỆU ---
if prompt := st.chat_input("Ví dụ: Soạn giáo án Ngữ Văn 8, bài 'Trong lòng mẹ', 2 tiết..."):
    
    # 1. Kiểm tra API Key
    if not api_key:
        st.info("⚠️ Vui lòng nhập Google API Key ở cột bên trái để bắt đầu.")
        st.stop()

    # 2. Hiển thị câu hỏi của người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3. Cấu hình AI (System Prompt - Phần quan trọng nhất)
    try:
        genai.configure(api_key=api_key)
        
        # System Prompt: Chỉ thị cho AI cách hành xử và định dạng giáo án
        system_instruction = """
        Bạn là một chuyên gia giáo dục và cố vấn chuyên môn tại Việt Nam. 
        Nhiệm vụ của bạn là soạn giáo án (Kế hoạch bài dạy) chi tiết theo chuẩn Công văn 5512/BGDĐT-GDTrH.

        YÊU CẦU VỀ CẤU TRÚC:
        1. Tên bài dạy, Môn học, Lớp, Thời lượng.
        2. I. MỤC TIÊU:
           - Về kiến thức.
           - V
