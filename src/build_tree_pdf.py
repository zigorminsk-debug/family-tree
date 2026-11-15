#!/usr/bin/env python3
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "family_tree.json"
FONTS_DIR = ROOT / "fonts"
OUT_PDF = ROOT / "Rodovoe_Drevo_Zaharevich_Bunel.pdf"

W_P, H_P = A4             # 595.27 x 841.89 pt (Portrait)
W_L, H_L = landscape(A4)  # 841.89 x 595.27 pt (Landscape)
TOTAL_PAGES = 8

# Archival Botanical Color Palette
PARCHMENT = colors.HexColor("#FAF6EC")
CARD_BG = colors.HexColor("#FFFDF8")
CARD_BG_SOFT = colors.HexColor("#F5EFE2")
INK = colors.HexColor("#223024")
INK_MUTED = colors.HexColor("#596557")
INK_SOFT = colors.HexColor("#776B5D")

FOREST_DEEP = colors.HexColor("#2D4F38")
SAGE_MID = colors.HexColor("#5B7D59")
SAGE_LIGHT = colors.HexColor("#8CA67B")
CANOPY_WASH_1 = colors.HexColor("#E8EFE1")
CANOPY_WASH_2 = colors.HexColor("#DCE6D3")
CANOPY_WASH_3 = colors.HexColor("#CFDDC4")

BARK_DARK = colors.HexColor("#634530")
BARK_MID = colors.HexColor("#7E5B40")
BARK_LIGHT = colors.HexColor("#9C7A5C")
SOIL_LIGHT = colors.HexColor("#E6DEC8")
SOIL_DARK = colors.HexColor("#C5B494")

GOLD = colors.HexColor("#AC8542")
GOLD_LIGHT = colors.HexColor("#E9D9B5")
GOLD_BG = colors.HexColor("#FBF5E6")

PATERNAL_ACCENT = colors.HexColor("#9D5E41")
PATERNAL_BG = colors.HexColor("#FBF2EC")
PATERNAL_BORDER = colors.HexColor("#D8B7A6")

MARUNOV_ACCENT = colors.HexColor("#784F5E")
MARUNOV_BG = colors.HexColor("#F8EFF2")
MARUNOV_BORDER = colors.HexColor("#CEB2BC")

MATERNAL_ACCENT = colors.HexColor("#3A685E")
MATERNAL_BG = colors.HexColor("#EEF5F2")
MATERNAL_BORDER = colors.HexColor("#A9C6BE")

CLUE_BORDER = colors.HexColor("#9E9281")
CLUE_BG = colors.HexColor("#F6F2E8")
RULE_LINE = colors.HexColor("#D8CEB8")


def register_fonts():
    font_map = {
        "Cormorant-Regular": FONTS_DIR / "CormorantGaramond-Regular.ttf",
        "Cormorant-SemiBold": FONTS_DIR / "CormorantGaramond-SemiBold.ttf",
        "Cormorant-Bold": FONTS_DIR / "CormorantGaramond-Bold.ttf",
        "Cormorant-Italic": FONTS_DIR / "CormorantGaramond-Italic.ttf",
        "Lora-Regular": FONTS_DIR / "Lora-Regular.ttf",
        "Lora-SemiBold": FONTS_DIR / "Lora-SemiBold.ttf",
        "Lora-Bold": FONTS_DIR / "Lora-Bold.ttf",
        "Lora-Italic": FONTS_DIR / "Lora-Italic.ttf",
        "PTSans-Regular": FONTS_DIR / "PT_Sans-Web-Regular.ttf",
        "PTSans-Bold": FONTS_DIR / "PT_Sans-Web-Bold.ttf",
        "PTSans-Italic": FONTS_DIR / "PT_Sans-Web-Italic.ttf",
    }
    for name, path in font_map.items():
        pdfmetrics.registerFont(TTFont(name, str(path)))


def wrap_text(text, font_name, font_size, max_width):
    if not text:
        return []
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else f"{cur} {word}"
        if pdfmetrics.stringWidth(trial, font_name, font_size) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_font_for_lines(lines_source, font_name, base_size, max_width, min_size=5.4):
    """Shrink font size if any individual word exceeds max_width."""
    sz = base_size
    words = [w for w in lines_source.split() if w]
    if not words:
        return sz
    while sz > min_size:
        if all(pdfmetrics.stringWidth(w, font_name, sz) <= max_width for w in words):
            break
        sz -= 0.25
    return sz


def draw_centered_wrapped(c, text, cx, top_y, font_name, font_size, max_width, leading, color=INK):
    c.saveState()
    sz = fit_font_for_lines(text, font_name, font_size, max_width)
    adj_leading = leading * (sz / font_size) if sz < font_size else leading
    c.setFont(font_name, sz)
    c.setFillColor(color)
    lines = wrap_text(text, font_name, sz, max_width)
    y = top_y
    for line in lines:
        c.drawCentredString(cx, y, line)
        y -= adj_leading
    c.restoreState()
    return y


def draw_left_wrapped(c, text, x, top_y, font_name, font_size, max_width, leading, color=INK):
    c.saveState()
    sz = fit_font_for_lines(text, font_name, font_size, max_width)
    c.setFont(font_name, sz)
    c.setFillColor(color)
    lines = wrap_text(text, font_name, sz, max_width)
    y = top_y
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    c.restoreState()
    return y


def draw_leaf(c, x, y, angle_deg, length, width, fill_color, stroke_color=None, vein=True, alpha=1.0):
    c.saveState()
    c.translate(x, y)
    c.rotate(angle_deg)
    if alpha < 1.0:
        c.setFillAlpha(alpha)
        c.setStrokeAlpha(alpha)
    p = c.beginPath()
    p.moveTo(0, 0)
    p.curveTo(length * 0.35, width * 0.65, length * 0.72, width * 0.52, length, 0)
    p.curveTo(length * 0.72, -width * 0.52, length * 0.35, -width * 0.65, 0, 0)
    p.close()
    c.setFillColor(fill_color)
    if stroke_color:
        c.setStrokeColor(stroke_color)
        c.setLineWidth(0.6)
        c.drawPath(p, stroke=1, fill=1)
    else:
        c.drawPath(p, stroke=0, fill=1)
    if vein:
        c.setStrokeColor(stroke_color or FOREST_DEEP)
        c.setStrokeAlpha(min(alpha, 0.45))
        c.setLineWidth(0.5)
        c.line(length * 0.08, 0, length * 0.85, 0)
    c.restoreState()


def draw_corner_sprig(c, x, y, sx=1, sy=1):
    c.saveState()
    c.translate(x, y)
    c.scale(sx, sy)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.0)
    p = c.beginPath()
    p.moveTo(0, 0)
    p.curveTo(12, -4, 24, -12, 34, -26)
    c.drawPath(p, stroke=1, fill=0)
    draw_leaf(c, 8, -3, -25, 13, 6, SAGE_LIGHT, FOREST_DEEP, alpha=0.85)
    draw_leaf(c, 19, -10, -45, 12, 5.5, SAGE_MID, FOREST_DEEP, alpha=0.85)
    draw_leaf(c, 28, -19, -70, 11, 5, GOLD_LIGHT, GOLD, alpha=0.95)
    c.setFillColor(GOLD)
    c.circle(35, -28, 2.0, stroke=0, fill=1)
    c.restoreState()


def draw_page_background(c, w, h, page_num=None, total_pages=TOTAL_PAGES, header_title=None):
    c.setFillColor(PARCHMENT)
    c.rect(0, 0, w, h, stroke=0, fill=1)

    m = 20
    c.setStrokeColor(RULE_LINE)
    c.setLineWidth(0.8)
    c.rect(m, m, w - 2 * m, h - 2 * m, stroke=1, fill=0)

    c.setStrokeColor(GOLD)
    c.setLineWidth(0.45)
    c.rect(m + 4, m + 4, w - 2 * (m + 4), h - 2 * (m + 4), stroke=1, fill=0)

    if header_title:
        c.setFont("PTSans-Bold", 7.5)
        c.setFillColor(INK_MUTED)
        c.drawString(34, h - 38, header_title.upper())
        c.setFont("Lora-Italic", 8.5)
        c.drawRightString(w - 34, h - 38, "Род Захаревич и Бунель")
        c.setStrokeColor(RULE_LINE)
        c.setLineWidth(0.6)
        c.line(34, h - 44, w - 34, h - 44)

    if page_num is not None:
        c.setStrokeColor(RULE_LINE)
        c.setLineWidth(0.5)
        c.line(34, 38, w - 34, 38)
        c.setFont("PTSans-Regular", 7.8)
        c.setFillColor(INK_SOFT)
        c.drawString(34, 28, "Семейный генеалогический альбом · Минская и Смоленская обл. · НИАБ, ГАМн, ГАСО, ЦАМО")
        c.drawRightString(w - 34, 28, f"Страница {page_num} из {total_pages}")


def draw_ornamental_divider(c, cx, y, width=220):
    c.saveState()
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.line(cx - width / 2, y, cx - 18, y)
    c.line(cx + 18, y, cx + width / 2, y)
    draw_leaf(c, cx - 2, y, 155, 11, 5, SAGE_LIGHT, FOREST_DEEP, vein=False)
    draw_leaf(c, cx + 2, y, 25, 11, 5, SAGE_LIGHT, FOREST_DEEP, vein=False)
    c.setFillColor(GOLD)
    c.circle(cx, y, 2.2, stroke=0, fill=1)
    c.restoreState()


def draw_cover_emblem(c, cx, cy):
    c.saveState()
    c.setFillColor(CANOPY_WASH_1)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.circle(cx, cy, 82, stroke=1, fill=1)

    c.setStrokeColor(SAGE_MID)
    c.setLineWidth(0.5)
    c.circle(cx, cy, 76, stroke=1, fill=0)

    c.setFillColor(CANOPY_WASH_2)
    c.circle(cx - 21, cy + 17, 33, stroke=0, fill=1)
    c.circle(cx + 21, cy + 17, 33, stroke=0, fill=1)
    c.circle(cx, cy + 31, 37, stroke=0, fill=1)

    c.setStrokeColor(BARK_MID)
    c.setLineCap(1)
    for dx, ctrl_x, end_y in [(-32, -14, -57), (-14, -5, -62), (14, 5, -62), (32, 14, -57)]:
        c.setLineWidth(2.2 if abs(dx) < 20 else 1.5)
        p = c.beginPath()
        p.moveTo(cx, cy - 37)
        p.curveTo(cx + ctrl_x, cy - 49, cx + dx * 0.7, cy - 55, cx + dx, cy + end_y)
        c.drawPath(p, stroke=1, fill=0)

    p = c.beginPath()
    p.moveTo(cx - 7.5, cy - 40)
    p.curveTo(cx - 4.5, cy - 13, cx - 4.5, cy + 5, cx - 2.8, cy + 14)
    p.lineTo(cx + 2.8, cy + 14)
    p.curveTo(cx + 4.5, cy + 5, cx + 4.5, cy - 13, cx + 7.5, cy - 40)
    p.close()
    c.setFillColor(BARK_DARK)
    c.drawPath(p, stroke=0, fill=1)

    branches = [
        (0, 6, -21, 19, -43, 30, 3.0),
        (0, 6, 21, 19, 43, 30, 3.0),
        (0, 11, -10, 30, -23, 50, 2.3),
        (0, 11, 10, 30, 23, 50, 2.3),
        (0, 13, 0, 34, 0, 58, 2.1),
        (-24, 21, -39, 12, -50, 6, 1.5),
        (24, 21, 39, 12, 50, 6, 1.5),
    ]
    c.setStrokeColor(BARK_DARK)
    for x0, y0, cx1, cy1, x1, y1, lw in branches:
        c.setLineWidth(lw)
        pb = c.beginPath()
        pb.moveTo(cx + x0, cy + y0)
        pb.curveTo(cx + cx1, cy + cy1, cx + (cx1 + x1) * 0.5, cy + y1 - 4, cx + x1, cy + y1)
        c.drawPath(pb, stroke=1, fill=0)

    leaves = [
        (-46, 30, 145, 16, 7.2, FOREST_DEEP),
        (-37, 41, 118, 15, 6.8, SAGE_MID),
        (-23, 50, 102, 16, 7.2, FOREST_DEEP),
        (-10, 57, 92, 15, 6.8, SAGE_LIGHT),
        (0, 60, 90, 17, 7.6, FOREST_DEEP),
        (10, 57, 88, 15, 6.8, SAGE_LIGHT),
        (23, 50, 78, 16, 7.2, FOREST_DEEP),
        (37, 41, 62, 15, 6.8, SAGE_MID),
        (46, 30, 35, 16, 7.2, FOREST_DEEP),
        (-50, 8, 168, 14, 6.2, SAGE_MID),
        (50, 8, 12, 14, 6.2, SAGE_MID),
        (-31, 18, 130, 13, 5.8, SAGE_LIGHT),
        (31, 18, 50, 13, 5.8, SAGE_LIGHT),
        (-14, 33, 112, 14, 6.2, SAGE_MID),
        (14, 33, 68, 14, 6.2, SAGE_MID),
    ]
    for lx, ly, ang, ln, wd, col in leaves:
        draw_leaf(c, cx + lx, cy + ly, ang, ln, wd, col, FOREST_DEEP, alpha=0.92)

    for bx, by in [(-43, 32), (-23, 52), (0, 62), (23, 52), (43, 32)]:
        c.setFillColor(GOLD)
        c.circle(cx + bx, cy + by, 2.5, stroke=0, fill=1)

    c.restoreState()


def build_page_1_cover(c, data):
    draw_page_background(c, W_P, H_P, page_num=1, total_pages=TOTAL_PAGES, header_title=None)

    draw_corner_sprig(c, 32, H_P - 32, 1, 1)
    draw_corner_sprig(c, W_P - 32, H_P - 32, -1, 1)

    cx = W_P / 2
    c.setFont("PTSans-Bold", 9)
    c.setFillColor(GOLD)
    c.drawCentredString(cx, H_P - 78, "СЕМЕЙНЫЙ ГЕНЕАЛОГИЧЕСКИЙ АЛЬБОМ")

    c.setFont("Cormorant-Bold", 33)
    c.setFillColor(FOREST_DEEP)
    c.drawCentredString(cx, H_P - 115, "РОДОСЛОВНАЯ КНИГА")

    draw_ornamental_divider(c, cx, H_P - 133, width=260)

    c.setFont("Cormorant-SemiBold", 23)
    c.setFillColor(INK)
    c.drawCentredString(cx, H_P - 164, "Род Захаревич и Бунель")

    draw_centered_wrapped(
        c,
        "с ветвями Хмыз, Адамович, Марунов и Винничек · Минская и Смоленская области",
        cx,
        H_P - 186,
        "Lora-Italic",
        11.0,
        W_P - 108,
        14,
        color=INK_MUTED,
    )

    draw_cover_emblem(c, cx, 540)

    # Family Summary Box
    bx, by, bw, bh = 50, 240, W_P - 100, 198
    c.setFillColor(CARD_BG)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.0)
    c.roundRect(bx, by, bw, bh, 8, stroke=1, fill=1)

    c.setStrokeColor(RULE_LINE)
    c.setLineWidth(0.5)
    c.roundRect(bx + 4, by + 4, bw - 8, bh - 8, 6, stroke=1, fill=0)

    c.setFont("PTSans-Bold", 8.5)
    c.setFillColor(GOLD)
    c.drawCentredString(cx, by + bh - 20, "СВЕДЕНИЯ О СЕМЕЙНОМ ДРЕВЕ")

    rows = [
        ("Отправная персона:", "Захаревич Игорь Владимирович (брат Владимир, 3 двоюр. брата)"),
        ("Линия отца:", "Захаревич и Хмыз · д. Большое Стиклево · находки ЦАМО (199 зсп, 173 сд)"),
        ("Второй брак бабушки:", "Марунов Иван Александрович · г. Сафоново (Смоленская обл.)"),
        ("Линия матери:", "Бунель (4 брата), Адамович (д. Ефимовичи и Счасновичи), Винничек"),
        ("Состав альбома:", "4 поколения · 22 персоны (+1 неизв. сиблинг) · 2 зацепки · 2 дела ЦАМО"),
    ]
    ry = by + bh - 43
    for idx, (label, val) in enumerate(rows):
        c.setFont("PTSans-Bold", 8.5)
        c.setFillColor(FOREST_DEEP)
        c.drawString(bx + 15, ry, label)
        draw_left_wrapped(c, val, bx + 146, ry, "Lora-Regular", 8.5, bw - 160, 10.6, color=INK)
        if idx < len(rows) - 1:
            c.setStrokeColor(RULE_LINE)
            c.setLineWidth(0.35)
            c.line(bx + 15, ry - 14, bx + bw - 15, ry - 14)
        ry -= 30

    # Contents preview below box
    c.setFont("PTSans-Bold", 8.3)
    c.setFillColor(INK_MUTED)
    c.drawCentredString(cx, 214, "СОДЕРЖАНИЕ АЛЬБОМА (8 СТРАНИЦ)")

    toc_items = [
        "Стр. 2 (альбомная) — Полное «Родовое древо»: 4 поколения, все братья и сёстры, 3 брака",
        "Стр. 3 — Поколение I (5 братьев) и Поколение II (родители, ветвь Маруновых)",
        "Стр. 4 — Поколение II (ветвь Бунель — Винничек) и Поколение III (линия отца и Маруновых)",
        "Стр. 5 — Поколение III (4 брата Бунель, Адамович) и Поколение IV (Бунель Александр и зацепки)",
        "Стр. 6 — Полный сводный реестр альбома (26 строк) и историко-географическая панорама",
        "Стр. 7 — Итоги поиска в ЦАМО, ПМВ (1914.svrt.ru) и аудит ЗАГС / метрических / камеральных баз",
        "Стр. 8 — Вопросы к родным, точные фонды НИАБ / ГАМн / ГАСО / ЗАГС и рабочая анкета",
    ]
    ty = 197
    for item in toc_items:
        c.setFont("Lora-Regular", 8.4)
        c.setFillColor(INK)
        c.drawCentredString(cx, ty, item)
        ty -= 15

    c.setFont("Lora-Italic", 8.5)
    c.setFillColor(INK_SOFT)
    c.drawCentredString(cx, 66, f"{data['edition']} · {data['date_label']}")
    c.showPage()


def draw_tree_card(
    c,
    x,
    y,
    w,
    h,
    title,
    role,
    subtitle,
    footer_note=None,
    bg=CARD_BG,
    border=FOREST_DEEP,
    accent=FOREST_DEEP,
    dashed=False,
    highlight_gold=False,
    badge_bg=CARD_BG_SOFT,
):
    c.saveState()
    if dashed:
        c.setDash(4, 3)
    c.setFillColor(bg)
    c.setStrokeColor(border)
    c.setLineWidth(1.4 if highlight_gold else 0.95)
    c.roundRect(x, y, w, h, 5.5, stroke=1, fill=1)

    if highlight_gold:
        c.setDash()
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.55)
        c.roundRect(x + 2.5, y + 2.5, w - 5, h - 5, 4.0, stroke=1, fill=0)

    c.setDash()
    pill_h = 12.5 if w < 90 else 13.5
    c.setFillColor(badge_bg)
    c.roundRect(x + 4, y + h - pill_h - 3.5, w - 8, pill_h, 3.0, stroke=0, fill=1)

    role_text = role.upper()
    role_size = 6.5 if w >= 90 else 5.8
    while role_size > 4.6 and pdfmetrics.stringWidth(role_text, "PTSans-Bold", role_size) > (w - 11):
        role_size -= 0.25
    c.setFont("PTSans-Bold", role_size)
    c.setFillColor(accent)
    c.drawCentredString(x + w / 2, y + h - pill_h - 0.1, role_text)

    name_top = y + h - (pill_h + 12.5)
    title_font = "Cormorant-Bold" if not dashed else "Lora-Bold"
    if w >= 142:
        title_size, leading = 10.2, 10.9
    elif w >= 100:
        title_size, leading = 9.0, 9.6
    elif w >= 74:
        title_size, leading = 8.1, 8.7
    else:
        title_size, leading = 7.4, 8.0
    if dashed:
        title_size = min(title_size, 8.2)
        leading = min(leading, 9.0)

    next_y = draw_centered_wrapped(
        c,
        title,
        x + w / 2,
        name_top,
        title_font,
        title_size,
        w - 8,
        leading,
        color=INK if not dashed else INK_MUTED,
    )

    min_sub_bottom = y + (13.5 if footer_note else 5)
    if subtitle and next_y - 0.5 >= min_sub_bottom:
        sub_font = "Lora-Italic" if dashed else "PTSans-Regular"
        if w >= 100:
            sub_size, sub_lead = 6.8, 7.9
        elif w >= 74:
            sub_size, sub_lead = 6.2, 7.2
        else:
            sub_size, sub_lead = 5.7, 6.7
        sub_size = fit_font_for_lines(subtitle, sub_font, sub_size, w - 8, min_size=4.8)
        lines = wrap_text(subtitle, sub_font, sub_size, w - 8)
        max_lines = max(1, int((next_y - min_sub_bottom + sub_lead - 1.5) // sub_lead))
        lines = lines[:max_lines]
        c.setFont(sub_font, sub_size)
        c.setFillColor(INK_MUTED)
        sy = next_y - 0.5
        for line in lines:
            c.drawCentredString(x + w / 2, sy, line)
            sy -= sub_lead

    if footer_note:
        fn_size = 6.3 if w >= 100 else (5.8 if w >= 74 else 5.3)
        while fn_size > 4.6 and pdfmetrics.stringWidth(footer_note, "PTSans-Italic", fn_size) > (w - 8):
            fn_size -= 0.25
        c.setFont("PTSans-Italic", fn_size)
        c.setFillColor(accent)
        c.drawCentredString(x + w / 2, y + 4.8, footer_note)

    c.restoreState()


def draw_marriage_knot(c, cx, cy, color=GOLD, label=None, r=7.8):
    c.saveState()
    c.setFillColor(CARD_BG)
    c.setStrokeColor(color)
    c.setLineWidth(1.1)
    c.circle(cx, cy, r, stroke=1, fill=1)
    c.setLineWidth(0.85)
    c.circle(cx - 2.2, cy, 2.7, stroke=1, fill=0)
    c.circle(cx + 2.2, cy, 2.7, stroke=1, fill=0)
    if label:
        c.setFont("PTSans-Bold", 5.8)
        c.setFillColor(color)
        c.drawCentredString(cx, cy + r + 3.0, label)
    c.restoreState()


def build_page_2_tree(c, data):
    draw_page_background(
        c,
        W_L,
        H_L,
        page_num=2,
        total_pages=TOTAL_PAGES,
        header_title="Визуальная схема · Полное родовое древо (4 поколения, 22 персоны + 1 неизв. сиблинг)",
    )

    cx_page = W_L / 2  # 420.94

    # Title block
    c.setFont("Cormorant-Bold", 20)
    c.setFillColor(FOREST_DEEP)
    c.drawCentredString(cx_page, H_L - 64, "Родовое древо Захаревич — Бунель")
    draw_ornamental_divider(c, cx_page, H_L - 74, width=260)

    # 1. Soft watercolor canopy backdrop
    c.saveState()
    blobs = [
        (125, 368, 108, 76, CANOPY_WASH_1),
        (260, 424, 130, 82, CANOPY_WASH_2),
        (430, 444, 155, 82, CANOPY_WASH_1),
        (595, 422, 138, 84, CANOPY_WASH_2),
        (720, 368, 112, 78, CANOPY_WASH_1),
        (195, 466, 102, 54, CANOPY_WASH_3),
        (485, 478, 135, 52, CANOPY_WASH_2),
        (685, 466, 115, 54, CANOPY_WASH_3),
        (395, 322, 200, 74, CANOPY_WASH_1),
    ]
    for bx, by, rx, ry, col in blobs:
        c.setFillColor(col)
        c.setFillAlpha(0.62)
        c.ellipse(bx - rx, by - ry, bx + rx, by + ry, stroke=0, fill=1)
    c.restoreState()

    # Exact zero-crossing planar geometry across x = 26..816 (790 pt)
    # Gen I (5 cards): y = 88..148 (h = 60)
    gen1_y, gen1_h = 88, 60
    igor_x, igor_w = 150, 146      # 150..296 (cx=223)
    vlad_x, vlad_w = 322, 146      # 322..468 (cx=395)
    trunk_x = 309                  # exact midpoint between 296 & 322 AND between Father & Mother!
    vit_x, vit_w = 482, 100        # 482..582 (cx=532)
    den_x, den_w = 588, 100        # 588..688 (cx=638)
    anat_x, anat_w = 698, 118      # 698..816 (cx=757)

    # Gen II (8 cards): y = 180..264 (h = 84)
    gen2_y, gen2_h = 180, 84
    val_x, val_w = 26, 80          # 26..106 (cx=66)
    nik_x, nik_w = 112, 80         # 112..192 (cx=152)
    fath_x, fath_w = 202, 98       # 202..300 (cx=251)
    moth_x, moth_w = 318, 98       # 318..416 (cx=367)
    vas2_x, vas2_w = 428, 84       # 428..512 (cx=470)
    vyach_x, vyach_w = 518, 86     # 518..604 (cx=561)
    evg_x, evg_w = 612, 96         # 612..708 (cx=660)
    bor_x, bor_w = 724, 92         # 724..816 (cx=770)
    # Central knot: (309, 222); Boris+Evgeniya knot: (716, 222)

    # Gen III (10 cards): y = 298..388 (h = 90)
    gen3_y, gen3_h = 298, 90
    mar_x, mar_w = 26, 94          # 26..120 (cx=73)
    nina_x, nina_w = 136, 102      # 136..238 (cx=187)
    mikh_x, mikh_w = 254, 96       # 254..350 (cx=302)
    fed3_x, fed3_w = 360, 56       # 360..416 (cx=388)
    vld3_x, vld3_w = 419, 57       # 419..476 (cx=447.5)
    ivn3_x, ivn3_w = 479, 56       # 479..535 (cx=507)
    vas3_x, vas3_w = 539, 77       # 539..616 (cx=577.5)
    mari_x, mari_w = 632, 66       # 632..698 (cx=665)
    nik3_x, nik3_w = 702, 58       # 702..760 (cx=731)
    unk3_x, unk3_w = 764, 52       # 764..816 (cx=790)

    # Gen IV (4 cards): y = 434..492 (h = 58)
    gen4_y, gen4_h = 434, 58
    c_hmyz_x, c_hmyz_w = 132, 112  # cx=188
    c_zah_x, c_zah_w = 250, 110    # cx=305
    c_bun_x, c_bun_w = 414, 152    # cx=490 (solid confirmed ancestor!)
    c_adam_x, c_adam_w = 660, 144  # cx=732

    # 2. Earthy hill & roots at the bottom
    c.saveState()
    p_hill = c.beginPath()
    p_hill.moveTo(175, 71)
    p_hill.curveTo(245, 93, 373, 93, 443, 71)
    p_hill.lineTo(443, 66)
    p_hill.curveTo(373, 71, 245, 71, 175, 66)
    p_hill.close()
    c.setFillColor(SOIL_LIGHT)
    c.setStrokeColor(SOIL_DARK)
    c.setLineWidth(0.7)
    c.drawPath(p_hill, stroke=1, fill=1)

    c.setStrokeColor(BARK_MID)
    c.setLineCap(1)
    root_curves = [
        (trunk_x - 10, 82, trunk_x - 36, 76, trunk_x - 76, 70, trunk_x - 118, 65, 2.9),
        (trunk_x - 6, 80, trunk_x - 24, 73, trunk_x - 48, 68, trunk_x - 72, 64, 2.0),
        (trunk_x + 10, 82, trunk_x + 36, 76, trunk_x + 76, 70, trunk_x + 118, 65, 2.9),
        (trunk_x + 6, 80, trunk_x + 24, 73, trunk_x + 48, 68, trunk_x + 72, 64, 2.0),
    ]
    for x0, y0, c1x, c1y, c2x, c2y, x1, y1, lw in root_curves:
        c.setLineWidth(lw)
        pr = c.beginPath()
        pr.moveTo(x0, y0)
        pr.curveTo(c1x, c1y, c2x, c2y, x1, y1)
        c.drawPath(pr, stroke=1, fill=0)

    c.setFont("PTSans-Bold", 7.0)
    c.setFillColor(PATERNAL_ACCENT)
    c.drawCentredString(96, 72, "Отцовские корни: д. Б. Стиклево")
    c.setFillColor(MARUNOV_ACCENT)
    c.drawCentredString(96, 62, "Отчим отца: г. Сафоново (Смоленск)")
    c.setFillColor(MATERNAL_ACCENT)
    c.drawCentredString(645, 72, "Материнские корни: д. Ефимовичи и Счасновичи (Клецкий р-н)")
    c.setFont("Lora-Italic", 6.8)
    c.setFillColor(INK_SOFT)
    c.drawCentredString(645, 62, "6 фамилий · 4 поколения · 22 персоны (+1 неизв. сиблинг)")

    # 3. Main trunk & botanical boughs
    p_trunk = c.beginPath()
    p_trunk.moveTo(trunk_x - 10.5, 79)
    p_trunk.curveTo(trunk_x - 6.5, 118, trunk_x - 4.5, 158, trunk_x - 4.0, 184)
    p_trunk.lineTo(trunk_x + 4.0, 184)
    p_trunk.curveTo(trunk_x + 4.5, 158, trunk_x + 6.5, 118, trunk_x + 10.5, 79)
    p_trunk.close()
    c.setFillColor(BARK_DARK)
    c.drawPath(p_trunk, stroke=0, fill=1)

    # Gen I sibling branches:
    # A) Игорь (223) and Владимир (395) from Parents' union (309, 222)
    c.setStrokeColor(BARK_MID)
    c.setLineWidth(2.4)
    c.line(trunk_x, 222, trunk_x, 166)
    for sx in [223, 395]:
        p_c = c.beginPath()
        p_c.moveTo(trunk_x, 166)
        p_c.curveTo((trunk_x + sx) / 2, 166, sx, 162, sx, gen1_y + gen1_h)
        c.drawPath(p_c, stroke=1, fill=0)

    # B) Виталий (532) and Денис (638) from Вячеслав (561)
    c.setStrokeColor(MATERNAL_ACCENT)
    c.setLineWidth(1.9)
    for sx in [532, 638]:
        p_vb = c.beginPath()
        p_vb.moveTo(561, gen2_y)
        p_vb.curveTo(561, 164, sx, 166, sx, gen1_y + gen1_h)
        c.drawPath(p_vb, stroke=1, fill=0)

    # C) Анатолий (757) from Евгения + Борис knot (716, 222)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.4)
    c.line(evg_x + evg_w, 222, bor_x, 222)
    c.setStrokeColor(MATERNAL_ACCENT)
    c.setLineWidth(1.9)
    p_an = c.beginPath()
    p_an.moveTo(716, 214)
    p_an.curveTo(716, 166, 757, 166, 757, gen1_y + gen1_h)
    c.drawPath(p_an, stroke=1, fill=0)

    # Main boughs from trunk fork up to Father (251) and Mother (367)
    c.setStrokeColor(BARK_DARK)
    c.setLineWidth(4.4)
    for sx in [251, 367]:
        p_p = c.beginPath()
        p_p.moveTo(trunk_x, 174)
        p_p.curveTo((trunk_x + sx) / 2, 178, sx, 174, sx, gen2_y + 2)
        c.drawPath(p_p, stroke=1, fill=0)

    # Central parental marriage line
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.line(fath_x + fath_w, 222, moth_x, 222)

    # --- Gen II -> Gen III branches (zero-crossing corridor y = 264..298) ---
    gen2_top = gen2_y + gen2_h  # 264
    gen3_bot = gen3_y           # 298
    gen3_mid = gen3_y + gen3_h / 2  # 343

    # A) 2nd marriage (Марунов 73 + Нина 187 -> knot at 128, 282) -> Валерий (66) & Николай (152)
    knot_mar_x, knot_mar_y = 128, 282
    c.setStrokeColor(MARUNOV_ACCENT)
    c.setLineWidth(1.4)
    c.line(mar_x + mar_w, gen3_mid, nina_x, gen3_mid)
    for px in [88, 168]:
        pm = c.beginPath()
        pm.moveTo(px, gen3_bot)
        pm.curveTo(px, 286, knot_mar_x, 285, knot_mar_x, knot_mar_y)
        c.drawPath(pm, stroke=1, fill=0)

    c.setStrokeColor(BARK_MID)
    c.setLineWidth(2.3)
    for sx in [66, 152]:
        ps = c.beginPath()
        ps.moveTo(sx, gen2_top)
        ps.curveTo(sx, 272, knot_mar_x, 273, knot_mar_x, knot_mar_y)
        c.drawPath(ps, stroke=1, fill=0)

    # B) 1st marriage (Нина 187 + Михаил 302 -> knot at 246, 282) -> Владимир М. (251)
    knot_zah_x, knot_zah_y = 246, 282
    c.setStrokeColor(PATERNAL_ACCENT)
    c.setLineWidth(1.4)
    c.line(nina_x + nina_w, gen3_mid, mikh_x, gen3_mid)
    for px in [210, 290]:
        pz = c.beginPath()
        pz.moveTo(px, gen3_bot)
        pz.curveTo(px, 286, knot_zah_x, 285, knot_zah_x, knot_zah_y)
        c.drawPath(pz, stroke=1, fill=0)

    c.setStrokeColor(BARK_DARK)
    c.setLineWidth(3.4)
    c.line(251, gen2_top, knot_zah_x, knot_zah_y)

    # C) Maternal union (Василий А. Бунель 577.5 + Мария Адамович 665 -> knot at 624, 282)
    #    branches cleanly down to Татьяна (367), Василий (470), Вячеслав (561), Евгения (660)
    knot_mat_x, knot_mat_y = 624, 282
    c.setStrokeColor(MATERNAL_ACCENT)
    c.setLineWidth(1.4)
    c.line(vas3_x + vas3_w, gen3_mid, mari_x, gen3_mid)
    for px in [592, 656]:
        pmat = c.beginPath()
        pmat.moveTo(px, gen3_bot)
        pmat.curveTo(px, 286, knot_mat_x, 285, knot_mat_x, knot_mat_y)
        c.drawPath(pmat, stroke=1, fill=0)

    c.setStrokeColor(BARK_MID)
    c.setLineWidth(2.8)
    pm_main = c.beginPath()
    pm_main.moveTo(367, gen2_top)
    pm_main.curveTo(380, 273, 520, 273, knot_mat_x, knot_mat_y)
    c.drawPath(pm_main, stroke=1, fill=0)
    for sx in [470, 561, 660]:
        c.setLineWidth(2.2)
        pms = c.beginPath()
        pms.moveTo(sx, gen2_top)
        pms.curveTo(sx, 272, (sx + knot_mat_x) / 2, 273, knot_mat_x, knot_mat_y)
        c.drawPath(pms, stroke=1, fill=0)

    # --- Gen III -> Gen IV boughs & clues (y = 388..434) ---
    gen3_top = gen3_y + gen3_h  # 388
    # A) Хмыз Андрей -> Нина Андреевна (dashed)
    c.setStrokeColor(BARK_LIGHT)
    c.setLineWidth(1.6)
    c.setDash(3, 2)
    c.line(187, gen3_top, 188, gen4_y)
    # B) Захаревич Пётр (?) -> Михаил (dashed)
    c.line(302, gen3_top, 305, gen4_y)
    c.setDash()

    # C) Бунель Александр (CONFIRMED!) -> 4 brothers (Фёдор 388, Владимир 447.5, Иван 507, Василий 577.5)
    c.setStrokeColor(BARK_DARK)
    c.setLineWidth(2.8)
    c.line(490, gen4_y, 490, 412)
    c.setLineWidth(1.9)
    for bx in [388, 447.5, 507, 577.5]:
        p4b = c.beginPath()
        p4b.moveTo(490, 412)
        p4b.curveTo((490 + bx) / 2, 412, bx, 405, bx, gen3_top)
        c.drawPath(p4b, stroke=1, fill=0)

    # D) Род Адамович -> Мария (665), Николай (731), ? (790) (dashed)
    c.setStrokeColor(BARK_LIGHT)
    c.setLineWidth(1.5)
    c.setDash(3, 2)
    c.line(732, gen4_y, 732, 412)
    for ax in [665, 731, 790]:
        p4a = c.beginPath()
        p4a.moveTo(732, 412)
        p4a.curveTo((732 + ax) / 2, 412, ax, 405, ax, gen3_top)
        c.drawPath(p4a, stroke=1, fill=0)
    c.setDash()

    # Botanical foliage accents
    foliage = [
        (44, 434, 130, 18, 8.0, SAGE_MID, 0.85),
        (76, 454, 108, 17, 7.5, FOREST_DEEP, 0.85),
        (110, 464, 90, 18, 8.0, SAGE_LIGHT, 0.88),
        (376, 488, 102, 17, 7.5, FOREST_DEEP, 0.85),
        (595, 492, 82, 18, 8.0, SAGE_MID, 0.88),
        (812, 428, 48, 17, 7.5, SAGE_MID, 0.85),
        (28, 340, 154, 16, 7.0, SAGE_LIGHT, 0.75),
        (185, 170, 145, 14, 6.2, SAGE_LIGHT, 0.70),
        (428, 170, 35, 14, 6.2, SAGE_LIGHT, 0.70),
    ]
    for lx, ly, ang, ln, wd, col, alp in foliage:
        draw_leaf(c, lx, ly, ang, ln, wd, col, FOREST_DEEP, alpha=alp)

    c.setFont("Lora-Italic", 7.1)
    c.setFillColor(MARUNOV_ACCENT)
    c.drawCentredString(74, 410, "Ветвь из г. Сафоново")
    c.drawCentredString(74, 400, "(Смоленская обл.)")

    c.restoreState()

    # 4. Marriage Knots
    draw_marriage_knot(c, trunk_x, 222, GOLD)
    draw_marriage_knot(c, 716, 222, MATERNAL_ACCENT, r=6.8)
    draw_marriage_knot(c, knot_mar_x, knot_mar_y, MARUNOV_ACCENT, label="2-й брак", r=7.2)
    draw_marriage_knot(c, knot_zah_x, knot_zah_y, PATERNAL_ACCENT, label="1-й брак", r=7.2)
    draw_marriage_knot(c, knot_mat_x, knot_mat_y, MATERNAL_ACCENT, r=7.2)

    # 5. Gen I Cards (5)
    draw_tree_card(
        c, igor_x, gen1_y, igor_w, gen1_h,
        title="Захаревич Игорь Владимирович",
        role="I поколение · «Я»",
        subtitle="Сын Владимира М. и Татьяны В.",
        footer_note="Отправная персона",
        bg=GOLD_BG, border=GOLD, accent=GOLD, highlight_gold=True, badge_bg=GOLD_LIGHT,
    )
    draw_tree_card(
        c, vlad_x, gen1_y, vlad_w, gen1_h,
        title="Захаревич Владимир Владимирович",
        role="I поколение · Родной брат",
        subtitle="Сын Владимира М. и Татьяны В.",
        footer_note="Даты и семья: ?",
        bg=CARD_BG, border=SAGE_MID, accent=FOREST_DEEP, badge_bg=CANOPY_WASH_1,
    )
    draw_tree_card(
        c, vit_x, gen1_y, vit_w, gen1_h,
        title="Бунель Виталий Вячеславович",
        role="I · Двоюр. брат",
        subtitle="Сын Вячеслава В. Бунеля",
        footer_note="Даты: ?",
        bg=MATERNAL_BG, border=MATERNAL_ACCENT, accent=MATERNAL_ACCENT, badge_bg=CARD_BG,
    )
    draw_tree_card(
        c, den_x, gen1_y, den_w, gen1_h,
        title="Бунель Денис Вячеславович",
        role="I · Двоюр. брат",
        subtitle="Сын Вячеслава В. Бунеля",
        footer_note="Даты: ?",
        bg=MATERNAL_BG, border=MATERNAL_ACCENT, accent=MATERNAL_ACCENT, badge_bg=CARD_BG,
    )
    draw_tree_card(
        c, anat_x, gen1_y, anat_w, gen1_h,
        title="Винничек Анатолий Борисович",
        role="I · Двоюродный брат",
        subtitle="Сын Евгении В. и Бориса Винничеков",
        footer_note="Даты: ?",
        bg=MATERNAL_BG, border=MATERNAL_ACCENT, accent=MATERNAL_ACCENT, badge_bg=CARD_BG,
    )

    # 6. Gen II Cards (8)
    draw_tree_card(
        c, val_x, gen2_y, val_w, gen2_h,
        title="Марунов Валерий Иванович",
        role="II · Дядя",
        subtitle="Единоутробный брат отца",
        footer_note="Даты: ?",
        bg=MARUNOV_BG, border=MARUNOV_ACCENT, accent=MARUNOV_ACCENT, badge_bg=CARD_BG,
    )
    draw_tree_card(
        c, nik_x, gen2_y, nik_w, gen2_h,
        title="Марунов Николай Иванович",
        role="II · Дядя",
        subtitle="Единоутробный брат отца",
        footer_note="Даты: ?",
        bg=MARUNOV_BG, border=MARUNOV_ACCENT, accent=MARUNOV_ACCENT, badge_bg=CARD_BG,
    )
    draw_tree_card(
        c, fath_x, gen2_y, fath_w, gen2_h,
        title="Захаревич Владимир Михайлович",
        role="II · Отец",
        subtitle="Сын Михаила и Нины Андреевны",
        footer_note="д. Б. Стиклево",
        bg=PATERNAL_BG, border=PATERNAL_ACCENT, accent=PATERNAL_ACCENT, badge_bg=CARD_BG,
    )
    draw_tree_card(
        c, moth_x, gen2_y, moth_w, gen2_h,
        title="Бунель Татьяна Васильевна",
        role="II · Мать",
        subtitle="Дочь Василия А. и Марии Адамович",
        footer_note="д. Ефимовичи",
        bg=MATERNAL_BG, border=MATERNAL_ACCENT, accent=MATERNAL_ACCENT, badge_bg=CARD_BG,
    )
    draw_tree_card(
        c, vas2_x, gen2_y, vas2_w, gen2_h,
        title="Бунель Василий Васильевич",
        role="II · Дядя",
        subtitle="Брат Татьяны В. Бунель",
        footer_note="Семья: ?",
        bg=MATERNAL_BG, border=MATERNAL_ACCENT, accent=MATERNAL_ACCENT, badge_bg=CARD_BG,
    )
    draw_tree_card(
        c, vyach_x, gen2_y, vyach_w, gen2_h,
        title="Бунель Вячеслав Васильевич",
        role="II · Дядя",
        subtitle="Отец Виталия и Дениса",
        footer_note="Супруга: ?",
        bg=MATERNAL_BG, border=MATERNAL_ACCENT, accent=MATERNAL_ACCENT, badge_bg=CARD_BG,
    )
    draw_tree_card(
        c, evg_x, gen2_y, evg_w, gen2_h,
        title="Винничек Евгения Васильевна",
        role="II · Тётя (мат.)",
        subtitle="Урожд. Бунель · мать Анатолия",
        footer_note="Брак: Борис В.",
        bg=MATERNAL_BG, border=MATERNAL_ACCENT, accent=MATERNAL_ACCENT, badge_bg=CARD_BG,
    )
    draw_tree_card(
        c, bor_x, gen2_y, bor_w, gen2_h,
        title="Винничек Борис",
        role="II · Зять",
        subtitle="Муж Евгении В., отец Анатолия",
        footer_note="Отчество: ?",
        bg=MATERNAL_BG, border=MATERNAL_ACCENT, accent=MATERNAL_ACCENT, badge_bg=CARD_BG,
    )

    # 7. Gen III Cards (10)
    draw_tree_card(
        c, mar_x, gen3_y, mar_w, gen3_h,
        title="Марунов Иван Александрович",
        role="III · Отчим отца",
        subtitle="г. Сафоново · 2-й муж Нины Андр.",
        footer_note="Даты, ВОВ: ?",
        bg=MARUNOV_BG, border=MARUNOV_ACCENT, accent=MARUNOV_ACCENT, badge_bg=CARD_BG,
    )
    draw_tree_card(
        c, nina_x, gen3_y, nina_w, gen3_h,
        title="Нина Андреевна (ур. Хмыз)",
        role="III · Бабушка (от.)",
        subtitle="1-й бр. Захаревич, 2-й Марунова",
        footer_note="д. Б. Стиклево",
        bg=PATERNAL_BG, border=PATERNAL_ACCENT, accent=PATERNAL_ACCENT, badge_bg=CARD_BG,
    )
    draw_tree_card(
        c, mikh_x, gen3_y, mikh_w, gen3_h,
        title="Захаревич Михаил [Петрович?]",
        role="III · Дед по отцу",
        subtitle="1917–23.10.1944 (? · 173 сд, Сувалки)",
        footer_note="ЦАМО: сверить!",
        bg=PATERNAL_BG, border=PATERNAL_ACCENT, accent=PATERNAL_ACCENT, badge_bg=CARD_BG,
    )
    draw_tree_card(
        c, fed3_x, gen3_y, fed3_w, gen3_h,
        title="Бунель Фёдор Александ.",
        role="Брат деда",
        subtitle="Сын Александра",
        footer_note="Даты: ?",
        bg=MATERNAL_BG, border=MATERNAL_ACCENT, accent=MATERNAL_ACCENT, badge_bg=CARD_BG,
    )
    draw_tree_card(
        c, vld3_x, gen3_y, vld3_w, gen3_h,
        title="Бунель Владимир Александ.",
        role="Брат деда",
        subtitle="Сын Александра",
        footer_note="Даты: ?",
        bg=MATERNAL_BG, border=MATERNAL_ACCENT, accent=MATERNAL_ACCENT, badge_bg=CARD_BG,
    )
    draw_tree_card(
        c, ivn3_x, gen3_y, ivn3_w, gen3_h,
        title="Бунель Иван Александ.",
        role="Брат деда",
        subtitle="Сын Александра",
        footer_note="Даты: ?",
        bg=MATERNAL_BG, border=MATERNAL_ACCENT, accent=MATERNAL_ACCENT, badge_bg=CARD_BG,
    )
    draw_tree_card(
        c, vas3_x, gen3_y, vas3_w, gen3_h,
        title="Бунель Василий Александрович",
        role="III · Дед (мат.)",
        subtitle="1918 (ВПП) · 43 зсп · ВОВ, плен",
        footer_note="д. Ефимовичи",
        bg=MATERNAL_BG, border=MATERNAL_ACCENT, accent=MATERNAL_ACCENT, badge_bg=CARD_BG,
    )
    draw_tree_card(
        c, mari_x, gen3_y, mari_w, gen3_h,
        title="Адамович Мария",
        role="III · Бабушка",
        subtitle="Ур. Адамович · д. Ефимовичи",
        footer_note="Отчество: ?",
        bg=MATERNAL_BG, border=MATERNAL_ACCENT, accent=MATERNAL_ACCENT, badge_bg=CARD_BG,
    )
    draw_tree_card(
        c, nik3_x, gen3_y, nik3_w, gen3_h,
        title="Адамович Николай",
        role="Брат баб.",
        subtitle="д. Счасновичи",
        footer_note="Семья: ?",
        bg=MATERNAL_BG, border=MATERNAL_ACCENT, accent=MATERNAL_ACCENT, badge_bg=CARD_BG,
    )
    draw_tree_card(
        c, unk3_x, gen3_y, unk3_w, gen3_h,
        title="Адамович (?)",
        role="III · ?",
        subtitle="Брат или сестра Марии",
        footer_note="Имя забыто",
        bg=CLUE_BG, border=CLUE_BORDER, accent=INK_SOFT, dashed=True, badge_bg=PARCHMENT,
    )

    # 8. Gen IV Cards (1 confirmed + 3 clues/research)
    draw_tree_card(
        c, c_hmyz_x, gen4_y, c_hmyz_w, gen4_h,
        title="Хмыз Андрей",
        role="Зацепка IV колена",
        subtitle="Отец Нины Андр. (ур. Хмыз) + ?",
        bg=GOLD_BG, border=GOLD, accent=GOLD, dashed=True, badge_bg=CARD_BG,
    )
    draw_tree_card(
        c, c_zah_x, gen4_y, c_zah_w, gen4_h,
        title="Захаревич Пётр (?)",
        role="Гипотеза ЦАМО IV к.",
        subtitle="По отчеству М. П. и И. П. (173 сд)",
        bg=CLUE_BG, border=CLUE_BORDER, accent=INK_SOFT, dashed=True, badge_bg=PARCHMENT,
    )
    draw_tree_card(
        c, c_bun_x, gen4_y, c_bun_w, gen4_h,
        title="Бунель Александр",
        role="IV поколение · Прадед",
        subtitle="Отец 4 сыновей (д. Ефимовичи) + супруга ?",
        bg=MATERNAL_BG, border=MATERNAL_ACCENT, accent=MATERNAL_ACCENT, dashed=False, badge_bg=CARD_BG,
    )
    draw_tree_card(
        c, c_adam_x, gen4_y, c_adam_w, gen4_h,
        title="Род Адамович (?)",
        role="IV колено · Поиск",
        subtitle="Родители Марии и Николая",
        bg=CLUE_BG, border=CLUE_BORDER, accent=INK_SOFT, dashed=True, badge_bg=PARCHMENT,
    )

    # 9. Legend bar
    ly = 42
    c.setFillColor(CARD_BG)
    c.setStrokeColor(RULE_LINE)
    c.setLineWidth(0.6)
    c.roundRect(34, ly, W_L - 68, 16, 4, stroke=1, fill=1)

    legend_items = [
        (44, GOLD, "Отправная персона", False),
        (158, PATERNAL_ACCENT, "Линия отца: Захаревич и Хмыз", False),
        (332, MARUNOV_ACCENT, "Отчим отца и сводные: Маруновы", False),
        (524, MATERNAL_ACCENT, "Линия матери: Бунель / Адамович / Винничек", False),
        (742, CLUE_BORDER, "Зацепка / ? к.", True),
    ]
    for lx, col, lbl, is_dash in legend_items:
        c.saveState()
        c.setStrokeColor(col)
        c.setFillColor(col if not is_dash else CLUE_BG)
        if is_dash:
            c.setDash(2, 1.5)
        c.roundRect(lx, ly + 4, 8, 8, 2, stroke=1, fill=1)
        c.setDash()
        c.setFont("PTSans-Regular", 7.0)
        c.setFillColor(INK_MUTED)
        c.drawString(lx + 11.5, ly + 5.3, lbl)
        c.restoreState()

    c.showPage()


def format_person_display_name(person):
    pid = person["id"]
    if pid == "nina_paternal":
        return "Марунова (Захаревич, урожд. Хмыз) Нина Андреевна"
    if pid == "tatyana_bunel":
        return "Бунель Татьяна Васильевна (в дев.)"
    if pid == "evgeniya_vinnichek":
        return "Винничек (урожд. Бунель) Евгения Васильевна"
    if pid == "mikhail_zaharevich":
        return "Захаревич Михаил [предп. Петрович]"
    if pid == "adamovich_unknown_sibling":
        return "Адамович [имя неизвестно]"
    surname_part = person.get("surname") or "(фамилия ?)"
    pat_part = person.get("patronymic") or ""
    return f"{surname_part} {person['first_name']} {pat_part}".strip()


def draw_person_dossier_card(c, x, y, w, h, person, accent, bg_tint, border_col, dashed=False):
    c.saveState()
    is_col3 = w < 200
    is_narrow = w < 320

    if dashed:
        c.setDash(4, 3)
    c.setFillColor(CARD_BG)
    c.setStrokeColor(border_col)
    c.setLineWidth(0.9)
    c.roundRect(x, y, w, h, 6, stroke=1, fill=1)
    c.setDash()

    c.setFillColor(accent)
    c.roundRect(x, y, 4.5 if is_col3 else 5, h, 2, stroke=0, fill=1)

    header_h = 26 if is_col3 else (28 if is_narrow else 30)
    c.setFillColor(bg_tint)
    c.rect(x + 5, y + h - header_h, w - 6, header_h - 1, stroke=0, fill=1)
    c.setStrokeColor(RULE_LINE)
    c.setLineWidth(0.4)
    c.line(x + 5, y + h - header_h, x + w, y + h - header_h)

    full_name = format_person_display_name(person)
    name_size = 9.7 if is_col3 else (11.0 if is_narrow else 12.6)
    while name_size > 7.6 and pdfmetrics.stringWidth(full_name, "Cormorant-Bold", name_size) > (w - 16):
        name_size -= 0.35
    c.setFont("Cormorant-Bold", name_size)
    c.setFillColor(INK)
    c.drawString(x + 10, y + h - (12.8 if is_col3 else 14.2), full_name)

    role_text = f"{person['role'].upper()} · ПОК. {person['generation']}"
    role_size = 6.2 if is_col3 else (6.8 if is_narrow else 7.3)
    while role_size > 5.0 and pdfmetrics.stringWidth(role_text, "PTSans-Bold", role_size) > (w - 16):
        role_size -= 0.25
    c.setFont("PTSans-Bold", role_size)
    c.setFillColor(accent)
    c.drawString(x + 10, y + h - (header_h - 3.5), role_text)

    life_val = person.get("birth_date") or "даты жизни уточняются"
    if person.get("death_place"):
        b_lbl = person.get("birth_date") or "рожд. ?"
        d_lbl = person.get("death_date") or "погиб"
        life_val = f"{b_lbl} · {d_lbl}; {person['death_place']}"
    elif person.get("death_date"):
        life_val = f"{person.get('birth_date') or 'рожд. ?'} · {person['death_date']}"

    if is_col3:
        fields = [
            ("Даты:", life_val),
            ("Истоки:", person.get("residence") or person.get("birth_place") or "уточняется"),
            ("Заметка:", person.get("notes") or "—"),
        ]
        val_offset = 44
        f_lbl_sz = 6.5
        f_val_sz = 6.6
        f_lead = 7.9
        row_gap = 1.4
    elif is_narrow:
        fields = [
            ("Даты:", life_val),
            ("Истоки:", person.get("residence") or person.get("birth_place") or "уточняется"),
            ("Брак:", person.get("marriage_display") or "уточняется"),
            ("Заметка:", person.get("notes") or "—"),
        ]
        val_offset = 56
        f_lbl_sz = 7.1
        f_val_sz = 7.2
        f_lead = 8.6
        row_gap = 1.6
    else:
        fields = [
            ("Даты / судьба:", life_val),
            ("Место / истоки:", person.get("residence") or person.get("birth_place") or "уточняется"),
            ("Брак / супруг(а):", person.get("marriage_display") or "уточняется"),
            ("Комментарий:", person.get("notes") or "—"),
        ]
        val_offset = 102
        f_lbl_sz = 7.6
        f_val_sz = 7.9
        f_lead = 9.4
        row_gap = 2.0

    fy = y + h - header_h - (9.5 if is_col3 else 10.5)
    for label, val in fields:
        if fy < y + 5:
            print(f"WARNING: skipped field '{label}' for {person['id']}")
            break
        c.setFont("PTSans-Bold", f_lbl_sz)
        c.setFillColor(INK_MUTED)
        c.drawString(x + 10, fy, label)
        val_x = x + val_offset
        max_w = w - val_offset - 7
        lines = wrap_text(val, "Lora-Regular", f_val_sz, max_w)
        avail_lines = max(1, int((fy - (y + 4.5)) // f_lead) + 1)
        if len(lines) > avail_lines:
            print(f"WARNING: clipped field '{label}' for {person['id']} ({len(lines)} > {avail_lines}): {lines[avail_lines:]}")
            lines = lines[:avail_lines]
        c.setFont("Lora-Regular", f_val_sz)
        c.setFillColor(INK)
        ly = fy
        for line in lines:
            c.drawString(val_x, ly, line)
            ly -= f_lead
        fy = ly - row_gap

    c.restoreState()


def draw_section_banner(c, x, y, w, title, subtitle, accent):
    c.saveState()
    title_sz = 13.6
    sub_sz = 8.2
    while title_sz > 7.4 and (
        pdfmetrics.stringWidth(title, "Cormorant-Bold", title_sz)
        + pdfmetrics.stringWidth(subtitle, "Lora-Italic", sub_sz)
        + 18
        > w
    ):
        title_sz -= 0.4
        sub_sz = max(6.2, sub_sz - 0.22)

    c.setFont("Cormorant-Bold", title_sz)
    c.setFillColor(accent)
    c.drawString(x, y, title)
    c.setFont("Lora-Italic", sub_sz)
    c.setFillColor(INK_MUTED)
    c.drawRightString(x + w, y + 1, subtitle)
    c.setStrokeColor(accent)
    c.setLineWidth(0.75)
    c.line(x, y - 5, x + w, y - 5)
    c.restoreState()


def enrich_marriage_labels(persons):
    by_id = {p["id"]: p for p in persons}
    out = []
    for p in persons:
        cp = dict(p)
        sp_names = []
        for sid in p.get("spouses", []):
            sp = by_id.get(sid)
            if sp:
                if sp["id"] == "nina_paternal":
                    s_name = "Нина Андреевна (ур. Хмыз)"
                else:
                    s_name = " ".join(filter(None, [sp.get("surname"), sp.get("first_name"), sp.get("patronymic")]))
                sp_names.append(s_name)
        if sp_names:
            if p["id"] == "nina_paternal":
                cp["marriage_display"] = "1-й муж: Захаревич Михаил; 2-й муж (после ВОВ): Марунов Иван Александрович"
            else:
                cp["marriage_display"] = ", ".join(sp_names) + " (дата и место ?)"
        else:
            cp["marriage_display"] = None
        out.append(cp)
    return out


def build_page_3_gen1_and_parents(c, data):
    draw_page_background(
        c, W_P, H_P, page_num=3, total_pages=TOTAL_PAGES,
        header_title="Поколение I (родные и двоюродные братья) и Поколение II (родители, Маруновы)"
    )
    persons = enrich_marriage_labels(data["persons"])
    by_id = {p["id"]: p for p in persons}

    x = 34
    w = W_P - 68  # 527.27
    half_w = (w - 10) / 2  # 258.6
    col3_w = (w - 16) / 3  # 170.4

    # Section 1: Gen I (5 cards: 2 + 3)
    draw_section_banner(c, x, H_P - 66, w, "Поколение I · Современная ветвь (5 персон)", "Отправная персона, родной и двоюродные братья", GOLD)
    draw_person_dossier_card(c, x, H_P - 170, half_w, 92, by_id["igor_zaharevich"], GOLD, GOLD_BG, GOLD)
    draw_person_dossier_card(c, x + half_w + 10, H_P - 170, half_w, 92, by_id["vladimir_v_zaharevich"], FOREST_DEEP, CANOPY_WASH_1, SAGE_MID)

    draw_person_dossier_card(c, x, H_P - 274, col3_w, 96, by_id["vitaliy_bunel"], MATERNAL_ACCENT, MATERNAL_BG, MATERNAL_BORDER)
    draw_person_dossier_card(c, x + col3_w + 8, H_P - 274, col3_w, 96, by_id["denis_bunel"], MATERNAL_ACCENT, MATERNAL_BG, MATERNAL_BORDER)
    draw_person_dossier_card(c, x + 2 * (col3_w + 8), H_P - 274, col3_w, 96, by_id["anatoliy_vinnichek"], MATERNAL_ACCENT, MATERNAL_BG, MATERNAL_BORDER)

    # Section 2: Gen II Parents (2 cards)
    draw_section_banner(c, x, H_P - 296, w, "Поколение II · Родители", "Союз родов Захаревич (д. Б. Стиклево) и Бунель (д. Ефимовичи)", FOREST_DEEP)
    draw_person_dossier_card(c, x, H_P - 422, half_w, 114, by_id["vladimir_m_zaharevich"], PATERNAL_ACCENT, PATERNAL_BG, PATERNAL_BORDER)
    draw_person_dossier_card(c, x + half_w + 10, H_P - 422, half_w, 114, by_id["tatyana_bunel"], MATERNAL_ACCENT, MATERNAL_BG, MATERNAL_BORDER)

    # Section 3: Gen II Father's Half-Brothers (Marunov, 2 cards)
    draw_section_banner(c, x, H_P - 444, w, "Поколение II · Единоутробные братья отца (ветвь Марунов)", "2-й брак Нины Андреевны (урожд. Хмыз) и И. А. Марунова", MARUNOV_ACCENT)
    draw_person_dossier_card(c, x, H_P - 564, half_w, 108, by_id["valery_marunov"], MARUNOV_ACCENT, MARUNOV_BG, MARUNOV_BORDER)
    draw_person_dossier_card(c, x + half_w + 10, H_P - 564, half_w, 108, by_id["nikolay_marunov"], MARUNOV_ACCENT, MARUNOV_BG, MARUNOV_BORDER)

    # Explanation Card at bottom (54..262)
    c.saveState()
    c.setFillColor(CARD_BG_SOFT)
    c.setStrokeColor(RULE_LINE)
    c.setLineWidth(0.75)
    c.roundRect(x, 54, w, 206, 6, stroke=1, fill=1)
    c.setFont("PTSans-Bold", 8.5)
    c.setFillColor(FOREST_DEEP)
    c.drawString(x + 14, 244, "Пояснение по родственным линиям I и II поколений:")

    items = [
        ("1. Главная линия Захаревич — Бунель:",
         "Владимир Михайлович Захаревич (родом по линии д. Большое Стиклево) и Татьяна Васильевна (урожд. Бунель, линия д. Ефимовичи) — родители Игоря Владимировича и Владимира Владимировича Захаревичей."),
        ("2. Ветвь Маруновых (единоутробные братья отца):",
         "После гибели на фронте первого мужа (Михаила Захаревича) Нина Андреевна (урожд. Хмыз) вышла замуж за Ивана Александровича Марунова из г. Сафоново. Их сыновья Валерий Иванович и Николай Иванович Маруновы — единоутробные братья отца (дяди для авторов древа)."),
        ("3. Двоюродные братья по материнской линии (Бунель и Винничек):",
         "У дяди Вячеслава Васильевича Бунеля двое сыновей — Виталий и Денис Вячеславовичи Бунель. У тёти Евгении Васильевны (урожд. Бунель) и её мужа Бориса Винничека — сын Анатолий Борисович Винничек. Все трое приходятся двоюродными братьями Игорю и Владимиру Захаревичам."),
    ]
    iy = 227
    for head, body in items:
        c.setFont("PTSans-Bold", 8.0)
        c.setFillColor(PATERNAL_ACCENT if head.startswith("2.") else (MATERNAL_ACCENT if head.startswith("3.") else FOREST_DEEP))
        c.drawString(x + 14, iy, head)
        next_y = draw_left_wrapped(c, body, x + 14, iy - 11.5, "Lora-Regular", 7.9, w - 28, 9.7, color=INK)
        iy = next_y - 7.5
    c.restoreState()

    c.showPage()


def build_page_4_gen2_mat_and_gen3_pat(c, data):
    draw_page_background(
        c, W_P, H_P, page_num=4, total_pages=TOTAL_PAGES,
        header_title="Поколение II (ветвь Бунель — Винничек) и Поколение III (линия отца)"
    )
    persons = enrich_marriage_labels(data["persons"])
    by_id = {p["id"]: p for p in persons}

    x = 34
    w = W_P - 68
    half_w = (w - 10) / 2

    # Section 1: Gen II Mother's Siblings & Spouse (4 cards)
    draw_section_banner(
        c, x, H_P - 66, w,
        "Поколение II · Братья, сестра и зять матери",
        "Ветвь Бунель — Винничек (дети В. А. Бунеля и М. Адамович)",
        MATERNAL_ACCENT,
    )
    draw_person_dossier_card(c, x, H_P - 180, half_w, 102, by_id["vasily_v_bunel"], MATERNAL_ACCENT, MATERNAL_BG, MATERNAL_BORDER)
    draw_person_dossier_card(c, x + half_w + 10, H_P - 180, half_w, 102, by_id["vyacheslav_bunel"], MATERNAL_ACCENT, MATERNAL_BG, MATERNAL_BORDER)
    draw_person_dossier_card(c, x, H_P - 292, half_w, 102, by_id["evgeniya_vinnichek"], MATERNAL_ACCENT, MATERNAL_BG, MATERNAL_BORDER)
    draw_person_dossier_card(c, x + half_w + 10, H_P - 292, half_w, 102, by_id["boris_vinnichek"], MATERNAL_ACCENT, MATERNAL_BG, MATERNAL_BORDER)

    # Section 2: Gen III Paternal & Marunov (3 cards)
    draw_section_banner(
        c, x, H_P - 314, w,
        "Поколение III · Отцовская и маруновская ветви",
        "д. Большое Стиклево (Минский р-н) и г. Сафоново (Смоленская обл.)",
        PATERNAL_ACCENT,
    )
    draw_person_dossier_card(c, x, H_P - 432, w, 106, by_id["nina_paternal"], PATERNAL_ACCENT, PATERNAL_BG, PATERNAL_BORDER)
    draw_person_dossier_card(c, x, H_P - 602, half_w, 160, by_id["mikhail_zaharevich"], PATERNAL_ACCENT, PATERNAL_BG, PATERNAL_BORDER)
    draw_person_dossier_card(c, x + half_w + 10, H_P - 602, half_w, 160, by_id["marunov_ivan"], MARUNOV_ACCENT, MARUNOV_BG, MARUNOV_BORDER)

    # Historical note box at bottom (54..226)
    c.saveState()
    c.setFillColor(PATERNAL_BG)
    c.setStrokeColor(PATERNAL_BORDER)
    c.setLineWidth(0.8)
    c.roundRect(x, 54, w, 170, 6, stroke=1, fill=1)
    c.setFillColor(PATERNAL_ACCENT)
    c.roundRect(x, 54, 4.5, 170, 2, stroke=0, fill=1)

    c.setFont("PTSans-Bold", 8.4)
    c.setFillColor(PATERNAL_ACCENT)
    c.drawString(x + 14, 208, "Исторический контекст · Дед Михаил Захаревич и призыв 1944 года в д. Большое Стиклево")
    hist_txt = (
        "Минский район был освобождён в начале июля 1944 года в ходе операции «Багратион», сразу после чего Минским РВК "
        "была проведена массовая мобилизация мужчин д. Большое Стиклево. В делах 199-го запасного стрелкового полка (ЦАМО ф. 8495) "
        "от 29 июля 1944 г. сохранилась запись на сержанта Захаровича [опечатка в гласной] Михаила Петровича, 1917 г.р., из д. Б. Стиклево — "
        "в одном списке с его односельчанином-связистом Хмызом Фёдором Даниловичем (1918 г.р.). "
        "Далее 173-я стрелковая дивизия (3-й Белорусский фронт) вела тяжёлые бои на Сувалкском выступе в Польше. По донесению о потерях "
        "173 сд от 23 октября 1944 г. (в день взятия г. Сувалки) красноармеец Захаревич Михаил Петрович (1917 г.р., «дер. Б.-Стекольное») был убит "
        "и первично похоронен в 100 м севернее д. Кшивулька Сувалкского повета — ныне это воинское кладбище на ул. Миколая Рея в черте г. Сувалки."
    )
    draw_left_wrapped(c, hist_txt, x + 14, 193, "Lora-Regular", 7.85, w - 28, 9.8, color=INK)
    c.restoreState()

    c.showPage()


def build_page_5_gen3_mat_and_gen4(c, data):
    draw_page_background(
        c, W_P, H_P, page_num=5, total_pages=TOTAL_PAGES,
        header_title="Поколение III (линия матери: Бунель, Адамович) и Поколение IV (прадеды)"
    )
    persons = enrich_marriage_labels(data["persons"])
    by_id = {p["id"]: p for p in persons}
    unk_sib = data["unknown_siblings"][0]

    x = 34
    w = W_P - 68
    half_w = (w - 10) / 2
    col3_w = (w - 16) / 3

    # Section 1: Gen III Bunel brothers (4)
    draw_section_banner(
        c, x, H_P - 66, w,
        "Поколение III · Братья Бунель (сыновья Александра Бунеля)",
        "д. Ефимовичи, Кухчицкий с/с, Клецкий р-н",
        MATERNAL_ACCENT,
    )
    draw_person_dossier_card(c, x, H_P - 188, w, 110, by_id["vasily_bunel"], MATERNAL_ACCENT, MATERNAL_BG, MATERNAL_BORDER)

    draw_person_dossier_card(c, x, H_P - 288, col3_w, 92, by_id["ivan_bunel"], MATERNAL_ACCENT, MATERNAL_BG, MATERNAL_BORDER)
    draw_person_dossier_card(c, x + col3_w + 8, H_P - 288, col3_w, 92, by_id["vladimir_bunel"], MATERNAL_ACCENT, MATERNAL_BG, MATERNAL_BORDER)
    draw_person_dossier_card(c, x + 2 * (col3_w + 8), H_P - 288, col3_w, 92, by_id["fedor_bunel"], MATERNAL_ACCENT, MATERNAL_BG, MATERNAL_BORDER)

    # Section 2: Gen III Adamovich branch (3 cards)
    draw_section_banner(
        c, x, H_P - 310, w,
        "Поколение III · Бабушка Адамович Мария, её брат Николай и родня",
        "д. Ефимовичи и д. Счасновичи",
        MATERNAL_ACCENT,
    )
    draw_person_dossier_card(c, x, H_P - 428, col3_w, 108, by_id["maria_adamovich"], MATERNAL_ACCENT, MATERNAL_BG, MATERNAL_BORDER)
    draw_person_dossier_card(c, x + col3_w + 8, H_P - 428, col3_w, 108, by_id["nikolay_adamovich"], MATERNAL_ACCENT, MATERNAL_BG, MATERNAL_BORDER)
    draw_person_dossier_card(c, x + 2 * (col3_w + 8), H_P - 428, col3_w, 108, unk_sib, INK_SOFT, CLUE_BG, CLUE_BORDER, dashed=True)

    # Section 3: Gen IV (1 confirmed ancestor + 2 clues)
    draw_section_banner(
        c, x, H_P - 450, w,
        "Поколение IV · Подтверждённый прадед и зацепки для поиска",
        "Вершина древа по данным семьи и ЦАМО",
        GOLD,
    )
    draw_person_dossier_card(c, x, H_P - 560, w, 98, by_id["aleksandr_bunel"], MATERNAL_ACCENT, MATERNAL_BG, MATERNAL_BORDER)

    for idx, clue in enumerate(data["research_clues"]):
        cx_box = x + idx * (half_w + 10)
        c.saveState()
        c.setFillColor(GOLD_BG if idx == 0 else CLUE_BG)
        c.setStrokeColor(GOLD if idx == 0 else CLUE_BORDER)
        c.setDash(4, 3)
        c.setLineWidth(0.95)
        c.roundRect(cx_box, H_P - 664, half_w, 94, 6, stroke=1, fill=1)
        c.setDash()
        c.setFont("PTSans-Bold", 8.0)
        c.setFillColor(GOLD if idx == 0 else PATERNAL_ACCENT)
        c.drawString(cx_box + 10, H_P - 586, clue["label"].upper())
        c.setFont("PTSans-Bold", 7.2)
        c.setFillColor(INK_MUTED)
        c.drawString(cx_box + 10, H_P - 598, clue["relation"])
        draw_left_wrapped(
            c,
            f"{clue['status']}. {clue['source']}",
            cx_box + 10,
            H_P - 611,
            "Lora-Italic",
            7.4,
            half_w - 20,
            9.0,
            color=INK,
        )
        c.restoreState()

    # Bottom clarification block
    c.saveState()
    c.setFillColor(CARD_BG_SOFT)
    c.setStrokeColor(RULE_LINE)
    c.setLineWidth(0.7)
    c.roundRect(x, 54, w, 112, 6, stroke=1, fill=1)
    c.setFont("PTSans-Bold", 8.2)
    c.setFillColor(MATERNAL_ACCENT)
    c.drawString(x + 12, 152, "Примечание о IV поколении и географии ветви Адамович:")
    note_g4 = (
        "1) Прадед Бунель Александр переведён из предварительных зацепок в подтверждённое IV поколение: он является общим отцом четырёх "
        "братьев — Василия, Ивана, Владимира и Фёдора Александровичей Бунель (д. Ефимовичи, Клецкий р-н).  "
        "2) По материнской линии бабушки Марии Адамович установлен её брат Николай Адамович (жил в д. Счасновичи) и известно, что у них был "
        "как минимум ещё один брат или сестра (имя уточняется).  "
        "3) По современной картографии Клецкого и соседнего Несвижского р-нов близ д. Ефимовичи находятся д. Чановичи (Ланский с/с Несвижского р-на) "
        "и д. Чаша (Заостровечский с/с Клецкого р-на) — стоит уточнить у родных, соответствует ли «д. Счасновичи» одному из этих сёл."
    )
    draw_left_wrapped(c, note_g4, x + 12, 139, "Lora-Regular", 7.55, w - 24, 9.1, color=INK)
    c.restoreState()

    c.showPage()


def build_page_6_index_and_regions(c, data):
    draw_page_background(
        c, W_P, H_P, page_num=6, total_pages=TOTAL_PAGES,
        header_title="Полный сводный реестр альбома и география рода"
    )

    x = 34
    w = W_P - 68
    col3_w = (w - 16) / 3

    draw_section_banner(
        c, x, H_P - 66, w,
        "Сводный реестр персон альбома (22 персоны + 1 сиблинг + 3 узла IV к.)",
        "Редакция 4.0 · Полный именной указатель",
        FOREST_DEEP,
    )

    ty = H_P - 80
    cols = [
        ("№", 20),
        ("ФИО / Известное имя", 172),
        ("Роль и поколение", 112),
        ("Истоки / ЦАМО", 110),
        ("Что уточнить", w - 414),
    ]
    c.saveState()
    c.setFillColor(FOREST_DEEP)
    c.rect(x, ty - 16, w, 16, stroke=0, fill=1)
    cx_pos = x
    c.setFont("PTSans-Bold", 7.1)
    c.setFillColor(colors.white)
    for cname, cw in cols:
        c.drawString(cx_pos + 4, ty - 11, cname)
        cx_pos += cw

    table_rows = [
        ("1", "Захаревич Игорь Владимирович", "I · Отправная персона", "— (Минская обл.)", "Даты рожд., семья"),
        ("2", "Захаревич Владимир Владимирович", "I · Родной брат", "— (Минская обл.)", "Даты, супруга, дети"),
        ("3", "Бунель Виталий Вячеславович", "I · Двоюр. брат (сын Вячеслава)", "линия д. Ефимовичи", "Даты, семья, дети"),
        ("4", "Бунель Денис Вячеславович", "I · Двоюр. брат (сын Вячеслава)", "линия д. Ефимовичи", "Даты, семья, дети"),
        ("5", "Винничек Анатолий Борисович", "I · Двоюр. брат (сын Евгении и Б.)", "линия д. Ефимовичи", "Даты, семья, дети"),
        ("6", "Захаревич Владимир Михайлович", "II · Отец", "линия д. Б. Стиклево", "Даты рожд., брак"),
        ("7", "Марунов Валерий Иванович", "II · Дядя (единоутр. брат отца)", "сын И. А. и Нины А.", "Даты, семья, дети"),
        ("8", "Марунов Николай Иванович", "II · Дядя (единоутр. брат отца)", "сын И. А. и Нины А.", "Даты, семья, дети"),
        ("9", "Бунель Татьяна Васильевна", "II · Мать (урожд. Бунель)", "линия д. Ефимовичи", "Даты рожд., фамилия"),
        ("10", "Бунель Василий Васильевич", "II · Дядя (брат матери)", "линия д. Ефимовичи", "Даты, супруга, дети"),
        ("11", "Бунель Вячеслав Васильевич", "II · Дядя (брат матери)", "линия д. Ефимовичи", "Даты, имя супруги"),
        ("12", "Винничек Евгения Васильевна", "II · Тётя (урожд. Бунель)", "линия д. Ефимовичи", "Даты жизни, внуки"),
        ("13", "Винничек Борис", "II · Дядя по свойству (муж Евгении)", "линия д. Ефимовичи", "Отчество, даты, истоки"),
        ("14", "Марунов Иван Александрович", "III · Отчим отца (2-й муж)", "г. Сафоново, Смол. обл.", "Даты, ВОВ, год брака"),
        ("15", "Марунова Нина Андреевна", "III · Бабушка (ур. Хмыз, Захар.)", "д. Большое Стиклево", "Даты, родня Хмыз"),
        ("16", "Захаревич Михаил [Петрович?]", "III · Дед по отцу (1-й муж)", "Б. Стиклево · Сувалки (173 сд)", "Сверить отч. и 1917 г.р."),
        ("17", "Бунель Василий Александрович", "III · Дед по матери", "Ефимовичи · 1918, 43 зсп", "Дата смерти, часть, плен"),
        ("18", "Бунель Иван Александрович", "III · Двоюродн. дед (брат Василия)", "линия д. Ефимовичи", "Даты, ВОВ, потомки"),
        ("19", "Бунель Владимир Александрович", "III · Двоюродн. дед (брат Василия)", "линия д. Ефимовичи", "Даты, ВОВ, потомки"),
        ("20", "Бунель Фёдор Александрович", "III · Двоюродн. дед (брат Василия)", "линия д. Ефимовичи", "Даты, ВОВ, потомки"),
        ("21", "Адамович Мария", "III · Бабушка по матери (ур. Адам.)", "д. Ефимовичи (Клецкий р-н)", "Отчество, даты, родня"),
        ("22", "Адамович Николай", "III · Двоюродн. дед (брат Марии)", "жил в д. Счасновичи", "Отчество, даты, семья"),
        ("?", "Адамович [имя неизвестно]", "III · Брат/сестра М. Адамович", "линия Ефим. / Счасновичи", "Установить имя и судьбу"),
        ("23", "Бунель Александр", "IV · Прадед (отец 4 бр. Бунель)", "д. Ефимовичи (предп.)", "Отчество, даты, супруга"),
        ("?", "Хмыз Андрей (зацепка)", "IV · Прадед по отцу (?)", "отец Нины Андреевны", "Даты жизни, супруга"),
        ("?", "Захаревич Пётр (гипотеза ЦАМО)", "IV · Возможн. прадед по отцу", "по отч. М. П. и И. П. (ЦАМО)", "Подтвердить по семье"),
    ]

    ry = ty - 16
    row_h = 20.6
    for idx, rdata in enumerate(table_rows):
        is_clue = rdata[0] == "?"
        bg = GOLD_BG if is_clue else (CARD_BG if idx % 2 == 0 else CARD_BG_SOFT)
        c.setFillColor(bg)
        c.setStrokeColor(RULE_LINE)
        c.setLineWidth(0.35)
        c.rect(x, ry - row_h, w, row_h, stroke=1, fill=1)

        cx_pos = x
        for col_i, ((_, cw), val) in enumerate(zip(cols, rdata)):
            font = (
                "PTSans-Bold"
                if col_i == 0 or (col_i == 1 and not is_clue)
                else ("Lora-Italic" if is_clue else "PTSans-Regular")
            )
            col = GOLD if is_clue and col_i == 0 else (INK if col_i <= 2 else INK_MUTED)
            draw_left_wrapped(c, val, cx_pos + 3.5, ry - 7.8, font, 6.75, cw - 6, 7.8, color=col)
            cx_pos += cw
        ry -= row_h

    # Section 2: 3 Region Cards side-by-side at bottom (54..190)
    reg_styles = [
        (PATERNAL_ACCENT, PATERNAL_BG, PATERNAL_BORDER),
        (MATERNAL_ACCENT, MATERNAL_BG, MATERNAL_BORDER),
        (MARUNOV_ACCENT, MARUNOV_BG, MARUNOV_BORDER),
    ]
    c.setFont("PTSans-Bold", 7.8)
    c.setFillColor(FOREST_DEEP)
    c.drawString(x, 194, "Историко-географическая панорама (3 региона истоков):")

    box_h = 132
    for idx, reg in enumerate(data["regions"]):
        acc, bg_c, brd = reg_styles[idx]
        rx = x + idx * (col3_w + 8)
        c.setFillColor(bg_c)
        c.setStrokeColor(brd)
        c.setLineWidth(0.75)
        c.roundRect(rx, 54, col3_w, box_h, 5, stroke=1, fill=1)
        c.setFillColor(acc)
        c.roundRect(rx, 54, 4, box_h, 2, stroke=0, fill=1)

        next_y = draw_left_wrapped(c, reg["name"], rx + 9, 54 + box_h - 11, "PTSans-Bold", 7.4, col3_w - 14, 8.5, color=acc)
        next_y = draw_left_wrapped(c, reg["admin"], rx + 9, next_y - 0.5, "PTSans-Italic", 6.2, col3_w - 14, 7.2, color=INK_MUTED)
        end_y = draw_left_wrapped(c, reg["notes"], rx + 9, next_y - 2.5, "Lora-Regular", 6.25, col3_w - 14, 7.35, color=INK)
        if end_y < 54:
            print(f"WARNING: clipped region card {reg['name']} (end_y={end_y:.1f})")

    c.restoreState()
    c.showPage()


def build_page_7_military_archives(c, data):
    draw_page_background(
        c, W_P, H_P, page_num=7, total_pages=TOTAL_PAGES,
        header_title="Итоги поиска в ЦАМО, ПМВ (1914.svrt.ru) и аудит ЗАГС / метрических / камеральных баз"
    )

    x = 34
    w = W_P - 68
    leads = data["archive_leads"]

    # Section 1: Confirmed / high-confidence matches on direct grandfathers
    draw_section_banner(
        c, x, H_P - 66, w,
        "1. Документы ЦАМО по обоим дедушкам (ОБД «Мемориал»)",
        "Впервые найденные номера фондов, описей, дел и частей",
        FOREST_DEEP,
    )

    # Card 1: Vasily Aleksandrovich Bunel
    cy = H_P - 80
    h1 = 84
    c.saveState()
    c.setFillColor(MATERNAL_BG)
    c.setStrokeColor(MATERNAL_BORDER)
    c.setLineWidth(0.9)
    c.roundRect(x, cy - h1, w, h1, 6, stroke=1, fill=1)
    c.setFillColor(MATERNAL_ACCENT)
    c.roundRect(x, cy - h1, 5, h1, 2, stroke=0, fill=1)
    c.setFont("Cormorant-Bold", 11.6)
    c.setFillColor(INK)
    c.drawString(x + 12, cy - 14.5, "Бунель Василий Александрович (1918 г.р.) — ПОДТВЕРЖДЕНО ПО ВПП ЦАМО")
    c.setFont("PTSans-Bold", 7.2)
    c.setFillColor(MATERNAL_ACCENT)
    c.drawString(x + 12, cy - 25.5, "ОБД «Мемориал» ID 1986566671 · ЦАМО, ф. 8322, оп. 101476, д. 40 (Военно-пересыльные пункты)")
    body1 = (
        "Место рождения: БССР, Барановичская обл., Клецкий р-н, д. Ефимовичи. Призван 13.10.1944 Клецким РВК, рядовой, "
        "направлен в 43-й запасный стрелковый полк 5-й зсд (прибыл не ранее 26.10.1944). После освобождения Западной Беларуси "
        "Клецкий РВК направил через ЗП уроженцев деревни (в тот же день в 43 зсп призван односельчанин Бунель Адам Иосифович). "
        "Запрос в ЦАМО по 43 зсп даст ключ к точной боевой части и обстоятельствам плена."
    )
    end1 = draw_left_wrapped(c, body1, x + 12, cy - 37.5, "Lora-Regular", 7.45, w - 22, 9.0, color=INK)
    if end1 < cy - h1:
        print(f"WARNING: clipped p7 card1 (end={end1:.1f}, min={cy - h1:.1f})")
    c.restoreState()

    # Card 2: Mikhail Petrovich Zakharevich
    cy2 = cy - h1 - 9
    h2 = 114
    c.saveState()
    c.setFillColor(PATERNAL_BG)
    c.setStrokeColor(PATERNAL_BORDER)
    c.setLineWidth(0.9)
    c.roundRect(x, cy2 - h2, w, h2, 6, stroke=1, fill=1)
    c.setFillColor(PATERNAL_ACCENT)
    c.roundRect(x, cy2 - h2, 5, h2, 2, stroke=0, fill=1)
    t2 = "Захаревич Михаил Петрович (1917 — 23.10.1944) — НАЙДЕН В 2 ДЕЛАХ ЦАМО (НА СВЕРКУ)"
    t2_sz = 11.4
    while t2_sz > 8.6 and pdfmetrics.stringWidth(t2, "Cormorant-Bold", t2_sz) > (w - 22):
        t2_sz -= 0.3
    c.setFont("Cormorant-Bold", t2_sz)
    c.setFillColor(INK)
    c.drawString(x + 12, cy2 - 14.5, t2)
    c.setFont("PTSans-Bold", 7.15)
    c.setFillColor(PATERNAL_ACCENT)
    c.drawString(x + 12, cy2 - 25.5, "ОБД ID 1989449643 (ВПП 199 зсп: ф. 8495, оп. 76116, д. 23) и ID 4240927 / 504240927 (173 сд: ф. 58, оп. 18003, д. 301)")
    body2 = (
        "1) В деле ВПП записан с опечаткой как Захарович Михаил Петрович, 1917 г.р., д. Б. Стиклево, сержант, прибыл 29.07.1944 в 199 зсп "
        "от призывной комиссии к-на Лапина (вместе с односельчанином Хмызом Фёдором Даниловичем, 1918 г.р.). "
        "2) В донесении 173 сд: Захаревич Михаил Петрович, 1917 г.р., дер. Б.-Стекольное [искажение Б. Стиклево], Минский РВК, красноармеец, "
        "убит 23.10.1944 (в день взятия г. Сувалки!), первичное захоронение — Польша, Сувалкский пов., д. Кшивулька, 100 м сев. "
        "(ныне воинское кладбище на ул. Миколая Рея в г. Сувалки). Необходимо сверить отчество «Петрович» и 1917 г.р.; на скане ID 4240718 может быть указана жена."
    )
    end2 = draw_left_wrapped(c, body2, x + 12, cy2 - 37.5, "Lora-Regular", 7.45, w - 22, 9.0, color=INK)
    if end2 < cy2 - h2:
        print(f"WARNING: clipped p7 card2 (end={end2:.1f}, min={cy2 - h2:.1f})")
    c.restoreState()

    # Section 2: Village & regional candidates (5 blocks)
    s2_y = cy2 - h2 - 17
    draw_section_banner(
        c, x, s2_y, w,
        "2. Односельчане и региональные зацепки (ЦАМО и ПМВ)",
        "д. Ефимовичи, д. Б. Стиклево и Сафоновский р-н",
        GOLD,
    )
    cand_top = s2_y - 11
    cand_h = 224
    c.saveState()
    c.setFillColor(GOLD_BG)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.roundRect(x, cand_top - cand_h, w, cand_h, 6, stroke=1, fill=1)

    yy = cand_top - 14
    for cand in leads["village_candidates"]:
        c.setFont("PTSans-Bold", 7.65)
        c.setFillColor(FOREST_DEEP)
        c.drawString(x + 11, yy, f"• {cand['name']} ({cand['birth_year']} г.р.) — {cand['place']}")
        next_y = draw_left_wrapped(c, cand["details"], x + 18, yy - 10.2, "Lora-Regular", 7.35, w - 30, 8.9, color=INK)
        yy = next_y - 5.2
    if yy + 5.2 < cand_top - cand_h:
        print(f"WARNING: clipped p7 candidates (yy={yy:.1f}, min={cand_top - cand_h:.1f})")
    c.restoreState()

    # Section 3: Audit of ZAGS, cameral & church databases (why open dates are absent)
    s3_y = cand_top - cand_h - 17
    draw_section_banner(
        c, x, s3_y, w,
        "3. Аудит ЗАГС, церковных книг, камеральных фондов и открытых баз",
        "Почему точные даты I–III поколений не открыты онлайн",
        MARUNOV_ACCENT,
    )
    chk_top = s3_y - 11
    chk_h = chk_top - 52
    c.saveState()
    c.setFillColor(CARD_BG)
    c.setStrokeColor(MARUNOV_BORDER)
    c.setLineWidth(0.8)
    c.roundRect(x, 52, w, chk_h, 6, stroke=1, fill=1)

    chk_y = chk_top - 15
    for line in leads["checked_no_match"]:
        next_y = draw_left_wrapped(c, f"— {line}", x + 11, chk_y, "Lora-Regular", 7.65, w - 22, 9.4, color=INK)
        chk_y = next_y - 6.5
    if chk_y + 6.5 < 52:
        print(f"WARNING: clipped p7 audit block (chk_y={chk_y:.1f})")
    c.restoreState()

    c.showPage()


def build_page_8_research_guide(c, data):
    draw_page_background(
        c, W_P, H_P, page_num=8, total_pages=TOTAL_PAGES,
        header_title="Вопросы к родным, точные фонды НИАБ / ГАМн / ГАСО / ЗАГС и рабочая анкета"
    )

    x = 34
    w = W_P - 68

    # Block 1: Priority questions
    draw_section_banner(
        c, x, H_P - 66, w,
        "1. Приоритетные вопросы к родственникам (с учётом находок ЦАМО)",
        "Для подтверждения архивных дел и достройки ветвей",
        FOREST_DEEP,
    )

    priorities = [
        ("Сверка находки по деду Михаилу Захаревичу и роду Хмыз (д. Б. Стиклево):",
         "Подтвердить отчество «Петрович» и 1917 г.р.; не был ли Захаревич Иван Петрович (1899 г.р.) его старшим братом? Кем приходятся Хмызы Фёдор Данилович (1918), Василий Фёдорович (1918), Виктор Фёдорович (1910)?"),
        ("Ветвь Бунель (д. Ефимовичи) и братья Василий, Иван, Владимир, Фёдор:",
         "Выяснить родство с односельчанами Бунель Адамом Иосифовичем (1909–1945) и Константином Мартыновичем (1913); год первого призыва/плена В. А. Бунеля (1918 г.р.) и даты жизни братьев Ивана, Владимира и Фёдора."),
        ("Ветвь Адамович (д. Ефимовичи и д. Счасновичи) и семья Винничек:",
         "Имя забытого брата/сестры Марии Адамович, её отчество; уточнить локализацию «д. Счасновичи» (ср. д. Чановичи / д. Чаша), отчество Бориса Винничека, даты семей Виталия, Дениса Бунель и Анатолия Винничека."),
        ("Ветвь Марунов (г. Сафоново) и II брак Нины Андреевны:",
         "Год 2-го брака с И. А. Маруновым, его даты жизни (проверить награды на «Память Народа» вручную), даты Валерия и Николая Маруновых."),
    ]

    py = H_P - 82
    for title, desc in priorities:
        c.saveState()
        c.setFillColor(GOLD)
        c.circle(x + 5, py - 3, 2.2, stroke=0, fill=1)
        c.setFont("PTSans-Bold", 7.55)
        c.setFillColor(FOREST_DEEP)
        c.drawString(x + 13, py - 5.0, title)
        next_y = draw_left_wrapped(c, desc, x + 13, py - 14.5, "Lora-Regular", 7.15, w - 16, 8.5, color=INK)
        py = next_y - 3.6
        c.restoreState()

    # Block 2: Exact archival fonds & ZAGS rules
    draw_section_banner(
        c, x, py - 5, w,
        "2. Точный архивный путеводитель (церковные, камеральные, ЗАГС)",
        "Шифры НИАБ, ГАМн, ГАСО и Закон РБ № 163-З",
        MATERNAL_ACCENT,
    )
    ay = py - 17
    box_h = 196
    c.saveState()
    c.setFillColor(CARD_BG)
    c.setStrokeColor(MATERNAL_BORDER)
    c.setLineWidth(0.8)
    c.roundRect(x, ay - box_h, w, box_h, 6, stroke=1, fill=1)

    ty = ay - 12
    for fond in data["archive_leads"]["archival_fonds"]:
        c.setFont("PTSans-Bold", 7.45)
        c.setFillColor(MATERNAL_ACCENT)
        c.drawString(x + 11, ty, f"• {fond['region']}:")
        ny1 = draw_left_wrapped(c, f"Церкви/ревизии: {fond['church']}", x + 17, ty - 9.6, "Lora-Regular", 7.0, w - 28, 8.2, color=INK)
        ny2 = draw_left_wrapped(c, f"Камеральные/ЗАГС: {fond['cameral_zags']}", x + 17, ny1 - 1.0, "Lora-Regular", 7.0, w - 28, 8.2, color=INK)
        ty = ny2 - 4.2

    c.setFont("PTSans-Bold", 7.45)
    c.setFillColor(PATERNAL_ACCENT)
    c.drawString(x + 11, ty, "• Порядок обращения в ЗАГС (РБ и РФ), ЦАМО и Польшу:")
    zags_rule = (
        "По Закону РБ № 163-З от 18.04.2022 (и ФЗ-143 РФ) акты ЗАГС хранятся 100 лет и выдаются только по заявлению родственников "
        "с цепочкой свидетельств (Минский р-н, Клецкий р-н, облархив ЗАГС Минской обл., ЗАГС г. Сафоново). В ЦАМО/ОБД открыть скан "
        "ID 4240718 (с. 35) по М. П. Захаревичу и проверить Польский Красный Крест (перезахоронение в г. Сувалки, ul. M. Reja)."
    )
    ny_end = draw_left_wrapped(c, zags_rule, x + 17, ty - 9.6, "Lora-Regular", 6.95, w - 28, 8.2, color=INK)
    if ny_end < ay - box_h:
        print(f"WARNING: clipped p8 archive box (ny_end={ny_end:.1f}, min={ay - box_h:.1f})")
    c.restoreState()

    # Block 3: Printable Interview Worksheet
    wy = ay - box_h - 15
    draw_section_banner(
        c, x, wy, w,
        "3. Рабочая таблица для записи сведений",
        "Заполните от руки в беседе с родными или после ответа из ЗАГС / архивов",
        PATERNAL_ACCENT,
    )

    table_top = wy - 12
    wcols = [
        ("ФИО (и девичья фамилия)", 168),
        ("Кем приходится", 96),
        ("Даты жизни", 90),
        ("Место / Примечания", w - 354),
    ]
    c.saveState()
    c.setFillColor(PATERNAL_ACCENT)
    c.rect(x, table_top - 15, w, 15, stroke=0, fill=1)
    cx_pos = x
    c.setFont("PTSans-Bold", 7.2)
    c.setFillColor(colors.white)
    for cname, cw in wcols:
        c.drawString(cx_pos + 4, table_top - 10.5, cname)
        cx_pos += cw

    row_y = table_top - 15
    row_h = 18.5
    num_rows = max(4, int((row_y - 48) // row_h))
    for i in range(num_rows):
        c.setFillColor(CARD_BG if i % 2 == 0 else PARCHMENT)
        c.setStrokeColor(RULE_LINE)
        c.setLineWidth(0.5)
        c.rect(x, row_y - row_h, w, row_h, stroke=1, fill=1)
        cx_pos = x
        for _, cw in wcols[:-1]:
            cx_pos += cw
            c.line(cx_pos, row_y, cx_pos, row_y - row_h)
        row_y -= row_h

    c.restoreState()
    c.showPage()


def main():
    register_fonts()
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    c = canvas.Canvas(str(OUT_PDF), pagesize=A4)
    c.setTitle(data["title"])
    c.setAuthor("Семейный архив Захаревич — Бунель")
    c.setSubject("Генеалогическое древо, альбом и архивный аудит ЦАМО / НИАБ / ГАМн / ГАСО / ЗАГС (Редакция 4.0)")

    build_page_1_cover(c, data)
    c.setPageSize(landscape(A4))
    build_page_2_tree(c, data)
    c.setPageSize(A4)
    build_page_3_gen1_and_parents(c, data)
    build_page_4_gen2_mat_and_gen3_pat(c, data)
    build_page_5_gen3_mat_and_gen4(c, data)
    build_page_6_index_and_regions(c, data)
    build_page_7_military_archives(c, data)
    build_page_8_research_guide(c, data)

    c.save()
    print(f"Generated PDF: {OUT_PDF} ({OUT_PDF.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
