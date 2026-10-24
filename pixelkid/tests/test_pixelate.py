from PIL import Image
import pytest
from pixelkid import pixelate


def make_photo():
    return Image.effect_mandelbrot((200, 150), (-2, -1.5, 1, 1.5), 30)


def test_keeps_size():
    assert pixelate(make_photo(), pixel_size=10).size == (200, 150)


def test_small_image():
    assert pixelate(make_photo(), pixel_size=10, upscale=False).size == (20, 15)


def test_color_limit():
    result = pixelate(make_photo(), pixel_size=5, colors=4)
    assert len(result.getcolors(10000)) <= 4


def test_save(tmp_path):
    path = tmp_path / "art.png"
    pixelate(make_photo(), save_as=str(path))
    assert path.exists()


def test_bad_values():
    with pytest.raises(ValueError):
        pixelate(make_photo(), pixel_size=1)
    with pytest.raises(ValueError):
        pixelate(make_photo(), colors=1)


def test_same_result_every_time():
    # приложение и PDF-раскраска должны получить одну и ту же картинку
    a = pixelate(make_photo(), pixel_size=8, colors=8, upscale=False)
    b = pixelate(make_photo(), pixel_size=8, colors=8, upscale=False)
    assert a.tobytes() == b.tobytes()


def test_no_duplicate_colors():
    # раньше в палитре бывали почти одинаковые цвета -- теперь каждый цвет заметно отличается
    result = pixelate(make_photo().convert("RGB"), pixel_size=5, colors=8, upscale=False)
    palette = [color for _, color in result.getcolors(10000)]
    for i, a in enumerate(palette):
        for b in palette[i + 1:]:
            assert sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5 > 10


def test_any_image_mode():
    for mode in ("L", "RGBA", "P"):
        photo = make_photo().convert("RGB").convert(mode)
        assert pixelate(photo, pixel_size=10, upscale=False).size == (20, 15)


def test_tiny_image():
    assert pixelate(Image.new("RGB", (1, 1), "red"), pixel_size=2, colors=256).size == (1, 1)


def test_thin_line_on_cell_border_is_kept():
    # тёмная линия шириной 10 px лежит ровно на границе двух клеток (по 5 px в каждой)
    photo = Image.new("RGB", (120, 120), "white")
    photo.paste((40, 40, 40), (55, 0, 65, 120))
    grid = pixelate(photo, pixel_size=12, colors=2, upscale=False)
    for y in range(grid.height):
        assert grid.getpixel((4, y))[0] < 128 or grid.getpixel((5, y))[0] < 128
