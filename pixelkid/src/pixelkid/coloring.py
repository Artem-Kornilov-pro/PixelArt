"""Функция coloring_pdf: фото -> цветной PDF «раскраска по номерам» в стиле МАСТЕРСАМ."""
from math import ceil
from pathlib import Path

from PIL import Image
from reportlab.lib.colors import HexColor, Color, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from .core import pixelate

# Фирменные цвета МАСТЕРСАМ (с сайта mastersam.org)
ORANGE = HexColor("#FF6A00")
ORANGE_LIGHT = HexColor("#FF8A00")
INK = HexColor("#251208")
MUTED = HexColor("#74665F")
LINE = HexColor("#F0DED0")
SOFT = HexColor("#FFF0E4")
GRID = HexColor("#C9B8AC")
NUMBER = HexColor("#8A786C")

FONTS = Path(__file__).parent / "fonts"
WIDTH, HEIGHT = A4
MARGIN = 36
LEGEND_COLUMNS = 5


def coloring_pdf(image, save_as="coloring.pdf", cells=32, colors=12, title="Пиксель-раскраска"):
    """Делает цветной PDF «раскраска по номерам».

    image   -- путь к файлу ("photo.jpg") или картинка Pillow (Image).
    save_as -- куда сохранить PDF.
    cells   -- сколько клеток в ширину (от 4 до 60).
    colors  -- сколько цветов в палитре (от 2 до 24).
    title   -- заголовок на листе.

    Страница 1 -- раскраска: клетки с номерами и палитра.
    Страница 2 -- ответ: как должна выглядеть готовая картинка.
    Возвращает палитру: список цветов (r, g, b), цвет номер 1 -- первый в списке.
    """
    if not 4 <= cells <= 60:
        raise ValueError("cells должен быть от 4 до 60")
    if not 2 <= colors <= 24:
        raise ValueError("colors должен быть от 2 до 24")

    photo = image.convert("RGB") if isinstance(image, Image.Image) else Image.open(image).convert("RGB")
    small = pixelate(photo, pixel_size=max(2, photo.width // cells), colors=colors, upscale=False)

    # Номер 1 -- самый частый цвет (так же нумерует приложение «Пиксель-раскраска»)
    palette = [color for _, color in sorted(small.getcolors(small.width * small.height), reverse=True)]
    numbers = [[palette.index(small.getpixel((x, y))) for x in range(small.width)] for y in range(small.height)]

    _register_fonts()
    pdf = Canvas(str(save_as), pagesize=A4)
    pdf.setTitle(title)
    pdf.setAuthor("МАСТЕРСАМ")
    pdf.setCreator("pixelkid")

    for answer in (False, True):
        _header(pdf, "Ответ" if answer else title,
                "Так выглядит готовая картинка" if answer else "Раскрась каждую клетку цветом с её номером")
        legend_top = _legend(pdf, palette)
        _grid(pdf, numbers, palette, top=HEIGHT - MARGIN - 58, bottom=legend_top + 18, answer=answer)
        _footer(pdf)
        pdf.showPage()
    pdf.save()
    return palette


def _register_fonts():
    for name in ("Regular", "Bold", "Black"):
        if f"Inter-{name}" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(f"Inter-{name}", str(FONTS / f"Inter-{name}.ttf")))


def _logo(pdf, x, y, size):
    """Логотип МАСТЕРСАМ: оранжевый квадрат с белой буквой М (как на mastersam.org)."""
    s = size / 256
    pdf.saveState()
    path = pdf.beginPath()
    path.roundRect(x + 8 * s, y + 8 * s, 240 * s, 240 * s, 58 * s)
    pdf.clipPath(path, stroke=0, fill=0)
    pdf.linearGradient(x + 36 * s, y + 232 * s, x + 220 * s, y + 24 * s, (ORANGE_LIGHT, ORANGE))
    pdf.restoreState()

    pdf.saveState()
    pdf.setStrokeColor(white)
    pdf.setLineWidth(25 * s)
    pdf.setLineCap(1)
    pdf.setLineJoin(1)
    m = pdf.beginPath()
    points = [(61, 177), (61, 81), (128, 142), (195, 81), (195, 177)]
    m.moveTo(x + points[0][0] * s, y + (256 - points[0][1]) * s)
    for px, py in points[1:]:
        m.lineTo(x + px * s, y + (256 - py) * s)
    pdf.drawPath(m, stroke=1, fill=0)
    pdf.restoreState()


def _header(pdf, title, subtitle):
    top = HEIGHT - MARGIN
    _logo(pdf, MARGIN - 2, top - 32, 34)

    # Разрядка букв живёт в состоянии PDF, поэтому ограничиваем её saveState/restoreState
    pdf.saveState()
    word = pdf.beginText(MARGIN + 38, top - 21)
    word.setFont("Inter-Black", 14)
    word.setCharSpace(1.2)
    word.setFillColor(INK)
    word.textOut("МАСТЕРСАМ")
    pdf.drawText(word)
    pdf.restoreState()

    pdf.setFillColor(INK)
    pdf.setFont("Inter-Black", 19)
    pdf.drawRightString(WIDTH - MARGIN, top - 14, title)
    pdf.setFillColor(MUTED)
    pdf.setFont("Inter-Regular", 9)
    pdf.drawRightString(WIDTH - MARGIN, top - 28, subtitle)

    # Оранжевая полоса с градиентом под шапкой
    pdf.saveState()
    bar = pdf.beginPath()
    bar.roundRect(MARGIN, top - 44, WIDTH - 2 * MARGIN, 4, 2)
    pdf.clipPath(bar, stroke=0, fill=0)
    pdf.linearGradient(MARGIN, 0, WIDTH - MARGIN, 0, (ORANGE_LIGHT, ORANGE))
    pdf.restoreState()


def _grid(pdf, numbers, palette, top, bottom, answer):
    rows, cols = len(numbers), len(numbers[0])
    cell = min((WIDTH - 2 * MARGIN) / cols, (top - bottom) / rows)
    left = (WIDTH - cols * cell) / 2
    gtop = top - (top - bottom - rows * cell) / 2   # центрируем и по высоте

    font = min(cell * 0.46, 10)
    for y, row in enumerate(numbers):
        for x, n in enumerate(row):
            cx, cy = left + x * cell, gtop - (y + 1) * cell
            if answer:
                pdf.setFillColor(Color(*(v / 255 for v in palette[n])))
                pdf.rect(cx, cy, cell, cell, stroke=0, fill=1)
            else:
                size = font if n < 9 else font * 0.85
                pdf.setFont("Inter-Regular", size)
                pdf.setFillColor(NUMBER)
                pdf.drawCentredString(cx + cell / 2, cy + cell / 2 - size * 0.36, str(n + 1))

    # Линии сетки: тонкие, каждая 10-я -- оранжевая, чтобы легче считать клетки
    for i in range(cols + 1):
        _grid_line(pdf, i, answer, left + i * cell, gtop, left + i * cell, gtop - rows * cell)
    for j in range(rows + 1):
        _grid_line(pdf, j, answer, left, gtop - j * cell, left + cols * cell, gtop - j * cell)

    pdf.setStrokeColor(ORANGE)
    pdf.setLineWidth(1.4)
    pdf.rect(left, gtop - rows * cell, cols * cell, rows * cell, stroke=1, fill=0)


def _grid_line(pdf, index, answer, x1, y1, x2, y2):
    if answer:
        pdf.setStrokeColor(white, alpha=0.35)
        pdf.setLineWidth(0.3)
    elif index % 10 == 0:
        pdf.setStrokeColor(ORANGE_LIGHT, alpha=0.7)
        pdf.setLineWidth(0.8)
    else:
        pdf.setStrokeColor(GRID)
        pdf.setLineWidth(0.35)
    pdf.line(x1, y1, x2, y2)


def _legend(pdf, palette):
    """Палитра: номер + квадратик цвета + RGB. Возвращает верхнюю границу блока."""
    rows = ceil(len(palette) / LEGEND_COLUMNS)
    item_w = (WIDTH - 2 * MARGIN - 20) / LEGEND_COLUMNS
    height = 30 + rows * 26 + 6
    bottom = MARGIN + 30
    top = bottom + height

    pdf.setFillColor(SOFT)
    pdf.setStrokeColor(LINE)
    pdf.setLineWidth(0.8)
    pdf.roundRect(MARGIN, bottom, WIDTH - 2 * MARGIN, height, 10, stroke=1, fill=1)

    pdf.setFillColor(INK)
    pdf.setFont("Inter-Black", 11)
    pdf.drawString(MARGIN + 12, top - 20, "Палитра")
    pdf.setFillColor(MUTED)
    pdf.setFont("Inter-Regular", 7.5)
    pdf.drawString(MARGIN + 66, top - 20, "номер · цвет · RGB")

    # Пиксельное украшение в углу, как на слайдах
    pdf.setFillColor(ORANGE)
    for dx, dy, s in ((0, 0, 6), (8, 0, 6), (8, -8, 6), (16, -8, 4)):
        pdf.rect(WIDTH - MARGIN - 32 + dx, top - 14 + dy, s, s, stroke=0, fill=1)

    for i, rgb in enumerate(palette):
        x = MARGIN + 10 + (i % LEGEND_COLUMNS) * item_w
        y = top - 50 - (i // LEGEND_COLUMNS) * 26
        pdf.setFillColor(INK)
        pdf.setFont("Inter-Bold", 11)
        pdf.drawRightString(x + 20, y + 5, str(i + 1))
        pdf.setFillColor(Color(*(v / 255 for v in rgb)))
        pdf.setStrokeColor(GRID)
        pdf.setLineWidth(0.6)
        pdf.roundRect(x + 26, y, 28, 18, 4, stroke=1, fill=1)
        pdf.setFillColor(MUTED)
        pdf.setFont("Inter-Regular", 6.5)
        pdf.drawString(x + 60, y + 6, "{} {} {}".format(*rgb))
    return top


def _footer(pdf):
    pdf.setFillColor(INK)
    pdf.setFont("Inter-Bold", 10)
    pdf.drawString(MARGIN, MARGIN + 6, "Имя:")
    pdf.setStrokeColor(GRID)
    pdf.setLineWidth(0.8)
    pdf.line(MARGIN + 30, MARGIN + 4, MARGIN + 230, MARGIN + 4)
    pdf.setFillColor(MUTED)
    pdf.setFont("Inter-Regular", 8)
    pdf.drawRightString(WIDTH - MARGIN, MARGIN + 6, "Сделано на Python · библиотека pixelkid · mastersam.org")
