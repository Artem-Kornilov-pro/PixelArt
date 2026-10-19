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
