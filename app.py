
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from PIL import Image
import tempfile
import os
import io
import re
from docx import Document
from docx.shared import Pt, RGBColor, Cm

# ================= CONFIG =================
st.set_page_config(
    page_title="Trợ lý Soạn Giáo Án NLS",
    page_icon="📘",
    layout="centered"
)

FILE_KHUNG_NANG_LUC = "khungnanglucso.pdf"

# ================= CSS + HEADER =================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #f4f6f9; }
.main-header {
    background: linear-gradient(135deg, #004e92 0%, #000428 100%);
    padding: 30px; border-radius: 15px; text-align: center;
    color: white; margin-bottom: 30px;
}
.main-header h1 { margin: 0; font-size: 2rem; }
.main-header p { margin-top: 10px; font-style: italic; color: #e0e0e0; }
.section-header {
    color: #004e92; border-bottom: 2px solid #ddd;
    padding-bottom: 5px; margin-top: 25px; margin-bottom: 15px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
<h1>📘 TRỢ LÝ SOẠN GIÁO ÁN KHUNG NĂNG LỰC SỐ</h1>
<p>Mai Văn Hùng – THCS Đồng Yên</p>
</div>
""", unsafe_allow_html=True)

# ================= UTILITIES =================
def convert_math_for_massivemark(text: str) -> str:
    text = re.sub(
        r'\[MATH\](.*?)\[/MATH\]',
        lambda m: r'\(' + m.group(1).strip() + r'\)',
        text,
        flags=re.DOTALL
    )
    return text

def auto_wrap_math(text: str) -> str:
    pattern = r'(?<!\[MATH\])(\b(?:\\frac\{.*?\}\{.*?\}|\\sqrt\{.*?\}|[0-9a-zA-Z]+(?:\^[0-9a-zA-Z]+)?\s*(?:=|>|<|≥|≤)\s*[0-9a-zA-Z]+))'
    return re.sub(pattern, r'[MATH]\1[/MATH]', text)

def process_math_blocks(text: str) -> str:
    def repl(m):
        return re.sub(r'\$(.*?)\$', r'\1', m.group(1).strip())
    return re.sub(r'\[MATH\](.*?)\[/MATH\]', repl, text, flags=re.DOTALL)

def add_formatted_text(paragraph, text):
    paragraph.style = paragraph.part.document.styles['Normal']
    parts = re.split(r'(\*\*.*?\*\*)', text)
    for part in parts:
        run = paragraph.add_run(part.replace('**',''))
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        if part.startswith('**') and part.endswith('**'):
            run.bold = True

def create_doc(content, ten_bai, lop):
    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Cm(21)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2)
    sec.bottom_margin = Cm(2)
    sec.left_margin = Cm(3)
    sec.right_margin = Cm(1.5)

    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(14)

    title = doc.add_heading(f"KẾ HOẠCH BÀI DẠY: {ten_bai.upper()}", 0)
    title.alignment = 1
    for r in title.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(14)
        r.bold = True

    doc.add_paragraph(f"Lớp: {lop}").runs[0].bold = True
    doc.add_paragraph("-" * 60)

    for line in content.split("\n"):
        p = doc.add_paragraph()
        add_formatted_text(p, line)

    return doc

# ================= API KEY =================
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.text_input("🔐 Nhập API Key:", type="password")

if api_key:
    genai.configure(api_key=api_key)

# ================= INPUT =================
st.markdown('<div class="section-header">📂 1. TÀI LIỆU NGUỒN</div>', unsafe_allow_html=True)

if os.path.exists(FILE_KHUNG_NANG_LUC):
    st.success("✅ Đã tích hợp khung năng lực số")
else:
    st.info("ℹ️ Chưa có khung năng lực số (khungnanglucso.pdf)")

uploaded_files = st.file_uploader(
    "Tải ảnh / PDF SGK:",
    type=["jpg","png","pdf"],
    accept_multiple_files=True
)

st.markdown('<div class="section-header">📝 2. THÔNG TIN BÀI DẠY</div>', unsafe_allow_html=True)

lop = st.text_input("📚 Lớp:", "Lớp 6")
ten_bai = st.text_input("📌 Tên bài học:")
ghi_chu = st.text_area("✍️ Ghi chú bổ sung:", height=100)

# ================= GENERATE =================
if st.button("🚀 SOẠN GIÁO ÁN NGAY"):
    if not api_key or not ten_bai.strip():
        st.error("Thiếu API Key hoặc tên bài học")
        st.stop()

    prompt = f"""
Soạn KẾ HOẠCH BÀI DẠY theo Công văn 5512 cho bài "{ten_bai}" – {lop}.

YÊU CẦU:
- ĐÚNG 4 hoạt động
- Mỗi hoạt động có bảng 2 cột
- Viết công thức trong [MATH]...[/MATH]
- Không mô tả kết quả sư phạm
- Bám sát SGK

Ghi chú giáo viên: {ghi_chu}
"""

    temp_paths = []
    with st.spinner("AI đang soạn giáo án..."):
        try:
            model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-09-2025")
            inputs = [prompt]

            for f in uploaded_files or []:
                if f.type == "application/pdf":
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(f.getvalue())
                        temp_paths.append(tmp.name)
                    inputs.append(genai.upload_file(tmp.name))
                else:
                    inputs.append(Image.open(f))

            resp = model.generate_content(inputs)
            if not resp or not resp.text:
                st.error("AI không sinh được nội dung")
                st.stop()

            text = process_math_blocks(auto_wrap_math(resp.text))
            st.session_state["result"] = text

        finally:
            for p in temp_paths:
                if os.path.exists(p):
                    os.remove(p)

# ================= OUTPUT =================
if "result" in st.session_state:
    ket_qua = st.session_state["result"]

    st.markdown('<div class="section-header">📄 KẾT QUẢ</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:white;padding:25px;">{ket_qua}</div>', unsafe_allow_html=True)

    # COPY MASSIVEMARK
    st.markdown("### 📋 COPY SANG MASSIVEMARK")
    mm_text = convert_math_for_massivemark(ket_qua)
    components.html(f"""
    <button onclick="navigator.clipboard.writeText(`{mm_text.replace('`','\\`')}`);"
    style="padding:12px 24px;font-size:16px;border-radius:8px;background:#ff9800;color:white;border:none;">
    📋 COPY MASSIVEMARK
    </button>
    """, height=80)

    # WORD
    st.markdown("### ⬇️ TẢI FILE WORD")
    safe = re.sub(r'[\\/:*?"<>|]', '', ten_bai)
    doc = create_doc(ket_qua, ten_bai, lop)
    buf = io.BytesIO()
    doc.save(buf); buf.seek(0)

    st.download_button(
        "⬇️ TẢI WORD (.docx)",
        buf,
        file_name=f"GiaoAn_{safe}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
