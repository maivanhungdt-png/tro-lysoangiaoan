import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import re
import io

# ===================== CONFIG =====================
st.set_page_config(page_title="Xuất giáo án Word", layout="wide")

API_KEY = st.secrets.get("GEMINI_API_KEY", "")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ===================== WORD EXPORT =====================
def create_doc_stable(content: str):
    doc = Document()

    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # ===== HOẠT ĐỘNG (chỉ Hoạt động thật: 1, 2.1, 3, 4, ...) =====
        if re.match(r'^Hoạt động\s+\d+(\.\d+)*:', line):
            p = doc.add_paragraph(line)
            p.runs[0].bold = True
            p.runs[0].font.name = 'Times New Roman'
            p.runs[0].font.size = Pt(14)

            doc.add_paragraph('a) Mục tiêu:')
            doc.add_paragraph('b) Nội dung:')
            doc.add_paragraph('c) Sản phẩm:')
            doc.add_paragraph('d) Tổ chức thực hiện:')

            i += 1
            continue

        # ===== XỬ LÝ BẢNG – ÉP HÒA Ô TRIỆT ĐỂ =====
        if line.startswith('|'):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i].strip())
                i += 1

            # Header
            header = table_lines[0]
            headers = header.split('|')[1:-1]
            cols = len(headers)

            # Body (gộp hết thành 1 dòng)
            body_lines = table_lines[2:]
            merged_cells = [''] * cols

            for r in body_lines:
                parts = r.split('|')[1:-1]
                for c in range(cols):
                    if c < len(parts):
                        txt = parts[c].strip()
                        if not txt:
                            continue

                        # CỘT HOẠT ĐỘNG: chỉ giữ các BƯỚC
                        if c == 0 and not txt.startswith('Bước'):
                            continue

                        merged_cells[c] += ('<br>' + txt if merged_cells[c] else txt)

            # Tạo bảng Word (2 hàng)
            table = doc.add_table(rows=2, cols=cols)
            table.style = 'Table Grid'
            table.autofit = True

            # Header row
            for c, h in enumerate(headers):
                cell = table.cell(0, c)
                cell._element.clear_content()
                p = cell.add_paragraph(h.strip())
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.runs[0]
                run.bold = True
                run.font.name = 'Times New Roman'
                run.font.size = Pt(13)

            # Body row
            for c, txt in enumerate(merged_cells):
                cell = table.cell(1, c)
                cell._element.clear_content()
                p = cell.add_paragraph()
                run = p.add_run(txt)
                run.font.name = 'Times New Roman'
                run.font.size = Pt(13)

            continue

        # ===== DÒNG THƯỜNG =====
        if line:
            p = doc.add_paragraph(line)
            p.runs[0].font.name = 'Times New Roman'
            p.runs[0].font.size = Pt(13)

        i += 1

    return doc


# ===================== UI =====================
st.title("📘 Tạo giáo án Word (Phần III chuẩn SGK)")

uploaded_file = st.file_uploader("Tải lên nội dung bài học / SGK (.txt)", type=["txt"])

if uploaded_file:
    sgk_text = uploaded_file.read().decode("utf-8")

    if st.button("🚀 Sinh giáo án"):
        with st.spinner("Đang tạo giáo án..."):
            prompt = f"""
Hãy soạn giáo án theo đúng mẫu SGK – SGV.
Đặc biệt chú ý PHẦN III:

- Mỗi Hoạt động phải có: a) Mục tiêu, b) Nội dung, c) Sản phẩm, d) Tổ chức thực hiện.
- Sau mục d) phải có bảng 2 cột: Hoạt động | Kết quả hoạt động.
- Cột Hoạt động chỉ gồm Bước 1 → Bước 4.
- Cột Kết quả hoạt động ghi ĐẦY ĐỦ NỘI DUNG KIẾN THỨC SGK tương ứng.
- Không ghi “HS nắm được…”.

Nội dung bài:
{sgk_text}
"""
            try:
                response = model.generate_content(prompt)
                content = response.text

                doc = create_doc_stable(content)

                buffer = io.BytesIO()
                doc.save(buffer)
                buffer.seek(0)

                st.success("Hoàn thành!")
                st.download_button(
                    "⬇️ Tải giáo án Word",
                    buffer,
                    file_name="GiaoAn.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

            except Exception as e:
                st.error(f"Lỗi khi tạo giáo án: {e}")
