import matplotlib.pyplot as plt
import numpy as np
import math
# ===============================
# 2.2. CÁC HÀM VẼ HÌNH – THEO MÔN
# ===============================

def toan_vi_tri_duong_thang(R=5, d=3, fname="toan_hinh1.png"):
    fig, ax = plt.subplots()
    circle = plt.Circle((0, 0), R, fill=False)
    ax.add_patch(circle)
    ax.plot([-R-3, R+3], [d, d])
    ax.plot(0, 0, 'ko'); ax.text(0.1, 0.1, 'O')
    ax.set_aspect('equal')
    ax.axis('off')
    plt.savefig(fname, bbox_inches='tight')
    plt.close()
    return fname


def vatly_vector_luc(fname="vatly_luc.png"):
    fig, ax = plt.subplots()
    ax.arrow(0.2, 0.5, 0.5, 0, head_width=0.03)
    ax.text(0.75, 0.5, "F")
    ax.text(0.15, 0.5, "O")
    ax.axis('off')
    plt.savefig(fname, bbox_inches='tight')
    plt.close()
    return fname


def hoa_so_do_phan_ung(fname="hoa_phan_ung.png"):
    fig, ax = plt.subplots()
    ax.text(0.2, 0.5, "A + B")
    ax.arrow(0.35, 0.5, 0.25, 0, head_width=0.03)
    ax.text(0.65, 0.5, "C")
    ax.axis('off')
    plt.savefig(fname, bbox_inches='tight')
    plt.close()
    return fname


def sinh_te_bao(fname="sinh_te_bao.png"):
    fig, ax = plt.subplots()
    cell = plt.Circle((0.5, 0.5), 0.3, fill=False)
    nucleus = plt.Circle((0.5, 0.5), 0.1)
    ax.add_patch(cell)
    ax.add_patch(nucleus)
    ax.text(0.45, 0.5, "Nhân")
    ax.axis('off')
    plt.savefig(fname, bbox_inches='tight')
    plt.close()
    return fname


def lichsu_truc_thoi_gian(fname="lichsu_timeline.png"):
    fig, ax = plt.subplots()
    ax.plot([0, 10], [0, 0])
    ax.text(1, 0.1, "1945")
    ax.text(5, 0.1, "1975")
    ax.text(9, 0.1, "2000")
    ax.axis('off')
    plt.savefig(fname, bbox_inches='tight')
    plt.close()
    return fname
def tao_hinh_tu_noi_dung(mon, text):
    text = text.lower()

    if mon == "Toán":
        if "đường tròn" in text or "vị trí tương đối" in text:
            return toan_vi_tri_duong_thang()

    if mon == "Vật lí":
        if "lực" in text:
            return vatly_vector_luc()

    if mon == "Hóa học":
        if "phản ứng" in text:
            return hoa_so_do_phan_ung()

    if mon == "Sinh học":
        if "tế bào" in text:
            return sinh_te_bao()

    if mon == "Lịch sử":
        return lichsu_truc_thoi_gian()

    return None
