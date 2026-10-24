from PIL import Image
import pytest
from pixelkid import coloring_pdf


def make_photo():
    return Image.effect_mandelbrot((200, 150), (-2, -1.5, 1, 1.5), 30).convert("RGB")


def test_creates_pdf_with_two_pages(tmp_path):
    path = tmp_path / "coloring.pdf"
    coloring_pdf(make_photo(), save_as=path, cells=20, colors=6)
    data = path.read_bytes()
    assert data.startswith(b"%PDF")
    assert b"/Count 2" in data          # раскраска + ответ


def test_palette(tmp_path):
    palette = coloring_pdf(make_photo(), save_as=tmp_path / "c.pdf", cells=20, colors=6)
    assert 2 <= len(palette) <= 6
    assert all(len(color) == 3 for color in palette)


def test_accepts_file_path(tmp_path):
    photo = tmp_path / "photo.png"
    make_photo().save(photo)
    coloring_pdf(str(photo), save_as=tmp_path / "c.pdf")
    assert (tmp_path / "c.pdf").exists()


def test_bad_values(tmp_path):
    with pytest.raises(ValueError):
        coloring_pdf(make_photo(), save_as=tmp_path / "c.pdf", cells=2)
    with pytest.raises(ValueError):
        coloring_pdf(make_photo(), save_as=tmp_path / "c.pdf", colors=30)
