import os
import datetime

print(f"Запуск скрипта: xAI_Marker_v1a_20250804_{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Указываем путь к файлу
index_file_path = os.path.join('C:\\Users\\User\\PyCharmProjects\\RentalSaaS', 'templates', 'index.html')

# Читаем и выводим содержимое файла
try:
    with open(index_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        print("Содержимое файла index.html:")
        print(content)
except FileNotFoundError:
    print(f"Ошибка: Файл по пути {index_file_path} не найден.")
except Exception as e:
    print(f"Ошибка при чтении файла: {e}")