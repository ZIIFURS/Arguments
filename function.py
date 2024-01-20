import sqlite3
import subprocess
import time
import os

from dictionary import genitive_to_nominative

def get_db_cursor():
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    return conn, cursor


def clean_pycache():
    current_directory = os.getcwd()

    pycache_path = os.path.join(current_directory, '__pycache__')

    files_to_delete = os.listdir(pycache_path)

    if files_to_delete:
        print(f"Каталог {pycache_path} пуст. Удаление не требуется.")
        for file_name in files_to_delete:
            file_path = os.path.join(pycache_path, file_name)
            os.remove(file_path)
            print(f"Файл {file_path} удален.")
def truncate_text(content, max_words=50, reduction='...'):
    words = content.split()
    finish_words = words[:max_words]
    finish_text = ' '.join(finish_words)

    if len(words) > max_words:
        finish_text += reduction

    return finish_text


def create_chat_data_table():
    conn = sqlite3.connect('chat_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_data (
            chat_id TEXT PRIMARY KEY,
            offset INTEGER
        )
    ''')

    conn.commit()
    conn.close()


# Функция для получения значения offset из базы данных
def get_offset_from_db(chat_id):
    conn = sqlite3.connect('chat_data.db')
    cursor = conn.cursor()

    # Выполняем запрос SELECT, чтобы получить значение offset для данного чата
    cursor.execute('SELECT offset FROM chat_data WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else 0


# Функция для обновления значения offset в базе данных
def update_offset_in_db(chat_id, offset):
    conn = sqlite3.connect('chat_data.db')
    cursor = conn.cursor()

    # Выполняем запрос UPDATE, чтобы обновить значение offset для данного чата
    cursor.execute('INSERT OR REPLACE INTO chat_data (chat_id, offset) VALUES (?, ?)', (chat_id, offset))

    conn.commit()
    conn.close()


def clear_chat_history(chat_id):
    conn = sqlite3.connect('chat_data.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM chat_data WHERE chat_id = ?', (chat_id,))

    conn.commit()
    conn.close()

def get_data_by_tomita_parser(content):

    def normalize_name(name):
        return name.upper()

    counter = 0
    clean_pycache()
    surnames_file = 'surnames.txt'
    output_file = 'output.txt'
    input_file = 'input.txt'

    with open(surnames_file, 'r', encoding='utf-8') as file:
        surnames = set(normalize_name(line) for line in file.read().splitlines())

    with open(input_file, 'w', encoding='utf-8') as file:
        file.write(content)

    subprocess.run(['./tomita-parser', 'config.proto'])
    time.sleep(2)

    extracted_surnames = set()
    extracted_places = set()

    with open(output_file, 'r', encoding='utf-8') as file:
        for line in file:
            if "Surname = " in line:
                surname = normalize_name(line.split('=')[-1].strip())
                extracted_surnames.add(surname)
            elif "Place = " in line:
                place = normalize_name(line.split('=')[-1].strip())
                extracted_places.add(place)

    filtered_surnames = set(surname for surname in surnames if
                            any(surname in extracted_surname for extracted_surname in extracted_surnames))
    filtered_places = [genitive_to_nominative.get(form, form) for form in extracted_places]

    if len(filtered_surnames) == 0:
        surnames_out = "В статье не встречаются вип-персоны"
        counter += 1
    else:
        surnames_out = str(filtered_surnames)[2:-2]

    if len(filtered_places) == 0:
        places_out = "В статье не встречаются достропримечательности"
        counter += 1
    else:
        places_out = str(filtered_places)[2:-2]

    print(surnames_out)
    print(places_out)

    clean_pycache()

    return surnames_out, places_out
