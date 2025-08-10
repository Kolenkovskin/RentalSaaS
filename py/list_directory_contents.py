import os
import datetime

print(f"Запуск скрипта: xAI_Marker_{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def list_directory_contents(path):
    try:
        for root, dirs, files in os.walk(path):
            print(f"Папка: {root}")
            for dir_name in dirs:
                print(f"  Подпапка: {dir_name}")
            for file_name in files:
                print(f"  Файл: {file_name}")
    except Exception as e:
        print(f"Ошибка при сканировании: {e}")

if __name__ == "__main__":
    path = r"C:\Users\User\Downloads\chrome-win64"
    list_directory_contents(path)