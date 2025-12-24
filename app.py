# =========================================================
#  APP: TRỢ LÝ SOẠN GIÁO ÁN TỰ ĐỘNG (NLS)
#  Tác giả: Mai Văn Hùng – THCS Đồng Yên – 0941037116
# =========================================================

# ===== THÔNG TIN CỐ ĐỊNH =====
TEN_GIAO_VIEN = "Mai Văn Hùng"
TRUONG = "TRƯỜNG THCS ĐỒNG YÊN"
TO_CHUYEN_MON = "TỔ KHTN"
SO_DIEN_THOAI = "0941037116"
# ============================

import streamlit as st
import google.generativeai as genai
import io, re
from docx import Document
from docx.shared import Pt, Cm
from docx.oxml import OxmlElement

# =========================================================
# CHUẨN TOÁN HỌC SGK THCS
# =========================================================
SUPERSCRIPTS = {'0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'}

def _convert_power(match):
    return match.group(1) + ''.join(SUPERSCRIPTS[c] for c in match.group(2))

def _add_fraction(paragraph, num, den):
    oMathPara = OxmlElement('m:oMathPara')
    oMath = OxmlElement('m:oMath')
    frac = OxmlElement('m:f')

    for tag, text in [('m:num',num),('m:den',den)]:
        el = OxmlElement(tag)
        r = OxmlElement('m:r')
        t = OxmlElement('m:t')
        t.text = text
        r.append(t)
        el.append(r)
        frac.append(el)

    oMath.append(frac)
    oMathPara.append(oMath)
    paragraph._p.append(oMathPara)

def add_formatted_text(paragraph, text):
    paragraph.style.font.name = 'Times New Roman'
    paragraph.style.font.size = Pt(14)

    text = re.sub(r'\$(.*?)\$', r'\1', text)
    text = re.sub(r'(\d)\s*[x×]\s*(\d)', r'\1 · \2', text)
    text = re.sub(r'(\d+)\^(\d+)', _convert_power, text)
    text = re.sub(r'\\sqrt\{(\d+)\}|sqrt\((\d+)\)', r'√\1\2', text)
    text = re.sub(r'\bcota\b','cot',text,flags=re.I)
    text = re.sub(r'\b(sin|cos|tan|cot)\s*\(?\s*(\d+)\s*\)?',r'\1 \2°',text,flags=re.I)

    frac = re.search(r'(\d+)\s*/\s*(\d+)', text)
    if frac:
        before = text[:frac.start()]
        after = text[frac.end():]
        if before.strip(): paragraph.add_run(before)
        _add_fraction(paragraph, frac.group(1), frac.group(2))
        if after.strip(): paragraph.add_run(after)
        return

    paragraph.add_run(text)

# =========================================================
# TẠO FILE WORD – FIX PHẦN III
# =========================================================
def create_doc_stable(content, ten_bai, lop):
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.top_margin = sec.bottom_margin = Cm(2)
    sec.left_margin, sec.right_margin = Cm(3), Cm(1.5)

    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(14)

    # --- Header ---
    doc.add_paragraph(TRUONG).runs[0].bold = True
    doc.add_paragraph(TO_CHUYEN_MON).runs[0].bold = True
    doc.add_paragraph(f"Họ và tên giáo viên: {TEN_GIAO_VIEN} – ĐT: {SO_DIEN_THOAI}").runs[0].bold = True
    doc.add_paragraph("")

    h = doc.add_heading("KẾ HOẠCH BÀI DẠY",0); h.alignment = 1
    doc.add_paragraph(ten_bai.upper()).runs[0].bold = True
    doc.add_paragraph(f"Lớp: {lop}").runs[0].bold = True
    doc.add_paragraph("-"*60)

    # --- Nội dung ---
    lines = content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            i += 1; continue

        if line.startswith("|"):
            table_lines = []
            while i < len(lines):
                cur = lines[i].rstrip()
                if cur.strip()=="" or cur.strip().startswith("---"): break
                table_lines.append(cur)
                i += 1

            headers = table_lines[0].split("|")[1:-1]
            table = doc.add_table(rows=1, cols=len(headers))
            table.style = "Table Grid"

            for j,h in enumerate(headers):
                add_formatted_text(table.rows[0].cells[j].paragraphs[0], h.strip())

            for row in table_lines[2:]:
                cols = row.split("|")[1:-1]
                cells = table.add_row().cells
                for j,c in enumerate(cols):
                    add_formatted_text(cells[j].paragraphs[0], c.replace("<br>","\n").strip())
            continue

        p = doc.add_paragraph()
        add_formatted_text(p, line)
        i += 1

    return doc

# =========================================================
# GIAO DIỆN
# =========================================================
st.set_page_config(page_title="Trợ lý Giáo án NLS", page_icon="📘")

st.markdown(f"""
<div style="background:linear-gradient(135deg,#004e92,#000428);
padding:25px;border-radius:15px;color:white;text-align:center">
<h2>📘 TRỢ LÝ SOẠN GIÁO ÁN TỰ ĐỘNG (NLS)</h2>
<p>Tác giả: {TEN_GIAO_VIEN} – {TRUONG} – ĐT: {SO_DIEN_THOAI}</p>
</div>
""", unsafe_allow_html=True)

lop = st.text_input("Lớp:", "Lớp 6")
ten_bai = st.text_input("Tên bài học:")
noi_dung = st.text_area("Nội dung / ghi chú:")

if st.button("SOẠN GIÁO ÁN"):
    model = genai.GenerativeModel("gemini-2.0-flash")
    res = model.generate_content(noi_dung or ten_bai)
    doc = create_doc_stable(res.text, ten_bai, lop)
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    st.download_button("⬇️ Tải file Word", buf, f"GiaoAn_{ten_bai}.docx")
