from tkinter import Tk, filedialog

from pixelkid import pixelate

root = Tk()
root.withdraw()

# 1. Выбираем фотографию
file_path = filedialog.askopenfilename(
    title="Выбери фотографию",
    filetypes=[("Изображения", "*.png *.jpg *.jpeg *.webp")]
)

if not file_path:
    raise SystemExit

# 2. Размер пикселя и количество цветов
pixel_size = int(input("Размер пикселя (например, 8, 12 или 20): "))
colors = int(input("Количество цветов (например, 16, 32 или 64): "))

# 3. Делаем пиксель-арт и сохраняем в папку проекта
result = pixelate(file_path, pixel_size=pixel_size, colors=colors, save_as="my_pixel_art.png")

print("Готово! Файл my_pixel_art.png сохранён в папке проекта")
result.show()
