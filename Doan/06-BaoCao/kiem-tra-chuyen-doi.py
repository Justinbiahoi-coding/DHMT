#!/usr/bin/env python3
"""Kiểm tra file .docx có đủ nội dung của file .md nguồn không.

Dùng: python3 kiem-tra-chuyen-doi.py bao-cao.md bao-cao.docx

Kiểm tra 5 việc:
  1. File .docx đọc được, cấu trúc ZIP hợp lệ
  2. Mọi dòng văn bản trong .md đều xuất hiện trong .docx
  3. Không có thẻ HTML hay chú thích bị in thành chữ
  4. Số bảng và số hình khớp giữa hai file
  5. Không còn dấu hiệu văn AI (gạch ngang dài, nháy cong)
"""
import html
import os
import re
import sys
import zipfile

NS_TABLE = "<w:tbl>"
NS_IMAGE = "<w:drawing>"


def doc_text(docx_path):
    z = zipfile.ZipFile(docx_path)
    if z.testzip() is not None:
        raise ValueError("File .docx hỏng")
    required = ["[Content_Types].xml", "_rels/.rels", "word/document.xml"]
    thieu = [r for r in required if r not in z.namelist()]
    if thieu:
        raise ValueError(f"Thiếu thành phần bắt buộc: {thieu}")
    xml = z.read("word/document.xml").decode("utf8")
    text = html.unescape(re.sub(r"<[^>]+>", "", xml.replace("</w:p>", "\n")))
    return xml, text


def chuan_hoa(s):
    return re.sub(r"\s+", " ", s).strip()


def main(md_path, docx_path):
    loi, canh_bao = [], []

    xml, text = doc_text(docx_path)
    text_norm = chuan_hoa(text)
    md = open(md_path, encoding="utf-8").read()

    # 2. Mọi dòng nội dung của .md phải có trong .docx
    md_khong_comment = re.sub(r"<!--[\s\S]*?-->", "", md)
    thieu = []
    trong_code = False
    for n, dong in enumerate(md_khong_comment.split("\n"), 1):
        t = dong.strip()
        if t.startswith("```"):
            trong_code = not trong_code
            continue
        if trong_code or not t:
            continue
        if re.fullmatch(r"\|?[\s:\-|]+\|?", t) or re.fullmatch(r"-{3,}", t):
            continue
        # Bỏ ký hiệu đầu dòng của danh sách: Word tự sinh số và dấu chấm tròn,
        # nên chúng không nằm trong phần text của .docx
        t_probe = re.sub(r"^\s*>\s?", "", t)
        t_probe = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", t_probe)
        # Bỏ ký hiệu markdown, thay bằng rỗng để không sinh khoảng trắng thừa
        plain = chuan_hoa(re.sub(r"[*`#|]|<br\s*/?>", "", t_probe))
        if len(plain) < 8:
            continue
        if plain[:40] not in text_norm:
            thieu.append(f"dòng {n}: {t[:60]}")
    if thieu:
        loi.append(f"{len(thieu)} dòng không có trong .docx")
        loi.extend("    " + x for x in thieu[:10])

    # 3. Thẻ HTML hoặc chú thích bị in thành chữ
    # Không dò "-->" riêng lẻ: sơ đồ ASCII hợp lệ có thể chứa mũi tên "--->",
    # chuỗi này mang "-->" như chuỗi con nên gây báo động giả. Một chú thích
    # <!-- --> bị rò rỉ luôn kéo theo dấu mở "<!--" lộ ra cùng, nên chỉ cần dò
    # dấu mở là đủ phát hiện rò rỉ thật.
    for mau in ["<br", "<!--", "</"]:
        if mau in text:
            loi.append(f"Thẻ {mau!r} bị in thành chữ trong .docx ({text.count(mau)} lần)")

    # 4. Số bảng và số hình
    # Dòng phân cách của bảng phải chứa ít nhất một dấu | (tránh đếm nhầm đường kẻ ---)
    so_bang_md = len([
        d for d in md_khong_comment.split("\n")
        if "|" in d and re.fullmatch(r"\s*\|?[\s:\-|]+\|?\s*", d) and "-" in d
    ])
    so_bang_docx = xml.count(NS_TABLE)
    if so_bang_md != so_bang_docx:
        canh_bao.append(f"Số bảng lệch: .md có {so_bang_md}, .docx có {so_bang_docx}")

    so_anh_md = len(re.findall(r"!\[[^\]]*\]\([^)]+\)", md_khong_comment))
    so_anh_docx = xml.count(NS_IMAGE)
    if so_anh_md != so_anh_docx:
        canh_bao.append(f"Số hình lệch: .md có {so_anh_md}, .docx nhúng {so_anh_docx}")

    # 5. Dấu hiệu văn AI
    for ten, mau in [("gạch ngang dài", r"[—–]"), ("nháy cong", r"[“”]")]:
        n = len(re.findall(mau, text))
        if n:
            canh_bao.append(f"Còn {n} {ten} trong .docx")

    # Báo cáo
    kb = round(os.path.getsize(docx_path) / 1024, 1)
    print(f"Nguồn:  {md_path}")
    print(f"Đích:   {docx_path}  ({kb} KB)")
    print(f"Bảng:   {so_bang_docx} | Hình: {so_anh_docx}")
    print()
    for x in loi:
        print("LỖI    ", x)
    for x in canh_bao:
        print("CẢNH BÁO", x)
    if not loi and not canh_bao:
        print("Đạt. Không phát hiện mất mát nội dung.")
    return 1 if loi else 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
