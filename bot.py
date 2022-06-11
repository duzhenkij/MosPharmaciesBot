import telebot
import datetime as dt
import sqlite3
from random import randint
from config import telegram_bot_token
from main import get_result_to_user

bot = telebot.TeleBot(telegram_bot_token, parse_mode=None)

start_command_text = 'Привет!' \
                     '\nОтправь мне наименование медицинского препарата ' \
                     'и я пришлю в каких аптеках его можно приобрести ' \
                     'по наиболее низким ценам'

info_command_text = 'Бот выполняет поиск медицинского препарата, отправленного пользователем, ' \
                    'среди крупных аптечных сетей Москвы и выводит топ-20 препаратов в порядке ' \
                    'убывания по актуальным ценам.'

error_message = 'Что-то пошло не так..' \
                '\nЛекарство не нашлось. ' \
                '\nВозможно стоит проверить написание. Попробуем ещё раз?'

waiting_massages_list = ['Секундочку..', 'Уже ищу..', 'Я уже в процессе поиска..', 'Подбираю..',
                         'Подбираю по наиболее выгодной цене..']


def count_user_coverage(user, datetime_query, medicine):
    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()
    cursor.execute(f"INSERT INTO statistic VALUES (?, ?, ?)",
                   (user, datetime_query, medicine))
    connect.commit()
    connect.close()


@bot.message_handler(commands=['start'])
def hello(message):
    bot.send_message(message.chat.id, start_command_text)
    bot.register_next_step_handler(message, execute_user_query)


@bot.message_handler(commands=['info'])
def get_info(message):
    bot.send_message(message.chat.id, info_command_text)
    bot.register_next_step_handler(message, execute_user_query)


@bot.message_handler(content_types=['text'])
def execute_user_query(message):
    if message.text == '/start':
        bot.send_message(message.chat.id, start_command_text)
        bot.register_next_step_handler(message, execute_user_query)
    elif message.text == '/info':
        bot.send_message(message.chat.id, info_command_text)
        bot.register_next_step_handler(message, execute_user_query)
    else:
        # counting user coverage in database
        user_id = message.chat.id
        datetime_query = str(dt.datetime.now())
        medicine = message.text
        count_user_coverage(user_id, datetime_query, medicine)

        # sending result to user
        bot.send_message(message.chat.id, waiting_massages_list[randint(0, 4)])

        try:
            bot.send_message(message.chat.id, get_result_to_user(message.text))
        except telebot.apihelper.ApiTelegramException:
            bot.send_message(message.chat.id, error_message)

        bot.register_next_step_handler(message, execute_user_query)


bot.infinity_polling()
