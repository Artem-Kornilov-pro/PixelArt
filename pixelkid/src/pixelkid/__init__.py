"""pixelkid — превращает фото в пиксель-арт и раскраску по номерам.

    from pixelkid import pixelate, coloring_pdf
    pixelate("photo.jpg", pixel_size=12, colors=16, save_as="art.png")
    coloring_pdf("photo.jpg", save_as="coloring.pdf")
"""
from .core import pixelate
from .coloring import coloring_pdf

__version__ = "0.3.0"
__all__ = ["pixelate", "coloring_pdf"]
