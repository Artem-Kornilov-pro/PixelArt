"""Собирает две презентации (ШЦТ и МАСТЕРСАМ) в PDF из одного набора слайдов.

Запуск из папки First_master_class:
    python slides/build_slides.py
Нужны: playwright (+ playwright install chromium) и Pillow.
"""
import asyncio
from pathlib import Path
from PIL import Image

HERE = Path(__file__).parent.resolve()

THEMES = {
    "shct": dict(
        key="shct", out="presentation_shct", font="Open Sans:wght@400;600;700;800",
        logo='<img class="logo" src="assets/logo_shct.png">',
        logo_white='<img class="logo" src="assets/logo_shct_white.png">',
        courses="Продолжай изучать Python: игры, боты, нейросети — всё начинается с таких маленьких проектов.",
    ),
    "ms": dict(
        key="ms", out="presentation_mastersam", font="Inter:wght@400;600;700;800;900",
        logo='<div class="logo"><img src="assets/m_logo.svg"><span>МАСТЕРСАМ</span></div>',
        logo_white='<div class="logo"><img src="assets/m_logo.svg"><span>МАСТЕРСАМ</span></div>',
        courses="Python (12–17 лет) · Python + ИИ (14–17 лет) · нейросети и ИИ-агенты",
    ),
}

CSS = """
@page { size: 1440px 810px; margin: 0 }
* { box-sizing: border-box; margin: 0; padding: 0 }
body { font-family: var(--font), Arial, sans-serif; color: var(--ink); background: #fff }
.slide { width: 1440px; height: 810px; position: relative; overflow: hidden; page-break-after: always;
         background: var(--bg); padding: 0 72px }
.logo { position: absolute; left: 64px; top: 38px; height: 56px; z-index: 5 }
h1 { font-size: 92px; line-height: 1.04; font-weight: var(--hw); letter-spacing: -1px }
h2 { font-size: 58px; line-height: 1.1; font-weight: var(--hw); position: absolute; left: 72px; top: 120px; z-index: 3 }
em { font-style: normal; color: var(--accent) }
.lead { font-size: 30px; line-height: 1.4; font-weight: 600 }
.body { position: absolute; left: 72px; right: 72px; top: 215px; bottom: 50px }
.row { display: flex; gap: 28px; height: 100% }
.col { display: flex; flex-direction: column; gap: 22px }
.card { background: var(--card); border: var(--cardborder); border-radius: var(--radius); padding: 28px 30px;
        box-shadow: var(--shadow); flex: 1; position: relative }
.card h3 { font-size: 30px; font-weight: 800; margin-bottom: 10px; line-height: 1.15 }
.card p, .txt { font-size: 24px; line-height: 1.38; font-weight: 600; color: var(--text) }
.big .card p { font-size: 28px } .big .card h3 { font-size: 32px } .big .card { align-self: flex-start; min-height: 400px }
.sm p { font-size: 21px } .sm h3 { font-size: 26px; margin-bottom: 6px }
.num { width: 64px; height: 64px; border-radius: 50%; background: var(--grad); color: #fff; font-weight: 800;
       font-size: 32px; display: flex; align-items: center; justify-content: center; margin-bottom: 18px }
.px { image-rendering: pixelated }
.img { border-radius: 24px; display: block; box-shadow: var(--shadow) }
.chip { display: inline-block; background: var(--soft); color: var(--accent); font-weight: 800; font-size: 22px;
        padding: 6px 16px; border-radius: 999px }
.cap { font-size: 22px; font-weight: 700; margin-top: 12px; text-align: center; line-height: 1.25 }
.code { background: #17142b; color: #e9e6ff; border-radius: 28px; padding: 30px 36px; font-family: 'JetBrains Mono', Menlo, monospace;
        font-size: 24px; line-height: 1.5; white-space: pre; box-shadow: var(--shadow) }
.code .c { color: #8f8ab8 } .code .k { color: #ff9ad5 } .code .s { color: #9be29b } .code .n { color: #ffd479 }
.arrow { font-size: 54px; font-weight: 800; color: var(--accent); align-self: center }
.grad { background: var(--grad); color: #fff }
.grad h2 { color: #fff } .grad em { color: #fff; text-decoration: underline; text-decoration-thickness: 6px }
.grad .card { background: #fff; color: var(--ink) }
.deco { position: absolute; z-index: 1 }
.pagenum { position: absolute; right: 40px; bottom: 22px; font-weight: 800; font-size: 20px; color: var(--accent); opacity: .8 }
.grad .pagenum { color: #fff }
table.px8 { border-collapse: collapse } table.px8 td { width: 54px; height: 54px; border: 2px solid rgba(255,255,255,.8) }
.phone { width: 230px; height: 409px; border-radius: 30px; border: 8px solid #111; overflow: hidden; position: relative; background: #000 }
.phone img { width: 100%; height: 100%; object-fit: cover; display: block }
.phone .play { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 60px; color: #fff; text-shadow: 0 2px 12px rgba(0,0,0,.6) }
.tr td { padding: 12px 18px; font-size: 24px; font-weight: 600; border-bottom: 2px solid var(--soft) }
.ext { white-space: nowrap; font-weight: 800; color: #fff; background: var(--grad); border-radius: 14px; padding: 6px 16px; font-size: 26px }

/* ---- ШЦТ ---- */
.t-shct { --font: 'Open Sans'; --ink: #0b0b1c; --text: #33334d; --accent: #7b2ff2; --soft: #f1e8ff; --bg: #fff; --card: #fff;
  --grad: linear-gradient(135deg, #e02cf3 0%, #7b3df5 50%, #2740ee 100%); --hw: 800; --radius: 34px;
  --cardborder: 4px solid transparent; --shadow: 0 10px 30px rgba(90,40,200,.18) }
.t-shct .card { background: linear-gradient(#fff, #fff) padding-box, var(--grad) border-box }
.t-shct .grad .card { background: linear-gradient(#fff, #fff) padding-box, linear-gradient(135deg,#fff,#fff) border-box }
.t-shct .sphere { border-radius: 50%; background: linear-gradient(135deg, #e02cf3, #3a3df5) }

/* ---- МАСТЕРСАМ ---- */
.t-ms { --font: 'Inter'; --ink: #251208; --text: #3f312b; --accent: #ff6a00; --soft: #fff0e4; --bg: #fffaf6; --card: #fff;
  --grad: linear-gradient(135deg, #ff8a00 0%, #ff6a00 100%); --hw: 900; --radius: 28px;
  --cardborder: 2px solid #f0ded0; --shadow: 0 10px 28px rgba(255,106,0,.14) }
.t-ms .logo { height: auto; top: 30px; display: flex; align-items: center; gap: 14px }
.t-ms .logo img { height: 60px }
.t-ms .logo span { font-weight: 900; font-size: 28px; letter-spacing: 1.5px; color: var(--ink) }
.t-ms .grad .logo span { color: #fff }
.t-ms .grad .logo img { outline: 4px solid #fff; border-radius: 16px }
.t-ms .pix { position: absolute; background: var(--grad); border-radius: 6px }
.t-ms .grad { background: linear-gradient(135deg, #ff8a00 0%, #ff5a00 100%) }
.t-ms .dark { background: #18100c }
"""


def photo(T, name):
    return f"assets/{T['key']}_{name}.png"


def decor(T, variant=0):
    """Маленькие украшения в углу (разные для двух стилей)."""
    if T["key"] == "shct":
        return '<div class="deco sphere" style="right:70px;top:46px;width:54px;height:54px"></div>'
    blocks = [(1330, 40, 22), (1358, 40, 22), (1358, 68, 22), (1386, 68, 14), (1330, 68, 14)]
    return "".join(f'<div class="deco pix" style="left:{x}px;top:{y}px;width:{s}px;height:{s}px"></div>' for x, y, s in blocks)


def slide(T, title, body, n, cls=""):
    logo = T["logo_white"] if cls == "grad" and T["key"] == "shct" else T["logo"]
    if cls == "grad" and T["key"] == "ms":
        logo = T["logo_white"]
    return f'''<section class="slide {cls}">{logo}{decor(T) if cls != "grad" else ""}
    <h2>{title}</h2><div class="body">{body}</div><div class="pagenum">{n}</div></section>'''


# ------------------------------------------------------------------ слайды
def s_title(T):
    p = lambda name: photo(T, name)
    if T["key"] == "shct":
        right = f'''<img class="deco" src="assets/shape_crop.jpg" style="right:0;top:0;height:810px">
        <img class="deco img px" src="{p("px16")}" style="left:690px;top:70px;width:180px;height:180px;border-radius:50%;border:8px solid #fff">'''
        logo = T["logo"]
    else:
        right = f'''<div class="deco" style="right:0;top:0;width:540px;height:810px;background:var(--grad)"></div>
        <img class="deco img" src="{p("photo")}" style="left:1010px;top:70px;width:320px;height:320px;border:8px solid #fff">
        <div class="deco" style="left:1148px;top:396px;width:44px;text-align:center;font-size:40px;line-height:40px;font-weight:900;color:#fff">↓</div>
        <img class="deco img px" src="{p("px16")}" style="left:1010px;top:440px;width:320px;height:320px;border:8px solid #fff">'''
        logo = T["logo"]
    return f'''<section class="slide">{logo}{right}
    <div style="position:absolute;left:72px;top:190px;width:{760 if T["key"]=="ms" else 800}px">
      <div class="chip" style="margin-bottom:28px">Мастер-класс по Python · 11–17 лет</div>
      <h1>Пиксель-арт<br>из <em>твоего фото</em></h1>
      <p class="lead" style="margin-top:34px">Как устроены картинки и как заставить Python рисовать пиксели</p></div></section>'''


def s_plan(T, n):
    items = [("Узнаем", "из чего состоят картинки: пиксели, разрешение, RGB"),
             ("Посмотрим", "что за пиксельные видео сейчас в TikTok"),
             ("Напишем код", "на Python: фото → пиксель-арт"),
             ("Соберём библиотеку", "и раскрасим результат в приложении")]
    cards = "".join(f'<div class="card"><div class="num">{i+1}</div><h3>{a}</h3><p>{b}</p></div>' for i, (a, b) in enumerate(items))
    return slide(T, "Что мы <em>сегодня</em> сделаем", f'<div class="row big">{cards}</div>', n)


def s_numbers(T, n):
    img = Image.open(HERE / "assets" / f"{T['key']}_8x8.png").convert("RGB")
    rows = ""
    for y in range(8):
        rows += "<tr>" + "".join("<td style='background:rgb(%d,%d,%d)'></td>" % img.getpixel((x, y)) for x in range(8)) + "</tr>"
    r, g, b = img.getpixel((3, 3))
    body = f'''<div class="row" style="align-items:center">
      <div><table class="px8" style="border-radius:20px;overflow:hidden;box-shadow:var(--shadow)">{rows}</table></div>
      <div class="col" style="flex:1;padding-left:20px">
        <p class="lead">Компьютер не видит {"котика" if T["key"] == "shct" else "людей на фото"}. Он видит <em>таблицу чисел</em>.</p>
        <p class="txt">Картинка — это сетка из маленьких клеточек. В каждой клеточке записан один цвет. Вот такой кусочек 8×8 мы увеличили из фото.</p>
        <div class="card" style="flex:none;padding:20px 26px"><p>Клеточка в 4-м ряду, 4-й столбец:<br><b style="font-size:34px;color:var(--accent)">({r}, {g}, {b})</b></p></div>
      </div></div>'''
    return slide(T, "Картинка — это <em>числа</em>", body, n)


def s_pixel(T, n):
    p = lambda name: photo(T, name)
    # увеличиваем маленькие кусочки: x1, x4, x16
    def crop(box, label):
        return f'''<div><div style="width:320px;height:320px;overflow:hidden;border-radius:24px;box-shadow:var(--shadow);position:relative">
        <img class="px" src="{p("photo")}" style="position:absolute;{box}"></div><div class="cap">{label}</div></div>'''
    body = f'''<div class="row" style="align-items:flex-start">
      {crop("width:320px;left:0;top:0", "Вся картинка")}<div class="arrow" style="margin-top:130px">→</div>
      {crop("width:1280px;left:-560px;top:-380px", "Приблизили ×4")}<div class="arrow" style="margin-top:130px">→</div>
      <div><div style="width:320px;height:320px;overflow:hidden;border-radius:24px;box-shadow:var(--shadow);position:relative"><img class="px" src="{p("res48")}" style="position:absolute;width:1280px;left:-560px;top:-380px"></div><div class="cap">Картинка 48×48: каждый квадратик — один пиксель!</div></div>
      </div>
      <div class="card" style="position:absolute;left:0;right:0;bottom:0;flex:none;padding:18px 30px"><p><b>Пиксель</b> (pixel — «picture element») — самый маленький кусочек картинки. Один квадратик = один цвет.</p></div>'''
    return slide(T, "Что такое <em>пиксель</em>", body, n)


def s_resolution(T, n):
    p = lambda name: photo(T, name)
    items = [("16", "256"), ("48", "2 304"), ("192", "36 864")]
    cols = "".join(f'''<div><img class="img px" src="{p("res"+w)}" style="width:270px;height:270px"><div class="cap">{w}×{w}<br><span style="color:var(--accent)">{c} пикселей</span></div></div>''' for w, c in items)
    body = f'''<div class="row"><div class="col" style="flex:none;width:900px"><div class="row" style="height:auto;gap:24px">{cols}</div></div>
      <div class="col" style="flex:1;gap:12px"><p class="lead" style="font-size:26px">Разрешение = сколько пикселей в ширину × в высоту.</p>
        <div class="card" style="flex:none;padding:18px 22px"><p><b>Full HD</b> 1920×1080 ≈ 2 млн пикселей (2 Мп)</p></div>
        <div class="card" style="flex:none;padding:18px 22px"><p><b>4K</b> 3840×2160 ≈ 8 млн пикселей</p></div>
        <p class="txt" style="font-size:21px">Больше пикселей — чётче, но файл тяжелее. Пиксель-арт — это когда мы <em>специально</em> выбираем маленькое разрешение.</p></div></div>'''
    return slide(T, "<em>Разрешение</em> картинки", body, n)


def s_rgb(T, n):
    def bar(name, color, val):
        return f'''<div style="display:flex;align-items:center;gap:18px"><b style="width:40px;font-size:34px">{name}</b>
        <div style="flex:1;height:34px;border-radius:20px;background:#eee"><div style="width:{val/255*100}%;height:100%;border-radius:20px;background:{color}"></div></div>
        <b style="width:60px;font-size:28px">{val}</b></div>'''
    sw = [("Красный", (255, 0, 0)), ("Жёлтый", (255, 255, 0)), ("Оранжевый", (255, 106, 0)), ("Белый", (255, 255, 255)),
          ("Чёрный", (0, 0, 0)), ("Фиолетовый", (123, 47, 242))]
    chips = "".join(f'''<div style="display:flex;align-items:center;gap:14px"><div style="width:54px;height:54px;border-radius:14px;border:3px solid #ddd;background:rgb{c}"></div>
        <div style="font-size:24px;font-weight:700;line-height:1.15">{name}<br><span style="color:var(--text);font-weight:600">({c[0]}, {c[1]}, {c[2]})</span></div></div>''' for name, c in sw)
    body = f'''<div class="row">
      <div class="card col" style="justify-content:center;gap:22px"><p class="lead" style="margin-bottom:6px">Цвет = 3 числа от 0 до 255</p>
        {bar("R", "#ff3b3b", 255)}{bar("G", "#2fbf4a", 106)}{bar("B", "#3b6bff", 0)}
        <div style="display:flex;align-items:center;gap:18px;margin-top:6px"><div style="width:80px;height:80px;border-radius:20px;background:rgb(255,106,0)"></div>
        <p class="txt">Красный 255 + зелёный 106 + синий 0 = <b>оранжевый</b></p></div></div>
      <div class="col" style="flex:none;width:520px"><div class="card" style="display:grid;grid-template-columns:1fr 1fr;gap:20px 10px">{chips}</div>
        <div class="card" style="flex:none;padding:20px 26px"><p>256 × 256 × 256 = <b style="color:var(--accent)">16 777 216</b> цветов!<br>В пиксель-арте берут всего 16–32.</p></div></div></div>'''
    return slide(T, "Цвет: <em>RGB</em>", body, n)


def s_ratio(T, n):
    shapes = [("16:9", 391, "YouTube, телевизор, экран"), ("4:3", 293, "старые мониторы и фото"), ("1:1", 220, "квадрат: аватарки, посты"),
              ("9:16", 124, "TikTok, Reels, Shorts")]
    boxes = "".join(f'''<div style="display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:12px;width:{max(w,200)}px">
        <div style="width:{w}px;height:220px;border-radius:18px;background:var(--grad);color:#fff;font-weight:800;font-size:{34 if w>150 else 24}px;display:flex;align-items:center;justify-content:center;box-shadow:var(--shadow)">{r}</div>
        <div class="cap" style="margin-top:0;font-size:20px">{d}</div></div>''' for r, w, d in shapes)
    body = f'''<div class="col" style="height:100%;justify-content:space-between"><div class="row" style="height:auto;align-items:flex-end;justify-content:space-between">{boxes}</div>
      <div class="card" style="flex:none;padding:20px 30px"><p><b>Соотношение сторон</b> = ширина : высота. Например, 1920×1080 → делим на 120 → <b>16:9</b>.
      Если растянуть фото под другое соотношение — оно исказится или обрежется.</p></div></div>'''
    return slide(T, "Соотношение <em>сторон</em>", body, n)


def s_formats(T, n):
    rows = [(".JPG / .JPEG", "Фотографии", "Маленький вес, но сжатие с потерями"),
            (".PNG", "Рисунки и пиксель-арт", "Без потерь, умеет быть прозрачным"),
            (".GIF", "Короткие анимации", "До 256 цветов — как мемы"),
            (".WEBP", "Современный формат сайтов", "Лёгкий и качественный"),
            (".SVG", "Логотипы и иконки", "Не из пикселей, а из формул — не теряет качество")]
    trs = "".join(f'<tr class="tr"><td><span class="ext">{a}</span></td><td><b>{b}</b></td><td>{c}</td></tr>' for a, b, c in rows)
    body = f'''<div class="card" style="padding:14px 30px;flex:none"><table style="width:100%;border-collapse:collapse">{trs}</table></div>
      <p class="txt" style="margin-top:18px"><b>Растровые</b> (из пикселей): JPG, PNG, GIF, WEBP. <b>Векторные</b> (из формул): SVG. Расширение — это то, что после точки в имени файла.</p>'''
    return slide(T, "Форматы и <em>расширения</em>", body, n)


def s_tiktok(T, n):
    p = lambda name: photo(T, name)
    phones = [("px32", "Пиксель-фильтр", "лицо и видео превращаются в квадратики"),
              ("col4", "8-bit версия себя", "мало цветов, как в играх 90-х"),
              ("px6", "Пиксельный переход", "картинка рассыпается на блоки")]
    ph = "".join(f'''<div style="display:flex;flex-direction:column;align-items:center;width:290px"><div class="phone"><img class="px" src="{p(i)}"><div class="play">▶</div></div>
        <div class="cap" style="color:#fff;font-size:24px">{t}</div><div class="cap" style="color:#fff;font-weight:600;font-size:19px;margin-top:4px">{d}</div></div>''' for i, t, d in phones)
    body = f'''<div class="row" style="justify-content:space-between;align-items:flex-start"><div class="row" style="flex:none;gap:34px;height:auto">{ph}</div>
      <div class="col" style="width:330px;color:#fff"><p class="lead">Здесь покажем 2–3 живых ролика из ленты.</p>
      <p style="font-size:24px;line-height:1.4;font-weight:600">Тренды меняются, а секрет один: <b>мало пикселей + мало цветов</b>. Его мы и повторим в коде.</p></div></div>'''
    return slide(T, "Пиксель-арт в <em>TikTok</em>", body, n, "grad")


def s_how(T, n):
    p = lambda name: photo(T, name)
    def step(img, label, cls="", sz=230):
        return f'<div><img class="img {cls}" src="{p(img)}" style="width:{sz}px;height:{sz}px"><div class="cap">{label}</div></div>'
    body = f'''<div class="row" style="height:auto;align-items:flex-start;justify-content:space-between">
      {step("photo", "Оригинал")}<div class="arrow" style="margin-top:90px">→</div>
      {step("res48", "1. Уменьшаем<br>(768 → 48 пикселей)", "px")}<div class="arrow" style="margin-top:90px">→</div>
      {step("small", "2. Оставляем<br>только 32 цвета", "px")}<div class="arrow" style="margin-top:90px">→</div>
      {step("px16", "3. Увеличиваем<br>БЕЗ размытия")}</div>
      <p class="txt" style="margin-top:34px">Каждый квадрат 16×16 пикселей превратился в одну точку. Потом точки снова растянули — и получились крупные пиксели.</p>'''
    return slide(T, "Как фото становится <em>пиксель-артом</em>", body, n)


def s_code(T, n):
    code = '''<span class="k">from</span> PIL <span class="k">import</span> Image

photo = Image.open(<span class="s">"photo.jpg"</span>).convert(<span class="s">"RGB"</span>)

<span class="c"># 1. Уменьшаем: квадрат 12×12 → одна точка</span>
small = photo.resize((photo.width // <span class="n">12</span>, photo.height // <span class="n">12</span>))

<span class="c"># 2. Оставляем 32 цвета</span>
small = small.quantize(colors=<span class="n">32</span>).convert(<span class="s">"RGB"</span>)

<span class="c"># 3. Увеличиваем БЕЗ размытия (NEAREST)</span>
result = small.resize(photo.size, Image.Resampling.NEAREST)
result.save(<span class="s">"pixel_art.png"</span>)'''
    body = f'''<div class="row"><div class="code" style="flex:none;width:860px;font-size:22px">{code}</div>
      <div class="col sm" style="flex:1;gap:14px"><div class="card" style="padding:16px 22px"><h3>Pillow</h3><p>Библиотека для работы с картинками. Ставится командой <b>pip install pillow</b>.</p></div>
      <div class="card" style="padding:16px 22px"><h3>12 и 32</h3><p>Меняй эти числа — и меняется стиль картинки!</p></div>
      <div class="card" style="padding:16px 22px"><h3>NEAREST</h3><p>«Ближайший сосед»: просто копирует цвет, ничего не размывает.</p></div></div></div>'''
    return slide(T, "Код на <em>Python</em>", body, n)


def s_lib(T, n):
    code = '''<span class="c"># в терминале:</span>
pip install pixelkid

<span class="c"># в программе:</span>
<span class="k">from</span> pixelkid <span class="k">import</span> pixelate

pixelate(<span class="s">"photo.jpg"</span>,
         pixel_size=<span class="n">12</span>,
         colors=<span class="n">16</span>,
         save_as=<span class="s">"art.png"</span>)'''
    rows = [("pixel_size", "размер пикселя"), ("colors", "сколько цветов"), ("save_as", "куда сохранить"), ("upscale", "вернуть маленькую картинку")]
    tr = "".join(f'<tr class="tr"><td><b>{a}</b></td><td>{b}</td></tr>' for a, b in rows)
    body = f'''<div class="row"><div class="col" style="flex:1;min-width:0"><div class="code" style="font-size:22px">{code}</div>
      <p class="txt">Библиотека — это чужой код, который подключается одной строкой. Мы только что сделали свою: всё, что мы написали, спрятано в одной функции <b>pixelate</b>.</p></div>
      <div class="card" style="flex:none;width:420px;align-self:flex-start"><h3 style="margin-bottom:6px">Параметры</h3><table style="width:100%;border-collapse:collapse">{tr}</table></div></div>'''
    return slide(T, "Наша библиотека <em>pixelkid</em>", body, n)


def s_app(T, n):
    body = f'''<div class="row" style="align-items:center"><img class="img" src="assets/app_shot.png" style="height:540px">
      <div class="col" style="flex:1"><p class="lead">Приложение <b>«Пиксель-раскраска»</b> на PyQt6.</p>
      <div class="card" style="flex:none;padding:20px 26px"><p><b>1.</b> Открой своё фото<br><b>2.</b> Выбери размер сетки и число цветов<br><b>3.</b> Раскрась клетки по номерам<br><b>4.</b> Зажми «подсказку» — увидишь ответ</p></div>
      <p class="txt">Внутри — наша функция <b>pixelate</b>. Окошки, кнопки и ползунки делает PyQt6.</p></div></div>'''
    return slide(T, "Пиксель-<em>раскраска</em>", body, n)


def s_tasks(T, n):
    tasks = [("Поменяй числа", "pixel_size от 4 до 40, colors от 2 до 64. Что нравится больше?"),
             ("Своё фото", "Попробуй селфи, питомца или любимого героя."),
             ("Сделай аватарку", "Квадратная картинка 1:1 в стиле 8-bit для соцсетей."),
             ("Челлендж ★", "Сделай 5 картинок с разным pixel_size с помощью цикла for.")]
    cards = "".join(f'<div class="card"><div class="num">{i+1}</div><h3>{a}</h3><p>{b}</p></div>' for i, (a, b) in enumerate(tasks))
    return slide(T, "Теперь <em>твоя очередь</em>", f'<div class="row big">{cards}</div>', n)


def s_end(T, n):
    return slide(T, "Что <em>дальше</em>?", f'''<div class="row"><div class="col" style="flex:1.2;justify-content:center;gap:26px">
      <p class="lead">Сегодня ты написал программу, поставил библиотеку и сделал приложение. Это и есть программирование!</p>
      <div class="card" style="flex:none;padding:22px 28px"><p>{T["courses"]}</p></div>
      <h1 style="font-size:64px">Спасибо! <em>Вопросы?</em></h1></div>
      <div class="col" style="flex:.6;align-items:center;justify-content:center"><img class="img px" src="{photo(T, "px16")}" style="width:400px;height:400px;border:8px solid #fff"></div></div>''', n)


SLIDES = [s_plan, s_numbers, s_pixel, s_resolution, s_rgb, s_ratio, s_formats, s_tiktok, s_how, s_code, s_lib, s_app, s_tasks, s_end]


def build_html(T):
    pages = [s_title(T)] + [fn(T, i + 2) for i, fn in enumerate(SLIDES)]
    fonts = f"https://fonts.googleapis.com/css2?family={T['font'].replace(' ', '+')}&family=JetBrains+Mono:wght@400;700&display=swap"
    return f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><link rel="stylesheet" href="{fonts}"><style>{CSS}</style></head><body class="t-{T["key"]}">{"".join(pages)}</body></html>'


async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        for T in THEMES.values():
            html_path = HERE / f"{T['out']}.html"
            html_path.write_text(build_html(T), encoding="utf-8")
            page = await browser.new_page(viewport={"width": 1440, "height": 810})
            await page.goto(html_path.as_uri(), wait_until="networkidle")
            await page.evaluate("document.fonts.ready")
            await page.pdf(path=str(HERE / f"{T['out']}.pdf"), width="1440px", height="810px", print_background=True)
            print("готово:", T["out"] + ".pdf")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
