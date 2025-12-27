
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from PIL import Image
import tempfile
import os
import io
import re
from docx import Document
from docx.shared import Pt, Cm

# ===================== CẤU TRÚC GIÁO ÁN CV5512 (CỐ ĐỊNH) =====================
GIAO_AN_CV5512 = """
I. Mục tiêu
1. Về kiến thức
2. Về năng lực
   a) Năng lực đặc thù
   b) Năng lực chung
   c) Năng lực số
3. Về phẩm chất

II. Thiết bị dạy học và học liệu
1. Giáo viên
2. Học sinh

III. Tiến trình dạy học

1. Hoạt động 1: Khởi động
a) Mục tiêu
b) Nội dung
c) Sản phẩm
d) Tổ chức thực hiện
| Hoạt động của giáo viên và học sinh | Ghi bảng |
|---|---|
| … | … |

2. Hoạt động 2: Hình thành kiến thức mới
2.1. Hoạt động 2.1
a) Mục tiêu
b) Nội dung
c) Sản phẩm
d) Tổ chức thực hiện
| Hoạt động của giáo viên và học sinh | Ghi bảng |
|---|---|
| … | … |

2.2. Hoạt động 2.2
a) Mục tiêu
b) Nội dung
c) Sản phẩm
d) Tổ chức thực hiện
| Hoạt động của giáo viên và học sinh | Ghi bảng |
|---|---|
| … | … |

3. Hoạt động 3: Luyện tập
a) Mục tiêu
b) Nội dung
c) Sản phẩm
d) Tổ chức thực hiện
| Hoạt động của giáo viên và học sinh | Ghi bảng |
|---|---|
| … | … |

4. Hoạt động 4: Vận dụng
a) Mục tiêu
b) Nội dung
c) Sản phẩm
d) Tổ chức thực hiện
| Hoạt động của giáo viên và học sinh | Ghi bảng |
|---|---|
| … | … |

IV. Điều chỉnh sau tiết dạy
"""

# ===================== CẤU HÌNH TRANG =====================
st.set_page_config(page_title="Trợ lý Soạn Giáo Án CV5512", page_icon="📘", layout="centered")

# ===================== GIAO DIỆN =====================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {background:#f4f6f9;}
.header {
background:linear-gradient(135deg,#004e92,#000428);
padding:25px;border-radius:15px;color:white;text-align:center;
margin-bottom:25px;
}
.section{color:#004e92;font-weight:bold;margin-top:25px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
<h1>📘 TRỢ LÝ SOẠN GIÁO ÁN CV5512</h1>
<p>Soạn đúng cấu trúc – Xuất Word – Copy MassiveMark</p>
</div>
""", unsafe_allow_html=True)

# ===================== TIỆN ÍCH =====================
def auto_wrap_math(text):
    pattern = r'(?<!\\[MATH\\])([0-9a-zA-Z]+\\s*(=|>|<|≥|≤)\\s*[0-9a-zA-Z]+)'
    return re.sub(pattern, r'[MATH]\\1[/MATH]', text)

def convert_massive(text):
    return re.sub(r'\\[MATH\\](.*?)\\[/MATH\\]', lambda m: f"\\({m.group(1)}\\)", text)

def create_word(content, ten_bai, lop):
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = sec.bottom_margin = Cm(2)
    sec.left_margin = Cm(3)
    sec.right_margin = Cm(1.5)

    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(14)

    title = doc.add_heading(f"KẾ HOẠCH BÀI DẠY: {ten_bai.upper()}", 0)
    title.alignment = 1
    for r in title.runs:
        r.bold = True

    doc.add_paragraph(f"Lớp: {lop}")
    doc.add_paragraph("-"*50)

    for line in content.split("\\n"):
        p = doc.add_paragraph(line)
        for r in p.runs:
            r.font.name='Times New Roman'
            r.font.size=Pt(14)

    return doc

# ===================== API KEY =====================
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.text_input("🔑 Nhập Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)

# ===================== NHẬP LIỆU =====================
st.markdown('<div class="section">📂 Tài liệu</div>', unsafe_allow_html=True)
files = st.file_uploader("Tải ảnh/PDF SGK (nếu có)", type=["jpg","png","pdf"], accept_multiple_files=True)

st.markdown('<div class="section">📝 Thông tin bài dạy</div>', unsafe_allow_html=True)
lop = st.text_input("Lớp:", "Lớp 6")
ten_bai = st.text_input("Tên bài học:")
ghi_chu = st.text_area("Ghi chú giáo viên:", height=100)

# ===================== SOẠN GIÁO ÁN =====================
if st.button("🚀 SOẠN GIÁO ÁN"):
    if not api_key or not ten_bai:
        st.error("Thiếu API key hoặc tên bài")
        st.stop()

    prompt = f"""
Bạn là giáo viên THCS giàu kinh nghiệm.

Hãy soạn KẾ HOẠCH BÀI DẠY theo Công văn 5512 cho:
Bài: {ten_bai} – {lop}

CẤU TRÚC BẮT BUỘC:
{GIAO_AN_CV5512}

YÊU CẦU:
- Giữ nguyên cấu trúc
- ĐÚNG 4 hoạt động
- Mỗi hoạt động có 1 bảng 2 cột
- Công thức đặt trong [MATH]...[/MATH]
- Không mô tả kết quả sư phạm

Ghi chú giáo viên:
{ghi_chu}
"""

    temp = []
    with st.spinner("Đang soạn giáo án..."):
        try:
            model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-09-2025")
            inputs=[prompt]
            for f in files or []:
                if f.type=="application/pdf":
                    with tempfile.NamedTemporaryFile(delete=False,suffix=".pdf") as tmp:
                        tmp.write(f.getvalue())
                        temp.append(tmp.name)
                    inputs.append(genai.upload_file(tmp.name))
                else:
                    inputs.append(Image.open(f))
            r = model.generate_content(inputs)
            result = auto_wrap_math(r.text)
            st.session_state["ga"] = result
        finally:
            for p in temp:
                if os.path.exists(p): os.remove(p)

# ===================== XUẤT KẾT QUẢ =====================
if "ga" in st.session_state:
    ga = st.session_state["ga"]
    st.markdown('<div class="section">📄 Giáo án</div>', unsafe_allow_html=True)
    st.text_area("Nội dung giáo án", ga, height=400)

    # Copy MassiveMark
    mm = convert_massive(ga)
    components.html(f"""
    <button onclick="navigator.clipboard.writeText(`{mm.replace('`','')}`)"
    style="padding:12px 20px;background:#ff9800;color:white;border:none;border-radius:8px;">
    📋 COPY SANG MASSIVEMARK
    </button>
    """, height=80)

    # Word
    doc = create_word(ga, ten_bai, lop)
    buf = io.BytesIO()
    doc.save(buf); buf.seek(0)
    safe = re.sub(r'[\\\\/:*?"<>|]', '', ten_bai)
    st.download_button("⬇️ TẢI FILE WORD", buf,
        file_name=f"GiaoAn_{safe}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
