import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import datetime

print(f"Запуск скрипта: xAI_Marker_{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def get_page_html():
    url = input("Пожалуйста, введите ссылку на страницу (например, https://www.kv.ee): ")
    chromedriver_path = os.path.join(os.getcwd(), "chromedriver.exe")  # Исправлен путь
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service)

    try:
        driver.get(url)
        html_code = driver.page_source
        print("HTML-код страницы:")
        print(html_code)
    except Exception as e:
        print(f"Ошибка при загрузке страницы: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    get_page_html()