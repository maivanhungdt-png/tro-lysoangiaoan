import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, Cm
import io, re

# ================== CẤU HÌNH ==================
st.set_page_config(
    page_title="Soạn giáo án CV5512 tích hợp năng lực số",
    page_icon="📘",
    layout="centered"
)

# ================== CẤU TRÚC GIÁO ÁN (GIỮ NGUYÊN) ==================
STRUCTURE = """
I. MỤC TIÊU
1. Về kiến thức
2. Về năng lực
   - Năng lực chung
   - Năng lực đặc thù
   - Năng lực số
3. Về phẩm chất

II. THIẾT BỊ DẠY HỌC VÀ HỌC LIỆU
1. Giáo viên
2. Học sinh

III. TIẾN TRÌNH DẠY HỌC

1. Hoạt động 1: Khởi động
a) Mục tiêu
b) Nội dung
c) Sản phẩm
d) Tổ chức thực hiện
| Hoạt động của giáo viên và học sinh | Ghi bảng |
|---|---|

2. Hoạt động 2: Hình thành kiến thức
a) Mục tiêu
b) Nội dung
c) Sản phẩm
d) Tổ chức thực hiện
| Hoạt động của giáo viên và học sinh | Ghi bảng |
|---|---|

3. Hoạt động 3: Luyện tập
a) Mục tiêu
b) Nội dung
c) Sản phẩm
d) Tổ chức thực hiện
| Hoạt động của giáo viên và học sinh | Ghi bảng |
|---|---|

4. Hoạt động 4: Vận dụng
a) Mục tiêu
b) Nội dung
c) Sản phẩm
d) Tổ chức thực hiện
| Hoạt động của giáo viên và học sinh | Ghi bảng |
|---|---|

IV. ĐIỀU CHỈNH SAU TIẾT DẠY
"""

# ================== HÀM WORD ==================
def create_word(content, ten_bai, lop):
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Cm(2)
    sec.bottom_margin = Cm(2)
    sec.left_margin = Cm(3)
    sec.right_margin = Cm(1.5)

    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(14)

    title = doc.add_heading(f"KẾ HOẠCH BÀI DẠY: {ten_bai.upper()}", 0)
    title.alignment = 1
    doc.add_paragraph(f"Lớp: {lop}")

    for line in content.split("\n"):
        p = doc.add_paragraph(line)
        for r in p.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(14)
    return doc

# ================== GIAO DIỆN ==================
st.title("📘 SOẠN GIÁO ÁN CV5512 – TÍCH HỢP NĂNG LỰC SỐ")

api_key = st.text_input("🔑 Gemini API Key", type="password")
if api_key:
    genai.configure(api_key=api_key)

st.header("📦 Khung năng lực số")
nls = st.multiselect(
    "Chọn các năng lực số cần tích hợp:",
    [
        "Sử dụng học liệu số",
        "Khai thác Internet an toàn",
        "Tạo sản phẩm học tập số",
        "Giao tiếp – hợp tác qua nền tảng số",
        "Ứng dụng CNTT giải quyết vấn đề"
    ]
)

st.header("📂 Tài liệu dạy học")
uploaded_files = st.file_uploader(
    "Tải SGK / tài liệu (PDF, ảnh):",
    type=["pdf", "png", "jpg"],
    accept_multiple_files=True
)

st.header("📝 Thông tin bài dạy")
lop = st.text_input("Lớp:", "Lớp 6")
ten_bai = st.text_input("Tên bài học:")

tao_tro_choi = st.checkbox("🎮 Có tạo trò chơi khởi động không?")
ghi_chu = st.text_area("Ghi chú giáo viên:", height=120)

# ================== SOẠN ==================
if st.button("🚀 SOẠN GIÁO ÁN"):
    if not api_key or not ten_bai:
        st.error("Thiếu API key hoặc tên bài")
    else:
        prompt = f"""
Bạn là giáo viên THCS.

Soạn KẾ HOẠCH BÀI DẠY theo Công văn 5512 cho:
- Bài: {ten_bai}
- Lớp: {lop}

GIỮ NGUYÊN CẤU TRÚC SAU (KHÔNG ĐƯỢC THAY ĐỔI):
{STRUCTURE}

YÊU CẦU BẮT BUỘC:
- Đúng 4 hoạt động.
- Mỗi hoạt động chỉ có 01 bảng 2 cột.
- Không tạo bảng 3 hoặc 4 cột.
- Tích hợp các NĂNG LỰC SỐ sau: {", ".join(nls) if nls else "Không yêu cầu cụ thể"}
- {"Hoạt động 1 có trò chơi khởi động" if tao_tro_choi else "Hoạt động 1 không thiết kế trò chơi"}

GHI CHÚ GIÁO VIÊN:
{ghi_chu}
"""

        model = genai.GenerativeModel("gemini-1.5-flash")
        result = model.generate_content(prompt)
        st.session_state["ga"] = result.text

# ================== KẾT QUẢ ==================
if "ga" in st.session_state:
    st.header("📄 GIÁO ÁN HOÀN CHỈNH")
    st.text_area("Nội dung:", st.session_state["ga"], height=500)

    doc = create_word(st.session_state["ga"], ten_bai, lop)
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)

    safe = re.sub(r'[\\/:*?"<>|]', '', ten_bai)
    st.download_button(
        "⬇️ Tải file Word",
        buf,
        file_name=f"GiaoAn_{safe}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
