import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(
    page_title="Trợ lý Soạn Giáo Án 5512",
    page_icon="📚",
    layout="centered"
)

st.title("📚 Trợ lý Soạn Giáo Án - Chuẩn 5512")
st.markdown("---")

# --- 2. CẤU HÌNH SIDEBAR (CỘT BÊN TRÁI) ---
with st.sidebar:
    st.header("⚙️ Cấu hình")
    st.write("Để sử dụng, bạn cần có Google API Key (Miễn phí).")
    
    # Nhập API Key
    api_key = st.text_input("Nhập Google API Key:", type="password")
    
    st.markdown("[👉 Lấy API Key tại đây](https://aistudio.google.com/app/apikey)")
    st.divider()
    
    st.write("💡 **Mẹo:** Hãy cung cấp tên bài học, lớp, và thời lượng (số tiết) để có kết quả tốt nhất.")
    
    # Nút xóa lịch sử chat để bắt đầu lại
    if st.button("🗑️ Xóa hội thoại"):
        st.session_state.messages = []
        st.rerun()

# --- 3. KHỞI TẠO LỊCH SỬ CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Chào Thầy/Cô! Em là trợ lý ảo chuyên hỗ trợ soạn giáo án theo công văn 5512. Thầy/Cô muốn soạn bài nào hôm nay ạ?"}
    ]

# --- 4. HIỂN THỊ LỊCH SỬ CHAT RA MÀN HÌNH ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. XỬ LÝ KHI NGƯỜI DÙNG NHẬP LIỆU ---
if prompt := st.chat_input("Ví dụ: Soạn giáo án Ngữ Văn 8, bài 'Trong lòng mẹ', 2 tiết..."):
    
    # Kiểm tra xem đã nhập API Key chưa
    if not api_key:
        st.info("⚠️ Vui lòng nhập Google API Key ở cột bên trái để bắt đầu.")
        st.stop()

    # Hiển thị câu hỏi của người dùng ngay lập tức
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Bắt đầu gọi AI xử lý
    try:
        genai.configure(api_key=api_key)
        
        # --- PHẦN QUAN TRỌNG NHẤT: SYSTEM PROMPT ---
        # Đây là đoạn hướng dẫn AI cách làm việc.
        # Đã được kiểm tra kỹ các dấu ngoặc kép """
        
        system_instruction = """
        Bạn là một chuyên gia giáo dục và cố vấn chuyên môn tại Việt Nam. 
        Nhiệm vụ của bạn là soạn giáo án (Kế hoạch bài dạy) chi tiết theo chuẩn Công văn 5512/BGDĐT-GDTrH.

        YÊU CẦU VỀ CẤU TRÚC:
        1. Tên bài dạy, Môn học, Lớp, Thời lượng.
        2. I. MỤC TIÊU:
           - Về kiến thức.
           - Về năng lực (Năng lực chung và Năng lực đặc thù).
           - Về phẩm chất.
        3. II. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU.
        4. III. TIẾN TRÌNH DẠY HỌC:
           Phải chia rõ thành 4 hoạt động:
           - Hoạt động 1: Xác định vấn đề/Nhiệm vụ học tập (Mở đầu).
           - Hoạt động 2: Hình thành kiến thức mới.
           - Hoạt động 3: Luyện tập.
           - Hoạt động 4: Vận dụng.
           
           Trong mỗi hoạt động cần ghi rõ:
           a) Mục tiêu.
           b) Nội dung.
           c) Sản phẩm.
           d) Tổ chức thực hiện (Gồm 4 bước: Chuyển giao, Thực hiện, Báo cáo, Kết luận).

        YÊU CẦU ĐỊNH DẠNG:
        - Sử dụng Markdown để trình bày đẹp mắt.
        - Dùng bảng (table) cho các phần so sánh hoặc hoạt động nếu cần thiết.
        - Ngôn ngữ sư phạm chuẩn mực, rõ ràng.
        """
        
        # Khởi tạo mô hình
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
        
        # Tạo ngữ cảnh hội thoại (để AI nhớ được những gì đã nói trước đó)
        chat_history = []
        for msg in st.session_state.messages:
            role = "user" if msg["role"] == "user" else "model"
            chat_history.append({"role": role, "parts": [msg["content"]]})
        
        # Bỏ qua tin nhắn cuối cùng (là prompt hiện tại) vì sẽ gửi qua hàm send_message
        chat_session = model.start_chat(history=chat_history[:-1]) 
        
        # Hiển thị trạng thái đang suy nghĩ
        with st.chat_message("assistant"):
            with st.spinner("Đang soạn giáo án... Thầy/Cô đợi một chút nhé!"):
                response = chat_session.send_message(prompt)
                st.markdown(response.text)
        
        # Lưu câu trả lời vào lịch sử
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Đã xảy ra lỗi: {e}")
