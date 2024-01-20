import telebot
import webbrowser
import shelve

from giga import rewr, summ
from spark import spark_text
from telebot import types
from parser import parser
from function import (get_db_cursor, truncate_text, create_chat_data_table, get_offset_from_db, update_offset_in_db,
                      clear_chat_history, get_data_by_tomita_parser)

bot = telebot.TeleBot('6406669187:AAGUKC_n-tWE2f1gvcJeTyfwdIMrpFueFuU')


@bot.message_handler(commands=['start'])
def main(message):
    create_chat_data_table()
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('Перейти на сайт', url='https://vlg.aif.ru/news')
    button2 = types.InlineKeyboardButton('Загрузить 10 новостей', callback_data='news')
    button3 = types.InlineKeyboardButton('Проверить наличие новых новостей', callback_data='new')
    markup.row(button1)
    markup.row(button2, button3)

    bot.send_message(message.chat.id, f'Привет, <b>{message.from_user.first_name}</b>!\n'
                                      f'Вы подписались на рассылку по новостям'
                                      f'с сайта '
                                      f'<a href="https://vlg.aif.ru/news"><b>"<ins>Аргументы и факты</ins>"</b></a>',
                     parse_mode='html', reply_markup=markup, disable_web_page_preview=True)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'news':
        conn, cursor = get_db_cursor()
        chat_id = callback.message.chat.id
        offset = get_offset_from_db(chat_id)

        cursor.execute(f'SELECT * FROM news ORDER BY SUBSTR(date, 10, 2) || SUBSTR(date, 4, 2) || SUBSTR(date, 1, 2) '
                       f'DESC LIMIT 10 OFFSET {offset}')
        news_records = cursor.fetchall()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("Загрузить еще 10 новостей")
        button2 = types.KeyboardButton('Проверить наличие новых новостей')
        markup.row(button1)
        markup.row(button2)

        for record in reversed(news_records):
            rew = rewr(record[4])
            sum = summ(record[4])
            person, place = get_data_by_tomita_parser(record[4])
            content = truncate_text(record[4])
            bot.send_message(callback.message.chat.id,
                             f'<i><b>{record[1]}:</b></i>\n\n'
                             f'{content}\n'
                             f'<a href="{record[3]}">Ссылка на новость</a>\n\n'
                             f'Персона/ы: {person}\n\n'
                             f'Достопримечательность/и: {place}\n\n'
                             f'Аннотация: {sum}\n'
                             f'Краткое описание: {rew}\n'
                             f'Дата: {record[2]}', parse_mode='html',
                             disable_web_page_preview=True)

        offset += len(news_records)
        update_offset_in_db(chat_id, offset)

        bot.send_message(callback.message.chat.id, 'Выберите действие: ', reply_markup=markup)

        cursor.close()
        conn.close()
    elif callback.data == 'new':
        new_news(callback.message)


@bot.message_handler(commands=['news'])
def news(message):
    conn, cursor = get_db_cursor()
    chat_id = message.chat.id
    offset = get_offset_from_db(chat_id)

    cursor.execute(f'SELECT * FROM news ORDER BY SUBSTR(date, 10, 2) || SUBSTR(date, 4, 2) || SUBSTR(date, 1, 2) '
                   f'DESC LIMIT 10 OFFSET {offset}')
    news_records = cursor.fetchall()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Загрузить еще 10 новостей")
    button2 = types.KeyboardButton('Проверить наличие новых новостей')
    markup.row(button1)
    markup.row(button2)

    for record in reversed(news_records):
        rew = rewr(record[4])
        sum = summ(record[4])
        person, place = get_data_by_tomita_parser(record[4])
        content = truncate_text(record[4])
        bot.send_message(message.chat.id,
                         f'<i><b>{record[1]}:</b></i>\n\n'
                         f'{content}\n'
                         f'<a href="{record[3]}">Ссылка на новость</a>\n\n'
                         f'Персона/ы: {person}\n\n'
                         f'Достопримечательность/и: {place}\n\n'
                         f'Аннотация: {sum}\n'
                         f'Краткое описание: {rew}\n'
                         f'Дата: {record[2]}', parse_mode='html',
                         disable_web_page_preview=True)


    offset += len(news_records)
    update_offset_in_db(chat_id, offset)

    bot.send_message(message.chat.id, 'Выберите действие: ', reply_markup=markup)

    cursor.close()
    conn.close()


@bot.message_handler(commands=['new'])
def new_news(message):
    flag, count = parser()
    if flag == 0:
        conn, cursor = get_db_cursor()
        chat_data = shelve.open('chat_data.db')
        chat_id = message.chat.id

        cursor.execute(f'SELECT id, title, date, url, content FROM news ORDER BY id DESC LIMIT {count}')
        new_news_records = cursor.fetchall()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("Загрузить еще 10 новостей")
        button2 = types.KeyboardButton('Проверить наличие новых новостей')
        markup.row(button1)
        markup.row(button2)

        bot.send_message(message.chat.id, 'Последние 10 новостей с сайта:\n')
        for record in reversed(new_news_records):
            rew = rewr(record[4])
            sum = summ(record[4])
            person, place = get_data_by_tomita_parser(record[4])
            content = truncate_text(record[4])
            bot.send_message(message.chat.id,
                             f'<i><b>{record[1]}:</b></i>\n\n'
                             f'{content}\n'
                             f'<a href="{record[3]}">Ссылка на новость</a>\n\n'
                             f'Персона/ы: {person}\n\n'
                             f'Достопримечательность/и: {place}\n\n'
                             f'Аннотация: {sum}\n'
                             f'Краткое описание: {rew}\n'
                             f'Дата: {record[2]}', parse_mode='html',
                             disable_web_page_preview=True)

        chat_data[str(chat_id)] = 0

        bot.send_message(message.chat.id, 'Выберите действие: ', reply_markup=markup)

        cursor.close()
        conn.close()
        chat_data.close()
    else:
        bot.send_message(message.chat.id, 'Новых новостей нет')


@bot.message_handler(func=lambda message: message.text.lower() == 'загрузить еще 10 новостей')
def more_news(message):
    conn, cursor = get_db_cursor()
    chat_id = message.chat.id
    offset = get_offset_from_db(chat_id)

    cursor.execute(f'SELECT * FROM news ORDER BY SUBSTR(date, 10, 2) || SUBSTR(date, 4, 2) || SUBSTR(date, 1, 2) '
                   f'DESC LIMIT 10 OFFSET {offset}')
    news_records = cursor.fetchall()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Загрузить еще 10 новостей")
    button2 = types.KeyboardButton('Проверить наличие новых новостей')
    markup.row(button1)
    markup.row(button2)

    for record in reversed(news_records):
        rew = rewr(record[4])
        sum = summ(record[4])
        person, place = get_data_by_tomita_parser(record[4])
        content = truncate_text(record[4])
        bot.send_message(message.chat.id,
                         f'<i><b>{record[1]}:</b></i>\n\n'
                         f'{content}\n'
                         f'<a href="{record[3]}">Ссылка на новость</a>\n\n'
                         f'Персона/ы: {person}\n\n'
                         f'Достопримечательность/и: {place}\n\n'
                         f'Аннотация: {sum}\n'
                         f'Краткое описание: {rew}\n'
                         f'Дата: {record[2]}', parse_mode='html',
                         disable_web_page_preview=True)


    offset += len(news_records)
    update_offset_in_db(chat_id, offset)

    bot.send_message(message.chat.id, 'Выберите действие: ', reply_markup=markup)

    cursor.close()
    conn.close()


@bot.message_handler(func=lambda message: message.text.lower() == 'проверить наличие новых новостей')
def check_new(message):
    flag, count = parser()
    if flag == 0:
        conn, cursor = get_db_cursor()
        chat_data = shelve.open('chat_data.db')
        chat_id = message.chat.id

        cursor.execute(f'SELECT id, title, date, url, content FROM news ORDER BY id DESC LIMIT {count}')
        new_news_records = cursor.fetchall()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("Загрузить еще 10 новостей")
        button2 = types.KeyboardButton('Проверить наличие новых новостей')
        markup.row(button1)
        markup.row(button2)

        bot.send_message(message.chat.id, 'Последние 10 новостей с сайта:\n')
        for record in reversed(new_news_records):
            rew = rewr(record[4])
            sum = summ(record[4])
            person, place = get_data_by_tomita_parser(record[4])
            content = truncate_text(record[4])
            bot.send_message(message.chat.id,
                             f'<i><b>{record[1]}:</b></i>\n\n'
                             f'{content}\n'
                             f'<a href="{record[3]}">Ссылка на новость</a>\n\n'
                             f'Персона/ы: {person}\n\n'
                             f'Достопримечательность/и: {place}\n\n'
                             f'Аннотация: {sum}\n'
                             f'Краткое описание: {rew}\n'
                             f'Дата: {record[2]}', parse_mode='html',
                             disable_web_page_preview=True)

        chat_data[str(chat_id)] = 0

        bot.send_message(message.chat.id, 'Выберите действие: ', reply_markup=markup)

        cursor.close()
        conn.close()
        chat_data.close()
    else:
        bot.send_message(message.chat.id, 'Новых новостей нет')


@bot.message_handler(commands=['clear'])
def clear(message):
    clear_chat_history(message.chat.id)
    bot.send_message(message.chat.id, 'История чата очищена')


@bot.message_handler(commands=['website'])
def site(_):
    webbrowser.open('https://vlg.aif.ru/news')


@bot.message_handler()
def spark(message):
    spark_text(message.text)
    # bot.send_message(message.chat.id, f'{syn, word, w2v}\n')

@bot.message_handler()
def website(message):
    if message.text.lower() == 'перейти на сайт':
        webbrowser.open(url='https://vlg.aif.ru/news')


bot.polling(non_stop=True)
