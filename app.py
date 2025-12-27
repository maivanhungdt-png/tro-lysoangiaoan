import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, Cm
from PyPDF2 import PdfReader
import io
import os
import re

# ================== CẤU HÌNH TRANG ==================
st.set_page_config(
    page_title="Soạn giáo án CV5512 tích hợp năng lực số",
    page_icon="📘",
    layout="centered"
)

# ================== HẰNG SỐ ==================
FILE_KHUNG_NLS = "khung_nang_luc_so.pdf"

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

# ================== HÀM ĐỌC KHUNG NLS ==================
def read_khung_nls(path):
    if not os.path.exists(path):
        return None
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()

# ================== HÀM TẠO WORD ==================
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

    p = doc.add_paragraph(f"Lớp: {lop}")
    p.runs[0].bold = True

    for line in content.split("\n"):
        para = doc.add_paragraph(line)
        for run in para.runs:
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)

    return doc

# ================== GIAO DIỆN ==================
st.title("📘 SOẠN GIÁO ÁN CV5512 – TÍCH HỢP NĂNG LỰC SỐ")

# ===== API KEY =====
api_key = st.text_input("🔑 Gemini API Key", type="password")
if api_key:
    genai.configure(api_key=api_key)

# ===== KHUNG NĂNG LỰC SỐ =====
st.header("📦 Khung năng lực số")

khung_nls_text = read_khung_nls(FILE_KHUNG_NLS)
has_nls = khung_nls_text is not None

if has_nls:
    st.success(f"✅ Đã tự động tích hợp file: {FILE_KHUNG_NLS}")
    with st.expander("📘 Xem nội dung khung năng lực số"):
        st.text_area("Nội dung:", khung_nls_text, height=300)
else:
    st.warning("⚠️ Chưa tìm thấy file khung_nang_luc_so.pdf")

# ===== TÀI LIỆU =====
st.header("📂 Tài liệu dạy học (SGK, học liệu)")
uploaded_files = st.file_uploader(
    "Tải ảnh / PDF bài dạy:",
    type=["pdf", "png", "jpg"],
    accept_multiple_files=True
)

# ===== THÔNG TIN BÀI DẠY =====
st.header("📝 Thông tin bài dạy")
lop = st.text_input("Lớp:", "Lớp 6")
ten_bai = st.text_input("Tên bài học:")
tao_tro_choi = st.checkbox("🎮 Có tạo trò chơi khởi động không?")
ghi_chu = st.text_area("Ghi chú của giáo viên:", height=120)

# ================== SOẠN GIÁO ÁN ==================
if st.button("🚀 SOẠN GIÁO ÁN"):
    if not api_key or not ten_bai.strip():
        st.error("Vui lòng nhập API key và tên bài học.")
    else:
        prompt = f"""
Bạn là giáo viên THCS.

Hãy soạn KẾ HOẠCH BÀI DẠY theo Công văn 5512 cho:
- Bài học: {ten_bai}
- Lớp: {lop}

PHẢI GIỮ NGUYÊN CẤU TRÚC SAU (KHÔNG ĐƯỢC THAY ĐỔI):
{STRUCTURE}

YÊU CẦU BẮT BUỘC:
- Đúng 4 hoạt động.
- Mỗi hoạt động chỉ có 01 bảng 2 cột (Hoạt động GV–HS | Ghi bảng).
- Không tạo bảng 3 hoặc 4 cột.
- {"Hoạt động 1 có trò chơi khởi động" if tao_tro_choi else "Hoạt động 1 không thiết kế trò chơi"}.

KHUNG NĂNG LỰC SỐ ÁP DỤNG:
{khung_nls_text if has_nls else "Không có file khung năng lực số"}

GHI CHÚ GIÁO VIÊN:
{ghi_chu}
"""

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        st.session_state["result"] = response.text

# ================== KẾT QUẢ & XUẤT ==================
if "result" in st.session_state:
    st.header("📄 GIÁO ÁN HOÀN CHỈNH")
    st.text_area("Nội dung:", st.session_state["result"], height=500)

    doc = create_word(st.session_state["result"], ten_bai, lop)
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)

    safe = re.sub(r'[\\/:*?"<>|]', '', ten_bai)
    st.download_button(
        "⬇️ Tải file Word (.docx)",
        buf,
        file_name=f"GiaoAn_{safe}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
