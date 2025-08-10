import os

# Путь к проекту
project_path = r"C:\Users\User\PycharmProjects\RentalSaaS"
output_file = os.path.join(project_path, "project_structure.txt")

# Функция для рекурсивного обхода директорий и записи структуры
def generate_structure(path, output_file, level=0):
    try:
        with open(output_file, 'a', encoding='utf-8') as f:
            # Получаем все элементы в текущей директории
            items = [item for item in os.listdir(path) if item != '.venv']
            for item in sorted(items):
                full_path = os.path.join(path, item)
                # Индентация для иерархии
                indent = "  " * level
                if os.path.isdir(full_path):
                    f.write(f"{indent}{item}/\n")
                    generate_structure(full_path, output_file, level + 1)
                else:
                    f.write(f"{indent}{item}\n")
                    # Чтение и запись содержимого файла (если это текстовый файл)
                    if item.endswith(('.txt', '.py', '.html')):
                        try:
                            with open(full_path, 'r', encoding='utf-8') as content_file:
                                content = content_file.read()
                                f.write(f"{indent}  Content:\n")
                                for line in content.split('\n'):
                                    f.write(f"{indent}    {line}\n")
                        except Exception as e:
                            f.write(f"{indent}  Error reading content: {e}\n")
    except Exception as e:
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"Error accessing {path}: {e}\n")

# Очистка файла перед записью (если он существует)
if os.path.exists(output_file):
    try:
        os.remove(output_file)
        print(f"Файл {output_file} очищен.")
    except Exception as e:
        print(f"Ошибка при очистке файла: {e}")

# Генерация структуры
print(f"Генерация структуры проекта в {output_file}...")
generate_structure(project_path, output_file)
print("Генерация завершена.")