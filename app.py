import streamlit as st
import google.generativeai as genai
from PIL import Image
import tempfile
import os
import io
import re
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ------------------ 1. CẤU HÌNH TRANG ------------------
st.set_page_config(
    page_title="Trợ lý Giáo án NLS",
    page_icon="📘",
    layout="centered"
)

FILE_KHUNG_NANG_LUC = "khungnanglucso.pdf"

# ------------------ 2. HÀM WORD (ỔN ĐỊNH PHẦN III) ------------------

def add_formatted_text(paragraph, text):
    paragraph.style.font.name = 'Times New Roman'
    paragraph.style.font.size = Pt(14)

    parts = re.split(r'(\*\*.*?\*\*)', text)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        else:
            run = paragraph.add_run(part)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)


def create_doc_stable(content, ten_bai, lop):
    doc = Document()

    # ---- Khổ giấy + lề ----
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

    # ---- Tiêu đề ----
    head = doc.add_heading(f'KẾ HOẠCH BÀI DẠY: {ten_bai.upper()}', 0)
    head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in head.runs:
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(0, 0, 0)

    p_lop = doc.add_paragraph(f'Lớp: {lop}')
    p_lop.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lop.runs[0].bold = True
