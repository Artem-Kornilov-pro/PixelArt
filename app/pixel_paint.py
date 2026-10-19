"""Пиксель-раскраска: загрузи фото, оно станет пиксельным, и ты его раскрасишь.

Запуск:  python app/pixel_paint.py
"""
import sys

from PIL import Image
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QColor, QPainter, QPen, QFont
from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QHBoxLayout, QLabel, QPushButton,
    QSlider, QVBoxLayout, QWidget,
)

from pixelkid import pixelate

CELL = 16  # размер одной клетки на экране


class Canvas(QWidget):
    """Полотно: клетки, которые можно закрашивать."""

    def __init__(self):
        super().__init__()
        self.small = None      # маленькая картинка: 1 точка = 1 клетка
        self.palette = []      # список цветов (r, g, b)
        self.target = []       # какой номер цвета должен быть в каждой клетке
        self.painted = []      # какой цвет закрашен (или None)
        self.current = 0       # выбранный цвет
        self.show_original = False

    def load(self, small):
        self.small = small
        self.palette = [c for _, c in sorted(small.getcolors(100000), reverse=True)]
        self.target = []
        for y in range(small.height):
            for x in range(small.width):
                self.target.append(self.palette.index(small.getpixel((x, y))))
        self.painted = [None] * len(self.target)
        self.current = 0
        self.setFixedSize(small.width * CELL, small.height * CELL)
        self.update()

    def paint_cell(self, event):
        x, y = int(event.position().x()) // CELL, int(event.position().y()) // CELL
        if self.small and 0 <= x < self.small.width and 0 <= y < self.small.height:
            self.painted[y * self.small.width + x] = self.current
            self.update()

    def mousePressEvent(self, event):
        self.paint_cell(event)

    def mouseMoveEvent(self, event):
        self.paint_cell(event)

    def fill_all(self):
        self.painted = list(self.target)
        self.update()

    def paintEvent(self, event):
        if not self.small:
            return
        p = QPainter(self)
        p.setFont(QFont("Arial", 7))
        for i, number in enumerate(self.target):
            x, y = (i % self.small.width) * CELL, (i // self.small.width) * CELL
            rect = QRect(x, y, CELL, CELL)
            shown = number if self.show_original else self.painted[i]
            if shown is None:
                p.fillRect(rect, QColor(245, 245, 245))
                p.setPen(QColor(150, 150, 150))
                p.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(number + 1))
            else:
                p.fillRect(rect, QColor(*self.palette[shown]))
        p.setPen(QPen(QColor(210, 210, 210)))
        for x in range(0, self.width() + 1, CELL):
            p.drawLine(x, 0, x, self.height())
        for y in range(0, self.height() + 1, CELL):
            p.drawLine(0, y, self.width(), y)

    def to_image(self):
        image = Image.new("RGB", self.small.size, (255, 255, 255))
        for i, color in enumerate(self.painted):
            if color is not None:
                image.putpixel((i % self.small.width, i // self.small.width), self.palette[color])
        return image.resize((self.small.width * 20, self.small.height * 20), Image.Resampling.NEAREST)


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Пиксель-раскраска")
        self.photo = None
        self.canvas = Canvas()

        self.open_button = QPushButton("Открыть фото")
        self.open_button.clicked.connect(self.open_photo)

        self.size_label = QLabel()
        self.size_slider = self.make_slider(10, 48, 24)
        self.colors_label = QLabel()
        self.colors_slider = self.make_slider(2, 16, 8)
        self.size_slider.valueChanged.connect(self.rebuild)
        self.colors_slider.valueChanged.connect(self.rebuild)

        self.palette_box = QHBoxLayout()

        self.hint_button = QPushButton("Показать подсказку (зажми)")
        self.hint_button.pressed.connect(lambda: self.set_original(True))
        self.hint_button.released.connect(lambda: self.set_original(False))
        self.fill_button = QPushButton("Закрасить всё")
        self.fill_button.clicked.connect(self.canvas.fill_all)
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save)

        top = QHBoxLayout()
        top.addWidget(self.open_button)
        top.addWidget(self.size_label)
        top.addWidget(self.size_slider)
        top.addWidget(self.colors_label)
        top.addWidget(self.colors_slider)
        bottom = QHBoxLayout()
        bottom.addWidget(self.hint_button)
        bottom.addWidget(self.fill_button)
        bottom.addWidget(self.save_button)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addLayout(self.palette_box)
        layout.addWidget(self.canvas, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(bottom)
        self.update_labels()

    def make_slider(self, low, high, value):
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(low, high)
        slider.setValue(value)
        return slider

    def update_labels(self):
        self.size_label.setText(f"Клеток в ширину: {self.size_slider.value()}")
        self.colors_label.setText(f"Цветов: {self.colors_slider.value()}")

    def open_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выбери фото", "", "Картинки (*.png *.jpg *.jpeg *.webp)")
        if path:
            self.load_photo(path)

    def load_photo(self, path):
        self.photo = Image.open(path).convert("RGB")
        self.rebuild()

    def rebuild(self):
        self.update_labels()
        if not self.photo:
            return
        cells = self.size_slider.value()
        small = pixelate(self.photo, pixel_size=max(2, self.photo.width // cells),
                         colors=self.colors_slider.value(), upscale=False)
        self.canvas.load(small)
        self.make_palette()
        self.adjustSize()

    def make_palette(self):
        while self.palette_box.count():
            self.palette_box.takeAt(0).widget().deleteLater()
        for number, color in enumerate(self.canvas.palette):
            button = QPushButton(str(number + 1))
            button.setFixedSize(34, 34)
            text = "white" if sum(color) < 380 else "black"
            button.setStyleSheet(f"background: rgb{color}; color: {text}; font-weight: bold;")
            button.clicked.connect(lambda _, n=number: self.choose(n))
            self.palette_box.addWidget(button)
        self.palette_box.addStretch()

    def choose(self, number):
        self.canvas.current = number

    def set_original(self, value):
        self.canvas.show_original = value
        self.canvas.update()

    def save(self):
        if not self.canvas.small:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить", "my_coloring.png", "PNG (*.png)")
        if path:
            self.canvas.to_image().save(path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    if len(sys.argv) > 1:
        window.load_photo(sys.argv[1])
    window.show()
    sys.exit(app.exec())
