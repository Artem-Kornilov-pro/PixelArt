# Документация проекта «Пиксель-арт»

Материалы мастер-класса для школы программирования (11–17 лет): код, библиотека, приложение, две презентации и конспект.

## Содержание

1. [Структура проекта](#структура-проекта)
2. [Установка](#установка)
3. [Скрипт `main.py`](#скрипт-mainpy)
4. [Библиотека `pixelkid`](#библиотека-pixelkid)
5. [Приложение «Пиксель-раскраска»](#приложение-пиксель-раскраска)
6. [Презентации](#презентации)
7. [Публикация библиотеки на PyPI](#публикация-библиотеки-на-pypi)
8. [Частые проблемы](#частые-проблемы)

## Структура проекта

```
First_master_class/
├── main.py                  скрипт для детей (использует pixelkid)
├── requirements.txt         зависимости всего проекта
├── pixelkid/                библиотека (пакет для pip)
│   ├── pyproject.toml
│   ├── README.md            описание функции
│   ├── src/pixelkid/__init__.py
│   └── tests/
├── app/pixel_paint.py       приложение «Пиксель-раскраска» (PyQt6)
├── slides/
│   ├── presentation_shct.pdf         презентация в стиле ШЦТ
│   ├── presentation_mastersam.pdf    презентация в стиле МАСТЕРСАМ
│   ├── build_slides.py               сборка обеих презентаций
│   ├── make_assets.py                подготовка картинок
│   ├── make_app_shot.py              скриншот приложения
│   ├── source/                       исходные картинки для слайдов
│   └── assets/                       готовые картинки для слайдов
└── docs/
    ├── lesson_plan.md       конспект для преподавателя
    ├── lesson_plan.pdf
    └── DOCUMENTATION.md     этот файл
```

## Установка

Нужен Python 3.9 или новее.

```bash
cd First_master_class
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Это установит Pillow, PyQt6 и библиотеку `pixelkid` с PyPI. Чтобы работать с локальной версией библиотеки, выполните `pip install -e ./pixelkid`.

**Mac и tkinter.** `main.py` использует окно выбора файла из `tkinter`. Если Python установлен через Homebrew, а запуск падает с `No module named '_tkinter'`, выполните `brew install python-tk@3.14` (версию замените на свою).

## Скрипт `main.py`

Простой скрипт, который дети запускают первым. Вся работа с картинкой — один вызов `pixelate` из библиотеки `pixelkid`:

1. Открывается окно выбора фото.
2. В терминале вводятся размер пикселя и число цветов.
3. `pixelate(...)` делает пиксель-арт и сохраняет его в `my_pixel_art.png` в текущей папке (откуда запущена программа). Результат открывается.

```bash
python main.py
```

Окна `simpledialog` и `messagebox` из `tkinter` не используются: в Tk 9 на Mac они падают с ошибкой `MacWindowStyle`.

## Библиотека `pixelkid`

Подробно: [pixelkid/README.md](../pixelkid/README.md). Кратко:

```python
from pixelkid import pixelate
pixelate("photo.jpg", pixel_size=12, colors=16, save_as="art.png")
```

Внутри три шага: уменьшить (`resize` + `LANCZOS`) → оставить N цветов (`quantize`) → увеличить без размытия (`resize` + `NEAREST`).

**Тесты:**

```bash
pip install pytest
pytest pixelkid/tests
```

## Приложение «Пиксель-раскраска»

```bash
python app/pixel_paint.py              # потом кнопка «Открыть фото»
python app/pixel_paint.py photo.jpg    # сразу с фото
```

| Элемент | Что делает |
|---|---|
| Открыть фото | Выбор файла (PNG, JPG, WEBP) |
| Клеток в ширину | От 10 до 48. Больше клеток — детальнее, но дольше раскрашивать |
| Цветов | От 2 до 16. Каждому цвету — номер в палитре |
| Палитра | Клик по номеру выбирает цвет |
| Клик / зажатая мышь по клетке | Закрашивает клетку выбранным цветом (в пустых клетках виден правильный номер) |
| Показать подсказку (зажми) | Пока кнопка зажата, показывается правильная картинка |
| Закрасить всё | Автозаполнение |
| Сохранить | PNG: каждая клетка 20×20 пикселей, незакрашенные — белые |

Приложение сделано как демонстрация: оно намеренно простое и нужно, чтобы показать, как функция `pixelate` становится частью программы с окнами. Вся логика в одном файле: класс `Canvas` (полотно) и `Window` (окно).

## Презентации

Две презентации с одинаковым содержанием (15 слайдов):

- `slides/presentation_shct.pdf` — стиль ШЦТ: фиолетово-синий градиент, шрифт Open Sans, логотип «Школа цифровых технологий».
- `slides/presentation_mastersam.pdf` — стиль МАСТЕРСАМ: оранжевый `#FF6A00`, шрифт Inter, логотип «М» с сайта mastersam.org.

**Пересборка** (если нужно поменять текст или фото):

```bash
pip install playwright pillow
playwright install chromium
python slides/make_assets.py        # картинки из slides/source
python slides/build_slides.py       # PDF
```

Тексты слайдов находятся в функциях `s_...` файла `slides/build_slides.py`, стили — в строке `CSS` в начале файла. Порядок слайдов задаёт список `SLIDES`. Для загрузки шрифтов нужен интернет.

**Слайд 9 (TikTok).** Реальные ролики в PDF не встроены: там макеты телефонов. Покажите свежие ролики с экрана или вставьте QR-коды.

## Публикация библиотеки на PyPI

Версия 0.1.0 **опубликована**: https://pypi.org/project/pixelkid/. Ниже шаги для новых версий.

1. Зарегистрируйтесь на [pypi.org](https://pypi.org) и включите двухфакторную защиту.
2. Создайте API-токен: Account settings → API tokens.
3. Проверьте, что имя `pixelkid` свободно (на момент подготовки было свободно). Если занято — измените `name` в `pixelkid/pyproject.toml` и папку `src/pixelkid`.
4. Соберите и проверьте пакет:
   ```bash
   cd pixelkid
   pip install build twine
   python -m build
   twine check dist/*
   ```
5. Сначала загрузите на тестовый сервер [test.pypi.org](https://test.pypi.org):
   ```bash
   twine upload --repository testpypi dist/*
   ```
6. Если всё в порядке — на настоящий:
   ```bash
   twine upload dist/*
   ```
   Логин: `__token__`, пароль: ваш токен.

Опубликованную версию нельзя перезаписать: для исправлений увеличьте `version` в `pyproject.toml` и в `src/pixelkid/__init__.py`.

**Без PyPI.** Библиотеку можно раздавать файлом `.whl` (после `python -m build` он лежит в `pixelkid/dist/`): `pip install pixelkid-0.1.0-py3-none-any.whl`. Или установить прямо из папки: `pip install ./pixelkid`.

## Частые проблемы

| Ошибка | Решение |
|---|---|
| `No module named 'PIL'` | `pip install pillow` |
| `No module named 'pixelkid'` | `pip install ./pixelkid` (из папки проекта) |
| `No module named '_tkinter'` | Mac: `brew install python-tk@3.14`. Linux: `sudo apt install python3-tk` |
| `externally-managed-environment` | Работайте в виртуальном окружении (`python3 -m venv .venv`) |
| `ValueError: pixel_size должен быть 2 или больше` | Размер пикселя должен быть числом от 2 |
| Приложение не открывается на Linux | `pip install PyQt6` и пакеты Qt: `sudo apt install libxcb-cursor0` |
