import streamlit as st
import google.generativeai as genai
from PIL import Image
import tempfile, os, io, re
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

# =================== CẤU HÌNH TRANG ===================
st.set_page_config(page_title="Trợ lý Giáo án NLS", page_icon="📘", layout="centered")
FILE_KHUNG_NANG_LUC = "khungnanglucso.pdf"

# =================== HÀM WORD ===================
def add_formatted_text(paragraph, text):
    parts = re.split(r'(\*\*.*?\*\*)', text)
    for part in parts:
        run = paragraph.add_run(part.replace('**',''))
        run.bold = part.startswith('**')
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)

def create_doc_stable(content, ten_bai, lop):
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.top_margin, sec.bottom_margin = Cm(2), Cm(2)
    sec.left_margin, sec.right_margin = Cm(3), Cm(1.5)

    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(14)

    h = doc.add_heading(f'KẾ HOẠCH BÀI DẠY: {ten_bai.upper()}', 0)
    h.alignment = 1
    for r in h.runs: r.bold = True

    doc.add_paragraph(f'Lớp: {lop}').alignment = 1
    doc.add_paragraph('-' * 60).alignment = 1

    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # ===== HOẠT ĐỘNG THẬT =====
        if re.match(r'^Hoạt động\s+\d+(\.\d+)*:', line):
            p = doc.add_paragraph(line)
            p.runs[0].bold = True
            for t in ['a) Mục tiêu:', 'b) Nội dung:', 'c) Sản phẩm:', 'd) Tổ chức thực hiện:']:
                doc.add_paragraph(t)
            i += 1
            continue

        # ===== BẢNG – ÉP HÒA Ô =====
        if line.startswith('|'):
            tbl = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                tbl.append(lines[i].strip())
                i += 1

            headers = tbl[0].split('|')[1:-1]
            cols = len(headers)
            merged = [''] * cols

            for r in tbl[2:]:
                cells = r.split('|')[1:-1]
                for c in range(cols):
                    if c < len(cells):
                        txt = cells[c].strip()
                        if not txt: continue
                        if c == 0 and not txt.startswith('Bước'): continue
                        merged[c] += '<br>' + txt if merged[c] else txt

            table = doc.add_table(rows=2, cols=cols)
            table.style = 'Table Grid'

            for c, htxt in enumerate(headers):
                cell = table.cell(0, c)
                cell.text = htxt.strip()
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                cell.paragraphs[0].runs[0].bold = True

            for c, txt in enumerate(merged):
                cell = table.cell(1, c)
                cell.text = txt.replace('<br>', '\n')

            continue

        if line:
            p = doc.add_paragraph()
            add_formatted_text(p, line)

        i += 1

    return doc

# =================== GIAO DIỆN (GIỮ NGUYÊN) ===================
st.markdown("""
<div style='background:linear-gradient(135deg,#004e92,#000428);
padding:30px;border-radius:15px;text-align:center;color:white'>
<h1>📘 TRỢ LÝ SOẠN GIÁO ÁN TỰ ĐỘNG (NLS)</h1>
<p>Tác giả: Mai Văn Hùng - THCS Đồng Yên</p>
</div>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("API Key:", type="password")
if api_key:
    genai.configure(api_key=api_key)

lop = st.text_input("📚 Lớp:", "Lớp 6")
ten_bai = st.text_input("📌 Tên bài học:")

if st.button("🚀 SOẠN GIÁO ÁN NGAY"):
    model = genai.GenerativeModel("gemini-1.5-flash")  # ✅ MODEL ĐÚNG
    response = model.generate_content(f"Soạn giáo án bài {ten_bai} {lop}")
    doc = create_doc_stable(response.text, ten_bai, lop)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)

    st.download_button("⬇️ TẢI FILE WORD", buf, file_name=f"GiaoAn_{ten_bai}.docx")
