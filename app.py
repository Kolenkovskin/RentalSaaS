from dotenv import load_dotenv
import os
load_dotenv()  # Загружает переменные из .env
import asyncio
from flask import Flask, jsonify, request, render_template
import sqlite3
import aioschedule as schedule
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError
from bs4 import BeautifulSoup
import sendgrid
from sendgrid.helpers.mail import Mail
import os


app = Flask(__name__, template_folder='templates')

# Настройки Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8036857233:AAEtKNmUzytmUcbHHF0Vt9V2Hfoa8Gs_TV8")
CHAT_ID = os.getenv("CHAT_ID", "5141864033")
bot = Bot(TELEGRAM_TOKEN)

# Настройки SendGrid
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
if not SENDGRID_API_KEY:
    raise ValueError("SENDGRID_API_KEY is not set in environment variables")

# xAI_Marker_v1p_20250809_1630
def send_notification(recipient_email):
    sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)
    message = Mail(
        from_email='kolenkovskin@hotmail.com',  # Убедитесь, что этот email верифицирован в SendGrid
        to_emails=recipient_email,
        subject='Тест уведомления',
        html_content='Новое бронирование!'
    )
    response = sg.send(message)
    print(f"SendGrid status: {response.status_code}")

# Инициализация БД
def init_db():
    conn = sqlite3.connect('py/rentals.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        price REAL,
        location TEXT,
        area REAL,
        rooms INTEGER,
        add_time TEXT,
        link TEXT UNIQUE
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY,
        listing_id INTEGER,
        user_id TEXT,
        booked_at TEXT,
        FOREIGN KEY (listing_id) REFERENCES listings (id)
    )''')
    conn.commit()
    conn.close()

# Парсинг данных из локального HTML-файла с улучшенным извлечением add_time
def parse_kv_ee(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    listings = []
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
        # Тип жилья
        excerpt = article.find('p', class_='object-excerpt')
        if excerpt:
            listing['type'] = excerpt.get_text(strip=True).split()[0] if excerpt.get_text(strip=True) else 'Apartment'
        # Площадь
        area_div = article.find('div', class_='area')
        if area_div:
            area_text = area_div.get_text(strip=True).replace('\xa0', ' ')
            listing['area'] = float(area_text.split(' ')[0]) if area_text else 0.0
        # Дата публикации (улучшенный парсинг)
        add_time_div = article.find('div', class_=['add-time', 'object-add-time'])  # Пробуем разные классы
        if add_time_div and add_time_div.get_text(strip=True):
            add_time = add_time_div.get_text(strip=True)
            listing['add_time'] = add_time if add_time else 'N/A'
        else:
            listing['add_time'] = 'N/A'  # Если не найдено, оставляем N/A
        # Ссылка
        link = article.find('a', href=True)
        if link and 'data-skeleton' in link.attrs and link['data-skeleton'] == 'object':
            full_link = 'https://www.kv.ee' + link['href']
            listing['link'] = full_link
        else:
            listing['link'] = 'N/A'
        # Количество комнат
        rooms_div = article.find('div', class_='rooms')
        if rooms_div:
            listing['rooms'] = int(rooms_div.get_text(strip=True).split()[0]) if rooms_div.get_text(strip=True).isdigit() else 0
        listings.append(listing)
    return listings

# Обновление данных из локального HTML-файла
def update_listings():
    try:
        conn = sqlite3.connect('py/rentals.db')
        c = conn.cursor()
        # Очистка таблицы перед обновлением
        c.execute("DELETE FROM listings")
        conn.commit()
        with open('HtmlCodeKv.txt', 'r', encoding='utf-8') as file:
            html_content = file.read()
        listings = parse_kv_ee(html_content)
        for listing in listings:
            c.execute(
                "INSERT OR IGNORE INTO listings (price, location, area, rooms, add_time, link) VALUES (?, ?, ?, ?, ?, ?)",
                (float(listing['price'].split(' ')[0].replace('€', '')) if listing['price'] else 0.0,
                 listing['location'] if listing['location'] else 'N/A',
                 listing['area'] if listing['area'] else 0.0,
                 listing['rooms'] if listing['rooms'] else 0,
                 listing['add_time'] if listing['add_time'] else 'N/A',
                 listing['link'] if listing['link'] else 'N/A')
            )
        conn.commit()
        print(f"Listings updated successfully. Total records: {len(listings)}")
    except Exception as e:
        print(f"Error updating listings: {e}")
    finally:
        conn.close()

# Отправка Telegram-уведомления
async def send_telegram_notification(chat_id, message):
    try:
        await bot.send_message(chat_id=chat_id, text=message)
        print(f"Telegram message sent: {message}")
    except TelegramError as e:
        print(f"Failed to send Telegram message: {e}")

# Асинхронный планировщик
async def run_scheduler():
    schedule.every().day.at("02:00").do(update_listings)
    while True:
        await schedule.run_pending()
        await asyncio.sleep(60)

# Эндпоинты API
@app.route('/listings', methods=['GET'])
def get_listings():
    conn = sqlite3.connect('py/rentals.db')
    c = conn.cursor()
    c.execute("SELECT * FROM listings")
    listings = [{'id': row[0], 'price': row[1], 'location': row[2], 'area': row[3], 'rooms': row[4], 'add_time': row[5], 'link': row[6]} for row in c.fetchall()]
    print(f"Number of listings returned: {len(listings)}")
    conn.close()
    return jsonify(listings)

@app.route('/analytics', methods=['GET'])
def get_analytics():
    conn = sqlite3.connect('py/rentals.db')
    c = conn.cursor()
    c.execute("SELECT location, AVG(price/area) as avg_price_per_m2 FROM listings WHERE price > 2 GROUP BY location HAVING avg_price_per_m2 IS NOT NULL AND avg_price_per_m2 > 0")
    analytics = [{'location': row[0], 'avg_price_per_m2': row[1]} for row in c.fetchall()]
    print(f"Number of analytics entries: {len(analytics)}")
    conn.close()
    return jsonify(analytics)

@app.route('/booking', methods=['POST'])
async def create_booking():
    data = request.get_json()
    listing_id = data.get('listing_id')
    user_id = data.get('user_id')
    if not listing_id or not user_id:
        return jsonify({'error': 'Missing required fields'}), 400
    conn = sqlite3.connect('py/rentals.db')
    c = conn.cursor()
    c.execute("INSERT INTO bookings (listing_id, user_id, booked_at) VALUES (?, ?, ?)",
              (listing_id, user_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    # Отправка уведомлений
    listing = c.execute("SELECT price, location FROM listings WHERE id = ?", (listing_id,)).fetchone()
    if listing:
        message = f"New booking for listing: Price {listing[0]}€, Location: {listing[1]} at {datetime.now()}"
        await send_telegram_notification(CHAT_ID, message)
        send_notification('estalpanek@gmail.com')  # Email-уведомление через SendGrid
    else:
        print(f"No listing found with id {listing_id}")
    conn.close()
    return jsonify({'message': 'Booking created'}), 201

# Маршрут для главной страницы
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    print(f"Запуск скрипта: xAI_Marker_v1aa_20250807_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    init_db()
    update_listings()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Запускаем планировщик в фоновом потоке
    from threading import Thread
    def run_scheduler_in_thread():
        loop.run_until_complete(run_scheduler())
    scheduler_thread = Thread(target=run_scheduler_in_thread, daemon=True)
    scheduler_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=True)