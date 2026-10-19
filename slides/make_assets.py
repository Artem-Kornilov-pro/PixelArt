"""Готовит картинки для презентаций: python slides/make_assets.py (исходники лежат в slides/source)."""
import shutil
from pathlib import Path
from PIL import Image
from pixelkid import pixelate

HERE = Path(__file__).parent.resolve()
SRC = HERE / "source"
OUT = HERE / "assets"
OUT.mkdir(exist_ok=True)

for name in ["m_logo.svg", "shape_crop.jpg"]:
    shutil.copy(SRC / name, OUT / name)

# Логотип ШЦТ: белый фон -> прозрачность, фиолетовая и белая версии
logo = Image.open(SRC / "logo_crop.png").convert("RGB")
alpha = logo.convert("L").point(lambda v: max(0, min(255, (255 - v) * 255 // 90)))
purple = Image.new("RGBA", logo.size, (107, 33, 214, 255)); purple.putalpha(alpha)
white = Image.new("RGBA", logo.size, (255, 255, 255, 255)); white.putalpha(alpha)
purple.save(OUT / "logo_shct.png"); white.save(OUT / "logo_shct_white.png")

def square(img, cx=0.5, cy=0.5, size=None):
    s = size or min(img.size)
    x = int(cx * img.width - s / 2); y = int(cy * img.height - s / 2)
    x = max(0, min(img.width - s, x)); y = max(0, min(img.height - s, y))
    return img.crop((x, y, x + s, y + s)).resize((768, 768), Image.Resampling.LANCZOS)

cat = Image.open(SRC / "cat.png").convert("RGB")
cat = cat.crop((40, 0, cat.width, cat.height))  # слева в исходнике кусок буквы из PDF
kids = Image.open(SRC / "hero.png").convert("RGB")
photos = {"shct": square(cat, 0.5, 0.45), "ms": square(kids, 0.6, 0.5)}

for key, photo in photos.items():
    photo.save(OUT / f"{key}_photo.png")
    for px in (6, 16, 32):
        pixelate(photo, pixel_size=px, colors=32, save_as=OUT / f"{key}_px{px}.png")
    for c in (2, 4, 8):
        pixelate(photo, pixel_size=12, colors=c, save_as=OUT / f"{key}_col{c}.png")
    for w in (16, 48, 192):                 # разрешения: маленькие настоящие картинки
        photo.resize((w, w), Image.Resampling.LANCZOS).save(OUT / f"{key}_res{w}.png")
    pixelate(photo, pixel_size=16, colors=32, upscale=False).save(OUT / f"{key}_small.png")
    # 8x8 кусочек для слайда «картинка — это числа»
    photo.crop((250, 150, 520, 420)).resize((8, 8), Image.Resampling.LANCZOS).save(OUT / f"{key}_8x8.png")
print(sorted(p.name for p in OUT.iterdir()))
