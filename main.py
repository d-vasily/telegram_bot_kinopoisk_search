# import requests
# import re
# from random import randint
# from bs4 import BeautifulSoup
# import pandas as pd
import telebot as tb
# from flask import Flask, request

from dbworker import set_info, get_info
from search_func import get_parameters

# kinopoist_search_bot
TOKEN = '2061129559:AAGIIMpRztdc3cA-kfxYxhd0ZGIx5FeLAGs'  # это мой токен
bot = tb.TeleBot(token=TOKEN)

set_info('default_search', '| | | yandex_plus_subscription| foreign| | ')


@bot.message_handler(commands=['start'])
def send_info(message):
    text = (
        "<b>Здесь ты можешь найти фильм для просмотра на кинопоиске.</b>\n\n"
        "Ты можешь выбирать параметры поиска, а также сохранять их.\n\n"
        "Помимо этого ты можешь создать свой список фильмов и редактировать его.\n\n"
        "Чтобы посмотреть описание функционала бота, используй команду /help."
    )
    bot.send_message(message.chat.id, text, parse_mode='HTML')


@bot.message_handler(commands=["menu"])
def menu(message):
    markup = tb.types.ReplyKeyboardMarkup(row_width=2, selective=False, one_time_keyboard=True)
    itembtn1 = tb.types.KeyboardButton('/search')
    itembtn2 = tb.types.KeyboardButton('/my_films')
    itembtn3 = tb.types.KeyboardButton('/help')
    itembtn4 = tb.types.KeyboardButton('/commands')
    markup.add(itembtn1, itembtn2, itembtn4, itembtn3)
    bot.send_message(message.chat.id, "Menu", reply_markup=markup)


@bot.message_handler(commands=["search"])
def search(message):
    markup = tb.types.ReplyKeyboardMarkup(row_width=2, selective=False, one_time_keyboard=True)
    itembtn1 = tb.types.KeyboardButton('/new_search')
    itembtn2 = tb.types.KeyboardButton('/previous_search')
    itembtn3 = tb.types.KeyboardButton('/saved_search')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.chat.id, "Choose search", reply_markup=markup)


@bot.message_handler(commands=["new_search"])
def new_search(message):
    parameters = get_info(str(message.chat.id) + 'new_search_parameters')
    if parameters == 'null':
        set_info(str(message.chat.id) + 'new_search_parameters', get_info('default_search'))
    set_info(message.chat.id, 'new_search')
    search_menu(message)


@bot.message_handler(commands=["previous_search"])
def previous_search(message):
    parameters = get_info(str(message.chat.id) + 'previous_search_parameters')
    if parameters == 'null':
        set_info(str(message.chat.id) + 'previous_search_parameters', dbw.get_info('default_search'))
    set_current_state(message.chat.id, 'previous_search')
    search_menu(message)


@bot.message_handler(commands=["saved_search"])
def saved_search(message):
    parameters = get_info(str(message.chat.id) + 'saved_search_parameters')
    if parameters == 'null':
        set_info(str(message.chat.id) + 'saved_search_parameters', get_info('default_search'))
    set_current_state(message.chat.id, 'saved_search')
    search_menu(message)


def search_menu(message):
    markup = tb.types.ReplyKeyboardMarkup(row_width=2, selective=False, one_time_keyboard=True)
    itembtn1 = tb.types.KeyboardButton('/current_parameters')
    itembtn2 = tb.types.KeyboardButton('/change_parameters')
    itembtn3 = tb.types.KeyboardButton('/start_search')
    itembtn4 = tb.types.KeyboardButton('/search')
    markup.add(itembtn1, itembtn2, itembtn4, itembtn3)
    bot.send_message(message.chat.id, "Search menu", reply_markup=markup)


@bot.message_handler(commands=["current_parameters"])
def current_parameters(message):
    search_type = get_info(str(message.chat.id))
    parameters = get_info(str(message.chat.id) + search_type + '_parameters')
    parameters = get_parameters(parameters)

    markup = tb.types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, text='aa', reply_markup=markup)
    bot.send_message(message.chat.id, str(message.chat.id), reply_markup=markup)


# example of ReplyKeyboardRemove
@bot.message_handler(commands=["сортировка"])
def reply_a(message):
    markup = tb.types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, text='aa', reply_markup=markup)
    bot.send_message(message.chat.id, str(message.chat.id), reply_markup=markup)


bot.infinity_polling()
