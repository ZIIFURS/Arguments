import sqlite3
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup as BS
from datetime import datetime
import re


def parser():
    url = "https://vlg.aif.ru/news"
    key = 0
    count = 0
    flag = 1
    checked_urls = set()

    while flag != 0:

        response = requests.get(url)
        soup = BS(response.text, 'html.parser')

        news_items = soup.find_all('div', class_='list_item')

        for item in news_items:
            title = item.find('span', class_='item_text__title').text
            date_element = item.find('span', class_='text_box__date')

            if date_element:
                date_text = date_element.text
                # Используем регулярное выражение для проверки формата даты
                date_match = re.match(r"\d{2}\.\d{2}\.\d{4}", date_text)
                if date_match:
                    date = date_match.group()
                else:
                    date = datetime.today().strftime('%d.%m.%Y')  # Получаем текущую дату
            else:
                date = "Нет даты"

            link_element = item.find('a').get('href')
            if link_element in checked_urls:
                continue

            link_absolute = urljoin(url, link_element)

            #        time.sleep(1)

            try:
                full_text_response = requests.get(link_absolute)
                full_text_response.raise_for_status()  # Проверка наличия ошибок при запросе
            except requests.exceptions.HTTPError as errh:
                print("HTTP Error:", errh)
                continue
            except requests.exceptions.ConnectionError as errc:
                print("Error Connecting:", errc)
                continue
            except requests.exceptions.Timeout as errt:
                print("Timeout Error:", errt)
                continue
            except requests.exceptions.RequestException as err:
                print("Other Error:", err)
                continue

            if full_text_response.status_code == 200:
                full_text_soup = BS(full_text_response.text, 'html.parser')
                full_text = full_text_soup.find('div', class_='article_text').text.strip()

            else:
                full_text = ''

            content = full_text.rstrip("Подробнее")

            conn = sqlite3.connect("news.db")
            cursor = conn.cursor()

            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS news (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        date TEXT,
                        url TEXT,
                        content TEXT
                    )
                ''')
            conn.commit()

            if link_element not in checked_urls:
                cursor.execute('SELECT COUNT(*) FROM news WHERE url = ?', (link_element,))

                existing_record_count = cursor.fetchone()[0]

                if existing_record_count == 0:
                    count += 1
                    cursor.execute('''
                                INSERT INTO news (title, date, url, content) VALUES (?, ?, ?, ?)
                            ''', (str(title), str(date), str(link_element), str(content.replace("\n\n", "\n"))))
                    conn.commit()

                else:
                    print(f"Все новости уже есть в бд!")
                    flag = 0
                    key = 1
                    break
                checked_urls.add(link_element)
        print("Догружено 10 новых новостей!")
        flag = 0

    conn.close()
    return key, count