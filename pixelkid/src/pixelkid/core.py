"""Функция pixelate: фото -> пиксель-арт."""
import numpy as np
from PIL import Image

SUBPIXELS = 6          # сколько «голосующих» точек по стороне каждой клетки
MAX_WORK = 4_000_000   # предел точек в рабочей копии (чтобы большие фото не тормозили)
MAX_VOTES = 16_000_000 # предел клеток x цветов для голосования
SAMPLE = 20_000        # по скольким точкам подбираем палитру
ITERATIONS = 25
RARE_BONUS = 0.2       # бонус редким цветам при голосовании (0 -- без бонуса)


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

    cols, rows = max(1, photo.width // pixel_size), max(1, photo.height // pixel_size)

    # 1. Уменьшаем до «рабочей» копии: в каждой будущей клетке k x k точек
    k = _subpixels(cols, rows, pixel_size, colors)
    work = photo.resize((cols * k, rows * k), Image.Resampling.LANCZOS)
    pixels = np.asarray(work, dtype=np.float32).reshape(-1, 3)

    # 2. Подбираем палитру так, как цвета различает глаз (пространство Lab)
    # 3. Каждой клетке -- самый частый цвет её блока (а не размытая «средняя каша»)
    lab = _to_lab(pixels)
    cells, palette = _grid(lab, pixels, cols, rows, k, colors)
    small = Image.fromarray(palette[cells].reshape(rows, cols, 3))

    # 4. Увеличиваем обратно без размытия
    result = small.resize(photo.size, Image.Resampling.NEAREST) if upscale else small

    if save_as:
        result.save(save_as)
    return result


def _grid(lab, pixels, cols, rows, k, colors):
    """Палитра + цвет каждой клетки, причём в результате ровно `colors` цветов (если хватает).

    Редкий цвет может не победить ни в одной клетке и пропасть. Тогда подбираем
    палитру чуть больше -- пока в картинке не окажется столько цветов, сколько просили.
    """
    def attempt(n):
        labels = _nearest(lab, _kmeans(lab, n))
        cells = _vote(labels, cols, rows, k, n) if k > 1 else labels
        return len(np.unique(cells)), cells, _mean_rgb(pixels, labels, n)

    best = attempt(colors)
    n = colors
    while best[0] < colors and n < 2 * colors:
        n += colors - best[0]
        result = attempt(n)
        if result[0] > colors:          # перестарались -- оставляем то, что было
            break
        if result[0] > best[0]:
            best = result
    return best[1], best[2]


def _subpixels(cols, rows, pixel_size, colors):
    """Сколько точек на сторону клетки можно себе позволить (1 -- без голосования)."""
    if cols * rows * colors > MAX_VOTES:
        return 1
    k = min(SUBPIXELS, pixel_size)
    while k > 1 and cols * rows * k * k > MAX_WORK:
        k -= 1
    return k


def _to_lab(rgb):
    """sRGB (0..255) -> CIE Lab: в Lab расстояние между цветами похоже на то, как их видит глаз."""
    c = rgb / 255
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    # Без матричного умножения (@): в NumPy 2.0 на Mac оно печатает ложные RuntimeWarning
    r, g, b = c[:, 0], c[:, 1], c[:, 2]
    xyz = np.stack([(0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047,
                    0.2126 * r + 0.7152 * g + 0.0722 * b,
                    (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883], 1)
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[:, 1] - 16, 500 * (f[:, 0] - f[:, 1]), 200 * (f[:, 1] - f[:, 2])], 1).astype(np.float32)


def _kmeans(lab, n):
    """Палитра из n цветов: k-means, начиная с самых непохожих цветов (так нет цветов-дублей)."""
    rng = np.random.default_rng(0)   # всегда одинаковый результат для одной картинки
    sample = lab[rng.choice(len(lab), SAMPLE, replace=False)] if len(lab) > SAMPLE else lab

    centers = [sample[np.argmin(sample[:, 0])]]          # начинаем с самого тёмного
    dist = ((sample - centers[0]) ** 2).sum(1)
    for _ in range(n - 1):
        centers.append(sample[np.argmax(dist)])          # следующий -- самый непохожий
        dist = np.minimum(dist, ((sample - centers[-1]) ** 2).sum(1))
    centers = np.array(centers)

    for _ in range(ITERATIONS):
        labels = _nearest(sample, centers)
        moved = 0.0
        for i in range(n):
            members = sample[labels == i]
            if len(members):
                new = members.mean(0)
                moved = max(moved, float(np.abs(new - centers[i]).max()))
                centers[i] = new
        if moved < 0.05:
            break
    return centers


def _nearest(lab, centers):
    """Номер ближайшего цвета палитры для каждой точки (по частям, чтобы хватило памяти)."""
    c2 = (centers ** 2).sum(1)
    out = np.empty(len(lab), dtype=np.int64)
    for start in range(0, len(lab), 65536):
        part = lab[start:start + 65536]
        # NumPy 2.0 на Mac (Accelerate) печатает здесь ложные RuntimeWarning; значения Lab
        # ограничены (примерно ±130), настоящего переполнения быть не может
        with np.errstate(all="ignore"):
            dot = part @ centers.T
        out[start:start + 65536] = np.argmin(c2 - 2 * dot, 1)
    return out


def _mean_rgb(pixels, labels, n):
    """Настоящий цвет каждого номера палитры -- среднее всех его точек."""
    count = np.maximum(np.bincount(labels, minlength=n), 1)[:, None]
    sums = np.stack([np.bincount(labels, weights=pixels[:, ch], minlength=n) for ch in range(3)], 1)
    return np.clip(np.round(sums / count), 0, 255).astype(np.uint8)


def _vote(labels, cols, rows, k, n):
    """Для каждой клетки выбираем цвет, которого больше всего среди её k x k точек.

    Редкие на картинке цвета (ствол, глаза, мелкие детали) получают небольшой бонус:
    иначе тонкая линия на границе двух клеток проигрывает фону в обеих и пропадает.
    """
    y = np.arange(rows * k) // k
    x = np.arange(cols * k) // k
    block = (y[:, None] * cols + x[None, :]).ravel()
    votes = np.bincount(block * n + labels, minlength=rows * cols * n).reshape(rows * cols, n)
    share = np.maximum(np.bincount(labels, minlength=n) / len(labels), 1e-9)
    return (votes * share ** -RARE_BONUS).argmax(1)
