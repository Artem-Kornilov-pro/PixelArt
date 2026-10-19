"""pixelkid — превращает фото в пиксель-арт одной функцией.

    from pixelkid import pixelate
    pixelate("photo.jpg", pixel_size=12, colors=16, save_as="art.png")
"""
from PIL import Image

__version__ = "0.1.0"
__all__ = ["pixelate"]


def pixelate(image, pixel_size=12, colors=32, save_as=None, upscale=True):
    """Делает из фотографии пиксель-арт.

    image      -- путь к файлу ("photo.jpg") или картинка Pillow (Image).
    pixel_size -- размер одного «большого пикселя» в обычных пикселях (2 и больше).
    colors     -- сколько цветов оставить (от 2 до 256).
    save_as    -- куда сохранить результат ("art.png"). Если не нужно -- не указывай.
    upscale    -- True: вернуть картинку исходного размера с крупными пикселями;
                  False: вернуть маленькую картинку, где 1 точка = 1 большой пиксель.

    Возвращает картинку Pillow (Image).
    """
    if pixel_size < 2:
        raise ValueError("pixel_size должен быть 2 или больше")
    if not 2 <= colors <= 256:
        raise ValueError("colors должен быть от 2 до 256")

    if isinstance(image, Image.Image):
        photo = image.convert("RGB")
    else:
        photo = Image.open(image).convert("RGB")

    # 1. Уменьшаем: каждый квадрат pixel_size x pixel_size станет одной точкой
    small_size = (max(1, photo.width // pixel_size), max(1, photo.height // pixel_size))
    small = photo.resize(small_size, Image.Resampling.LANCZOS)

    # 2. Оставляем только нужное количество цветов
    small = small.quantize(colors=colors).convert("RGB")

    # 3. Увеличиваем обратно без размытия
    result = small.resize(photo.size, Image.Resampling.NEAREST) if upscale else small

    if save_as:
        result.save(save_as)
    return result
