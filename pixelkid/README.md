# pixelkid

Превращает любое фото в пиксель-арт **одной функцией** — и в цветную PDF-раскраску по номерам. Сделано для мастер-классов по Python (возраст 11–17).

```python
from pixelkid import pixelate

pixelate("photo.jpg", pixel_size=12, colors=16, save_as="art.png")
```

## Установка

```
pip install pixelkid
```

Нужен Python 3.8+. Вместе с `pixelkid` автоматически установятся Pillow и reportlab.

## Функция `pixelate`

```python
pixelate(image, pixel_size=12, colors=32, save_as=None, upscale=True)
```

| Параметр | Что это | По умолчанию |
|---|---|---|
| `image` | Путь к файлу (`"photo.jpg"`) или картинка Pillow (`Image`) | — |
| `pixel_size` | Размер «большого пикселя» в обычных пикселях, от 2. Чем больше — тем крупнее квадраты | `12` |
| `colors` | Сколько цветов оставить, от 2 до 256 | `32` |
| `save_as` | Куда сохранить результат. Если не указать — файл не создаётся | `None` |
| `upscale` | `True` — картинка исходного размера с крупными пикселями. `False` — маленькая картинка, где 1 точка = 1 большой пиксель | `True` |

**Возвращает** картинку Pillow (`PIL.Image.Image`), поэтому её можно показать (`.show()`), сохранить (`.save(...)`) или обработать дальше.

**Ошибки.** Если `pixel_size` меньше 2 или `colors` вне диапазона 2–256, функция выбросит `ValueError`.

## Функция `coloring_pdf`

```python
coloring_pdf(image, save_as="coloring.pdf", cells=32, colors=12, title="Пиксель-раскраска")
```

Делает цветной PDF «раскраска по номерам» (A4) в стиле МАСТЕРСАМ.

| Параметр | Что это | По умолчанию |
|---|---|---|
| `image` | Путь к файлу или картинка Pillow | — |
| `save_as` | Куда сохранить PDF | `"coloring.pdf"` |
| `cells` | Сколько клеток в ширину, от 4 до 60 | `32` |
| `colors` | Сколько цветов в палитре, от 2 до 24 | `12` |
| `title` | Заголовок на листе | `"Пиксель-раскраска"` |

- **Страница 1** — раскраска: клетки с номерами, палитра «номер · цвет · RGB», строка для имени.
- **Страница 2** — ответ: как выглядит готовая картинка.

**Возвращает** палитру — список цветов `(r, g, b)`. Цвет с номером 1 — первый в списке (самый частый на картинке).

## Примеры

```python
from pixelkid import pixelate, coloring_pdf

# 1. Просто показать результат
pixelate("cat.jpg").show()

# 2. Очень крупные пиксели и всего 4 цвета
pixelate("cat.jpg", pixel_size=30, colors=4, save_as="cat_8bit.png")

# 3. Пять версий одного фото
for size in (4, 8, 16, 24, 32):
    pixelate("cat.jpg", pixel_size=size, save_as=f"cat_{size}.png")

# 4. Раскраска по номерам для печати
coloring_pdf("cat.jpg", save_as="cat_coloring.pdf", cells=24, colors=8)

# 5. Маленькая «сетка» для своих игр и раскрасок
grid = pixelate("cat.jpg", pixel_size=16, upscale=False)
print(grid.size)   # например, (48, 48): можно перебрать каждую клеточку
```

## Как это работает

1. **Уменьшаем** фото: каждый квадрат `pixel_size × pixel_size` становится одной точкой.
2. **Оставляем** только `colors` цветов (`quantize`).
3. **Увеличиваем** обратно методом `NEAREST` — он просто копирует цвет и не размывает границы.

## Разработка

```
pip install -e .[dev]    # или: pip install -e . pytest
pytest
python -m build          # собрать пакет в папку dist/
```

## Лицензия

MIT. Шрифт Inter в папке `fonts` — SIL Open Font License 1.1 (`fonts/OFL.txt`).
