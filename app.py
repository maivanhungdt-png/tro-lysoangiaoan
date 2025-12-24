# =========================================================
# TRỢ LÝ SOẠN GIÁO ÁN TỰ ĐỘNG (NLS)
# Tác giả: Mai Văn Hùng – THCS Đồng Yên – Tổ KHTN
# ĐT: 0941037116
# =========================================================

# ===== THÔNG TIN CỐ ĐỊNH =====
TEN_GIAO_VIEN = "Mai Văn Hùng"
TRUONG = "TRƯỜNG THCS ĐỒNG YÊN"
TO_CHUYEN_MON = "TỔ KHTN"
SO_DIEN_THOAI = "0941037116"
# ============================

import streamlit as st
import google.generativeai as genai
import io, re, tempfile, os
from docx import Document
from docx.shared import Pt, Cm
from docx.oxml import OxmlElement

# =========================================================
# CHUẨN TOÁN HỌC SGK THCS
# =========================================================
SUPERSCRIPTS = {
    '0':'⁰','1':'¹','2':'²','3':'³','4':'⁴',
    '5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'
}

def _convert_power(match):
    return match.group(1) + ''.join(SUPERSCRIPTS[c] for c in match.group(2))

def _add_fraction(paragraph, num, den):
    oMathPara = OxmlElement('m:oMathPara')
    oMath = OxmlElement('m:oMath')
    frac = OxmlElement('m:f')

    num_el = OxmlElement('m:num')
    num_r = OxmlElement('m:r')
    num_t = OxmlElement('m:t')
    num_t.text = num
    num_r.append(num_t)
    num_el.append(num_r)

    den_el = OxmlElement('m:den')
    den_r = OxmlElement('m:r')
    den_t = OxmlElement('m:t')
    den_t.text = den
    den_r.append(den_t)
    den_el.append(den_r)

    frac.append(num_el)
    frac.append(den_el)
    oMath.append(frac)
    oMathPara.append(oMath)
