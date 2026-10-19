# pixelkid

Превращает любое фото в пиксель-арт **одной функцией**. Сделано для мастер-классов по Python (возраст 11–17).

```python
from pixelkid import pixelate

pixelate("photo.jpg", pixel_size=12, colors=16, save_as="art.png")
```

## Установка

```
pip install pixelkid
```

Нужен Python 3.8+. Вместе с `pixelkid` автоматически установится Pillow.

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

## Примеры

```python
from pixelkid import pixelate

# 1. Просто показать результат
pixelate("cat.jpg").show()

# 2. Очень крупные пиксели и всего 4 цвета
pixelate("cat.jpg", pixel_size=30, colors=4, save_as="cat_8bit.png")

# 3. Пять версий одного фото
for size in (4, 8, 16, 24, 32):
    pixelate("cat.jpg", pixel_size=size, save_as=f"cat_{size}.png")

# 4. Маленькая «сетка» для своих игр и раскрасок
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

MIT
