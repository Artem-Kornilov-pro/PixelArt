"""Делает скриншот приложения для презентации (запускать из папки First_master_class):
QT_QPA_PLATFORM=offscreen .venv/bin/python slides/make_app_shot.py
"""
import sys
sys.path.insert(0, "app")
from PyQt6.QtWidgets import QApplication
from pixel_paint import Window

app = QApplication([])
w = Window()
w.load_photo("slides/assets/shct_photo.png")
w.show()
c = w.canvas
for i, n in enumerate(c.target):
    if i < len(c.target) * 0.62:
        c.painted[i] = n
c.update()
w.grab().save("slides/assets/app_shot.png")
