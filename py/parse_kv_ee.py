import os
from bs4 import BeautifulSoup
import datetime

print(f"Запуск скрипта: xAI_Marker_v1b_20250804_{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def parse_kv_ee(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    listings = []

    # Находим все объявления
    articles = soup.find_all('article', class_=['default', 'object-type-apartment'])
    for article in articles:
        listing = {}

        # Цена
        price_div = article.find('div', class_='price')
        if price_div:
            price_text = price_div.get_text(strip=True).replace('\xa0', ' ')
            listing['price'] = price_text

        # Район
        h2_link = article.find('h2').find('a', href=True)
        if h2_link:
            location = h2_link.get_text(strip=True)
            listing['location'] = location

        # Тип жилья (из excerpt или контекста)
        excerpt = article.find('p', class_='object-excerpt')
        if excerpt:
            listing['type'] = excerpt.get_text(strip=True).split()[0] if excerpt.get_text(strip=True) else 'Apartment'

        # Площадь
        area_div = article.find('div', class_='area')
        if area_div:
            area_text = area_div.get_text(strip=True).replace('\xa0', ' ')
            listing['area'] = area_text

        # Дата публикации
        add_time_div = article.find('div', class_='add-time')
        if add_time_div:
            add_time = add_time_div.get_text(strip=True)
            listing['add_time'] = add_time if add_time else 'N/A'

        # Ссылка (используем первый <a> с href внутри article)
        link = article.find('a', href=True)
        if link and 'data-skeleton' in link.attrs and link['data-skeleton'] == 'object':
            full_link = 'https://www.kv.ee' + link['href']
            listing['link'] = full_link
        else:
            listing['link'] = 'N/A'

        # Количество комнат
        rooms_div = article.find('div', class_='rooms')
        if rooms_div:
            listing['rooms'] = rooms_div.get_text(strip=True)

        listings.append(listing)

    return listings


if __name__ == "__main__":
    # Запрашиваем путь к файлу у пользователя
    file_path = input(
        "Пожалуйста, введите путь к файлу HTML (например, C:\\Users\\User\\PyCharmProjects\\RentalSaaS\\HtmlCodeKv.txt): ")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        results = parse_kv_ee(html_content)
        for idx, result in enumerate(results, 1):
            print(f"Объявление {idx}: {result}")
    except FileNotFoundError:
        print(f"Ошибка: Файл по пути {file_path} не найден.")
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")