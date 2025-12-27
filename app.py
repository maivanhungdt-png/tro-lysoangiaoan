import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, Cm
import io
import re

# ================= CẤU HÌNH TRANG =================
st.set_page_config(
    page_title="Soạn giáo án CV5512 tích hợp năng lực số",
    page_icon="📘",
    layout="centered"
)

# ================= CẤU TRÚC GIÁO ÁN (GIỮ NGUYÊN) =================
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

# ================= HÀM TẠO WORD =================
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

    title = doc.add_heading(f"KẾ HOẠCH BÀI DẠY: {ten_bai.upper()}", level=0)
    title.alignment = 1

    p = doc.add_paragraph(f"Lớp: {lop}\n")
    p.runs[0].bold = True

    for line in content.split("\n"):
        para = doc.add_paragraph(line)
        for run in para.runs:
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)

    return doc

# ================= GIAO DIỆN =================
st.title("📘 SOẠN GIÁO ÁN CV5512 – TÍCH HỢP NĂNG LỰC SỐ")

api_key = st.text_input("🔑 Gemini API Key", type="password")
if api_key:
    genai.configure(api_key=api_key)

lop = st.text_input("Lớp:", "Lớp 6")
ten_bai = st.text_input("Tên bài học:")
ghi_chu = st.text_area("Ghi chú của giáo viên (định hướng năng lực số, học liệu số):", height=120)

# ================= SOẠN GIÁO ÁN =================
if st.button("🚀 SOẠN GIÁO ÁN"):
    if not api_key or not ten_bai.strip():
        st.error("Cần nhập API key và tên bài học.")
    else:
        prompt = f"""
Bạn là giáo viên THCS.

Hãy soạn KẾ HOẠCH BÀI DẠY theo Công văn 5512 cho bài:
- Tên bài: {ten_bai}
- Lớp: {lop}

PHẢI GIỮ NGUYÊN CẤU TRÚC SAU (KHÔNG ĐƯỢC THAY ĐỔI):
{STRUCTURE}

YÊU CẦU BẮT BUỘC:
- Đúng 4 hoạt động.
- Mỗi hoạt động chỉ có 01 bảng 2 cột: Hoạt động GV–HS | Ghi bảng.
- Không tạo bảng 3 hoặc 4 cột.
- Tích hợp rõ NĂNG LỰC SỐ trong mục Mục tiêu và trong hoạt động học.
- Viết giáo án đầy đủ, dùng được nộp hồ sơ.

Ghi chú giáo viên:
{ghi_chu}
"""

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        ket_qua = response.text
        st.session_state["result"] = ket_qua

# ================= HIỂN THỊ & XUẤT =================
if "result" in st.session_state:
    st.markdown("## 📄 GIÁO ÁN HOÀN CHỈNH")
    st.text_area("Nội dung giáo án:", st.session_state["result"], height=500)

    # Xuất Word
    doc = create_word(st.session_state["result"], ten_bai, lop)
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)

    safe_name = re.sub(r'[\\/:*?"<>|]', '', ten_bai)
    st.download_button(
        "⬇️ Tải file Word (.docx)",
        buf,
        file_name=f"GiaoAn_{safe_name}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
