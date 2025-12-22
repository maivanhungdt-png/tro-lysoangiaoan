import streamlit as st
from openai import OpenAI

# 1. Cấu hình trang web
st.set_page_config(page_title="Trợ lý Soạn Giáo Án", page_icon="📚")

st.title("📚 Trợ lý Soạn Giáo Án 5512")
st.write("Nhập chủ đề, lớp học và yêu cầu để tạo giáo án theo chuẩn CV 5512.")

# 2. Nhập API Key ở thanh bên (Sidebar) để bảo mật
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    st.markdown("[Lấy API Key tại đây](https://platform.openai.com/account/api-keys)")

# 3. Khởi tạo lịch sử chat
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Chào thầy/cô! Tôi có thể giúp gì cho việc soạn giáo án hôm nay?"}]

# 4. Hiển thị lịch sử chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 5. Xử lý khi người dùng nhập liệu
if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Vui lòng nhập OpenAI API Key để tiếp tục.")
        st.stop()

    client = OpenAI(api_key=openai_api_key)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # --- BÍ MẬT CÔNG NGHỆ: SYSTEM PROMPT (Lời nhắc hệ thống) ---
    # Đây là phần quan trọng nhất để biến AI thành chuyên gia giáo dục
    system_instruction = """
    Bạn là một chuyên gia giáo dục tại Việt Nam, am hiểu sâu sắc chương trình Giáo dục phổ thông 2018.
    Nhiệm vụ của bạn là hỗ trợ giáo viên soạn giáo án (kế hoạch bài dạy) theo công văn 5512.
    
    Cấu trúc giáo án cần bao gồm:
    1. Mục tiêu (Kiến thức, Năng lực, Phẩm chất).
    2. Thiết bị dạy học và học liệu.
    3. Tiến trình dạy học (Hoạt động mở đầu, Hình thành kiến thức, Luyện tập, Vận dụng).
    
    Hãy trình bày rõ ràng, sử dụng bảng biểu nếu cần thiết (dạng Markdown).
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo", # Hoặc gpt-4
        messages=[{"role": "system", "content": system_instruction}] + st.session_state.messages
    )
    
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
