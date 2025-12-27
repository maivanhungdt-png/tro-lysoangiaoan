
import streamlit as st
import google.generativeai as genai
from PIL import Image
import tempfile
import os
import io
import re
from docx import Document
from docx.shared import Pt, RGBColor, Cm

# =========================================================
# CHUYỂN CÔNG THỨC SANG CHUẨN MASSIVEMARK (BIBCIT)
# =========================================================
def convert_math_for_massivemark(text: str) -> str:
    text = re.sub(
        r'\[MATH\](.*?)\[/MATH\]',
        lambda m: r'\(' + m.group(1).strip() + r'\)',
        text,
        flags=re.DOTALL
    )
    pattern = r'(?<!\\\()(\b(?:\\frac\{.*?\}\{.*?\}|\\sqrt\{.*?\}|[0-9a-zA-Z]+(?:\^[0-9a-zA-Z]+)?\s*(?:=|>|<|≥|≤)\s*[0-9a-zA-Z]+(?:\^[0-9a-zA-Z]+)?))'
    text = re.sub(pattern, r'\\(\1\\)', text)
    return text

# =========================================================
# XỬ LÝ CÔNG THỨC TOÁN THCS – CHUẨN SGK + MATHTYPE
# =========================================================
def auto_wrap_math(text: str) -> str:
    pattern = r'(?<!\[MATH\])(\b(?:\\frac\{.*?\}\{.*?\}|\\sqrt\{.*?\}|[0-9a-zA-Z]+(?:\^[0-9a-zA-Z]+)?\s*(?:=|>|<|≥|≤)\s*[0-9a-zA-Z]+(?:\^[0-9a-zA-Z]+)?))'
    return re.sub(pattern, r'[MATH]\1[/MATH]', text)

def process_math_blocks(text: str) -> str:
    def repl(match):
        expr = match.group(1).strip()
        expr = re.sub(r'\$(.*?)\$', r'\1', expr)
        return expr
    return re.sub(r'\[MATH\](.*?)\[/MATH\]', repl, text, flags=re.DOTALL)

# --- WORD HELPERS ---
def add_formatted_text(paragraph, text):
    # FIX: do not access paragraph.style.font directly
    paragraph.style = paragraph.part.document.styles['Normal']
    parts = re.split(r'(\*\*.*?\*\*)', text) 
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            clean = part[2:-2]
            run = paragraph.add_run(clean)
            run.bold = True
        else:
            run = paragraph.add_run(part)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)

def create_doc_stable(content, ten_bai, lop):
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(3)
    section.right_margin = Cm(1.5)

    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(14)
    style.paragraph_format.line_spacing = 1.2

    head = doc.add_heading(f'KẾ HOẠCH BÀI DẠY: {ten_bai.upper()}', 0)
    head.alignment = 1
    for run in head.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.bold = True
        run.font.color.rgb = RGBColor(0, 0, 0)

    p_lop = doc.add_paragraph(f'Lớp: {lop}')
    p_lop.alignment = 1
    p_lop.runs[0].bold = True
    doc.add_paragraph("-" * 60).alignment = 1

    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#'):
            line = line.replace('#', '').strip()

        if line.startswith('|'):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i].strip())
                i += 1
            valid_rows = [r for r in table_lines if '---' not in r]
            if len(valid_rows) >= 2:
                cols = len(valid_rows[0].split('|')) - 2
                table = doc.add_table(rows=len(valid_rows), cols=cols)
                table.style = 'Table Grid'
                for r_idx, r_text in enumerate(valid_rows):
                    cells_data = r_text.split('|')[1:-1]
                    for c_idx, cell_text in enumerate(cells_data):
                        cell = table.cell(r_idx, c_idx)
                        cell._element.clear_content()
                        raw = cell_text.strip().replace('<br>', '\n').replace('<br/>', '\n')
                        for sub in raw.split('\n'):
                            if not sub.strip():
                                continue
                            p = cell.add_paragraph()
                            if r_idx == 0:
                                p.alignment = 1
                                r = p.add_run(sub.replace('**',''))
                                r.bold = True
                            else:
                                add_formatted_text(p, sub.strip())
            continue

        if not line:
            i += 1
            continue

        if re.match(r'^(I\.|II\.|III\.|IV\.|V\.)', line) or (re.match(r'^\d+\.', line) and len(line) < 50):
            p = doc.add_paragraph(line.replace('**',''))
            p.runs[0].bold = True
            p.runs[0].font.name = 'Times New Roman'
            p.runs[0].font.size = Pt(14)
        elif line.startswith('- '):
            p = doc.add_paragraph("– ")
            add_formatted_text(p, line[2:].strip())
        else:
            p = doc.add_paragraph()
            add_formatted_text(p, line)
        i += 1

    return doc

# --- STREAMLIT UI ---
st.set_page_config(page_title="Trợ lý Giáo án NLS", page_icon="📘", layout="centered")

# ================== UI HEADER (GIỐNG BẢN CŨ) ==================
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #f4f6f9; }

    .main-header {
        background: linear-gradient(135deg, #004e92 0%, #000428 100%);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        color: white !important;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-family: 'Segoe UI', sans-serif;
        font-size: 2rem;
    }
    .main-header p {
        color: #e0e0e0 !important;
        margin-top: 10px;
        font-style: italic;
    }
    .section-header {
        color: #004e92;
        border-bottom: 2px solid #ddd;
        padding-bottom: 5px;
        margin-top: 20px;
        margin-bottom: 15px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>📘 TRỢ LÝ SOẠN GIÁO ÁN KHUNG NĂNG LỰC SỐ TỰ ĐỘNG (NLS)</h1>
    <p>Tác giả: Mai Văn Hùng - Trường THCS Đồng Yên - SĐT: 0941037116</p>
</div>
""", unsafe_allow_html=True)
# ===============================================================

FILE_KHUNG_NANG_LUC = "khungnanglucso.pdf"

st.markdown("<h1>📘 TRỢ LÝ SOẠN GIÁO ÁN</h1>", unsafe_allow_html=True)

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.text_input("Nhập API Key:", type="password")

if api_key:
    genai.configure(api_key=api_key)

uploaded_files = st.file_uploader("Tải Ảnh/PDF bài dạy:", type=["jpg","png","pdf"], accept_multiple_files=True)

output_mode = st.radio("🧮 Chọn cách xử lý công thức:", ["Word / MathType", "Copy MassiveMark (BibCit)"], index=1)
lop = st.text_input("📚 Lớp:", "Lớp 6")
ten_bai = st.text_input("📌 Tên bài học:", "")
noidung_bosung = st.text_area("✍️ Ghi chú thêm:", height=100)

if st.button("🚀 SOẠN GIÁO ÁN NGAY"):
    if not api_key:
        st.error("Thiếu API Key")
    else:
        temp_paths = []
        try:
            with st.spinner("AI đang soạn giáo án..."):
                model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-09-2025')
                prompt = f"""
Đóng vai là một Giáo viên THCS với hơn 15 năm kinh nghiệm dạy học, am hiểu chương trình GDPT 2018.
Nhiệm vụ: Soạn Kế hoạch bài dạy (Giáo án) theo Công văn 5512 cho bài: "{ten_bai}" – {lop}.

DỮ LIỆU ĐẦU VÀO:
- Các hình ảnh/PDF SGK và tài liệu đính kèm (nếu có): dùng để trích xuất CHÍNH XÁC kiến thức.
- Ghi chú bổ sung của giáo viên: "{noidung_bosung}".

YÊU CẦU BẮT BUỘC VỀ CẤU TRÚC (CÔNG VĂN 5512):
I. Mục tiêu
1. Về kiến thức
2. Về năng lực
   a) Năng lực đặc thù
   b) Năng lực chung
   c) Tích hợp năng lực số
3. Về phẩm chất

II. Thiết bị dạy học và học liệu
1. Giáo viên
2. Học sinh

III. Tiến trình dạy học
Gồm ĐÚNG 4 hoạt động:
- Hoạt động 1: Khởi động
- Hoạt động 2: Hình thành kiến thức mới
  + Hoạt động 2.1 (ứng với mục 1 SGK)
  + Hoạt động 2.2 (ứng với mục 2 SGK) (có thể thêm 2.3 nếu SGK có)
- Hoạt động 3: Luyện tập
- Hoạt động 4: Vận dụng

VỚI MỖI HOẠT ĐỘNG, TRÌNH BÀY THEO THỨ TỰ:
a) Mục tiêu
b) Nội dung
c) Sản phẩm
d) Tổ chức thực hiện (chỉ ghi dòng này, sau đó đến bảng)

SAU MỤC d) BẮT BUỘC CÓ 01 BẢNG 2 CỘT:

| Hoạt động của giáo viên và học sinh | Ghi bảng |
|---|---|
| … | … |

QUY ĐỊNH BẢNG (KHÔNG NGOẠI LỆ):
- Mỗi hoạt động chỉ có 01 bảng
- Mỗi bảng chỉ có 02 hàng
- Nội dung trong ô gộp bằng <br>
- Không dùng gạch đầu dòng tự động trong bảng

CỘT “Hoạt động của giáo viên và học sinh”:
Phải mô tả ĐẦY ĐỦ 4 BƯỚC:
Bước 1: Chuyển giao nhiệm vụ
Bước 2: Thực hiện nhiệm vụ
Bước 3: Báo cáo, thảo luận
Bước 4: Kết luận, nhận định

CỘT “Ghi bảng”:
- Ghi TOÀN BỘ kết quả kiến thức đúng SGK
- Có thể gồm: khái niệm, định nghĩa, ví dụ, bài tập, lời giải chi tiết

QUY ƯỚC CÔNG THỨC TOÁN:
- MỌI công thức toán phải đặt trong [MATH] ... [/MATH]
- Chỉ dùng LaTeX cơ bản THCS: \\frac, \\sqrt, ^
- KHÔNG dùng $, $$, \\text, \\mathbb, Unicode ² ³ √
- Không để ký hiệu =, <, >, ≥, ≤ trong văn bản thường

IV. Điều chỉnh sau tiết dạy

LƯU Ý:
- Không dùng ký tự #
- Không mô tả kết quả sư phạm
- Không lặp lại câu chữ mục tiêu
- Không bỏ trống cột “Ghi bảng”
- Bám sát SGK và tài liệu đính kèm
"""
                input_data = [prompt]

                if uploaded_files:
                    for f in uploaded_files:
                        if f.type == "application/pdf":
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                                tmp.write(f.getvalue())
                                temp_paths.append(tmp.name)
                            input_data.append(genai.upload_file(tmp.name))
                        else:
                            input_data.append(Image.open(f))

                response = model.generate_content(input_data)
                if not response or not response.text or not response.text.strip():
                    st.error("AI không sinh được nội dung.")
                    st.stop()

                ket_qua_text = response.text
                if output_mode == "Copy MassiveMark (BibCit)":
                    ket_qua_text = convert_math_for_massivemark(ket_qua_text)
                else:
                    ket_qua_text = auto_wrap_math(ket_qua_text)
                    ket_qua_text = process_math_blocks(ket_qua_text)

        except Exception as e:
            st.error(f"Có lỗi: {e}")
            st.stop()
        finally:
            for p in temp_paths:
                if os.path.exists(p):
                    os.remove(p)

        st.markdown("### 📄 KẾT QUẢ")
        st.text_area("Kết quả", ket_qua_text, height=400)

        if output_mode == "Word / MathType":
            safe = re.sub(r'[\\/:*?"<>|]', '', ten_bai) or "GiaoAn"
            doc = create_doc_stable(ket_qua_text, ten_bai, lop)
            buf = io.BytesIO()
            doc.save(buf); buf.seek(0)
            st.download_button("⬇️ Tải Word", buf, file_name=f"GiaoAn_{safe}.docx",
                               mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
