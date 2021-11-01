# import requests
# import re
# from random import randint
# from bs4 import BeautifulSoup
import pandas as pd
import telebot as tb
# from flask import Flask, request

from tabulate import tabulate
from dbworker import set_info, get_info, get_parameters
from parser import get_ten

# default settings !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
set_info('default_search', '| | | yandex_plus_subscription| foreign| | ')
set_info('genre', '| anime| mystery| comedy| crime| adventure| family| thriller| horror| sci-fi| fantasy| 1')
set_info('sort', '| popularity| year| 2')
set_info('rating', '| high_rated| 3')
set_info('subscript', 'available_online| yandex_plus_subscription| kinopoisk_with_amediateka_subscription| 4')
set_info('country', '| foreign| russian| 5')
set_info('kind', '| films| serials| 6')

# kinopoist_search_bot
TOKEN = ''  # это мой токен
bot = tb.TeleBot(token=TOKEN)


# start !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=['start'])
def send_info(message):
    set_info(str(message.chat.id) + 'state', 'start')
    text1 = (
        'Страна:\nСША\n\nГод:\n2019\n\nЯзык озвучки:\nРусский, Английский\n\nСубтитры:\nРусские, Английские\n\nОписание:\nВ начале 1960-х Генри Форд II принимает решение улучшить имидж компании и сменить курс на производство более модных автомобилей. После неудавшейся попытки купить практически банкрота Ferrari американцы решают бросить вызов итальянским конкурентам на трассе и выиграть престижную гонку 24 часа Ле-Мана. Чтобы создать подходящую машину, компания нанимает автоконструктора Кэррола Шэлби, а тот отказывается работать без выдающегося, но, как считается, трудного в общении гонщика Кена Майлза. Вместе они принимаются за разработку впоследствии знаменитого спорткара Ford GT40.'
    )
    text = (
        "<b>Здесь ты можешь найти фильм для просмотра на кинопоиске.</b>\n\n"
        "Ты можешь выбирать параметры поиска, а также сохранять.\n\n"
        "Помимо этого ты можешь создать свой список фильмов и редактировать его.\n\n"
        "Чтобы посмотреть описание функционала бота, используй команду /help."
    )
    bot.send_message(message.chat.id, text1, parse_mode='HTML')


# menu !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["menu"])
def menu(message):
    set_info(str(message.chat.id) + 'state', 'menu')
    markup = tb.types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    itembtn1 = tb.types.KeyboardButton('/search')
    itembtn2 = tb.types.KeyboardButton('/my_films')
    itembtn3 = tb.types.KeyboardButton('/help')
    itembtn4 = tb.types.KeyboardButton('/commands')
    markup.add(itembtn1, itembtn2, itembtn4, itembtn3)
    bot.send_message(message.chat.id, "Menu", reply_markup=markup)
    send_info(message)


# search !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["search"])
def search(message):
    set_info(str(message.chat.id) + 'state', 'search')
    markup = tb.types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    itembtn1 = tb.types.KeyboardButton('/new_search')
    itembtn2 = tb.types.KeyboardButton('/previous_search')
    itembtn3 = tb.types.KeyboardButton('/saved_search')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.chat.id, "Choose search", reply_markup=markup)


# new search !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["new_search"])
def new_search(message):
    set_info(str(message.chat.id) + 'search_parameters', get_info('default_search'))
    parameters = get_info(str(message.chat.id) + 'saved_search_parameters')
    if parameters == 'null':
        parameters == get_info('default_search')
    set_info(str(message.chat.id) + 'search_parameters', parameters)
    search_menu(message)
    search_menu(message)


# previous search !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["previous_search"])
def previous_search(message):
    search_menu(message)


# saved search !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["saved_search"])
def saved_search(message):
    parameters = get_info(str(message.chat.id) + 'saved_search_parameters')
    if parameters == 'null':
        parameters == get_info('default_search')
    set_info(str(message.chat.id) + 'search_parameters', parameters)
    search_menu(message)


# search menu!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def search_menu(message):
    markup = tb.types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = tb.types.KeyboardButton('/current_parameters')
    itembtn2 = tb.types.KeyboardButton('/change_parameters')
    itembtn3 = tb.types.KeyboardButton('/save_search_parameters')
    itembtn4 = tb.types.KeyboardButton('/start_search')
    itembtn5 = tb.types.KeyboardButton('/search')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5)
    bot.send_message(message.chat.id, "Search menu", reply_markup=markup)


# search !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["start_search"])
def start_search(message):
    set_info(str(message.chat.id) + 'state', 'search_in_process')
    if get_info(str(message.chat.id) + 'film_num') == 'null':
        set_info(str(message.chat.id) + 'film_num', '1')
    markup = tb.types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = tb.types.KeyboardButton('/next_ten')
    itembtn2 = tb.types.KeyboardButton('/find_starting_from')
    itembtn3 = tb.types.KeyboardButton('/save_search_parameters')
    itembtn4 = tb.types.KeyboardButton('/end_search')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
    bot.send_message(message.chat.id, "Search", reply_markup=markup)


# next_ten !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["next_ten"])
def next_ten(message):
    film_num = get_info(str(message.chat.id) + 'film_num')
    if film_num == 'null':
        film_num = '1'
    film_num = int(film_num)
    parameters = get_info(str(message.chat.id) + 'search_parameters')
    if parameters == 'null':
        parameters == get_info('default_search')
    df = get_ten(film_num, parameters)
    set_info(str(message.chat.id) + 'film_num', str(film_num + 10))


# find_starting_from !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["find_starting_from"])
def find_starting_from(message):
    set_info(str(message.chat.id) + 'state', 'find_starting_with')
    bot.send_message(message.chat.id, "Enter the number you want to start with")


# find_starting_from !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(func=lambda msg: msg.text is not None and msg.chat.id == 'find_starting_with')
def reply_to_message(message):
    try:
        num = int(message.text)
    except Exception:
        bot.send_message(message.chat.id, 'Wrong number. Try again')
        return
    set_info(str(message.chat.id) + 'film_num', str(num))
    set_info(str(message.chat.id) + 'state', 'search_in_process')


# end_search !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["end_search"])
def end_search(message):


    menu(message)


# save_search_parameters !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["save_search_parameters"])
def save_search_parameters(message):
    parameters = get_info(str(message.chat.id) + 'search_parameters')
    if parameters == 'null':
        parameters == get_info('default_search')
    set_info(str(message.chat.id) + 'saved_search_parameters', parameters)


# call search_menu !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["search_menu"])
def search_menu_call(message):
    search_menu(message)


# current_parameters !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["current_parameters"])
def current_parameters(message):
    set_info(str(message.chat.id) + 'state', 'current_parameters')
    parameters = get_parameters(str(message.chat.id) + 'search_parameters')
    bot.send_message(message.chat.id, text=parameters)


# change_parameters !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["change_parameters"])
def change_parameters(message):
    set_info(str(message.chat.id) + 'state', 'change_parameters')
    search_type = get_info(str(message.chat.id))
    if search_type != 'null':
        bot.send_message(message.chat.id, 'Search type not found. Please press \\search and choose search type')
        return
    markup = tb.types.ReplyKeyboardMarkup(row_width=3, one_time_keyboard=False)
    itembtn1 = tb.types.KeyboardButton('/genre')
    itembtn2 = tb.types.KeyboardButton('/sort')
    itembtn3 = tb.types.KeyboardButton('/rating')
    itembtn4 = tb.types.KeyboardButton('/subscript')
    itembtn5 = tb.types.KeyboardButton('/country')
    itembtn6 = tb.types.KeyboardButton('/kind')
    itembtn7 = tb.types.KeyboardButton('/search_menu')
    itembtn8 = tb.types.KeyboardButton('/current_parameters')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6, itembtn7, itembtn8)
    bot.send_message(message.chat.id, "Menu", reply_markup=markup)


# choose genre !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["genre"])
def genre(message):
    set_info(str(message.chat.id) + 'state', 'genre')
    search_type = get_info(str(message.chat.id))
    if search_type != 'null':
        bot.send_message(message.chat.id, 'Search type not found. Please press \\search and choose search type')
        return
    markup = tb.types.ReplyKeyboardMarkup(row_width=4, one_time_keyboard=True)
    itembtn1 = tb.types.KeyboardButton('/1')
    itembtn2 = tb.types.KeyboardButton('/2')
    itembtn3 = tb.types.KeyboardButton('/3')
    itembtn4 = tb.types.KeyboardButton('/4')
    itembtn5 = tb.types.KeyboardButton('/5')
    itembtn6 = tb.types.KeyboardButton('/6')
    itembtn7 = tb.types.KeyboardButton('/7')
    itembtn8 = tb.types.KeyboardButton('/8')
    itembtn9 = tb.types.KeyboardButton('/9')
    itembtn10 = tb.types.KeyboardButton('/10')
    itembtn11 = tb.types.KeyboardButton('/11')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6, itembtn7, itembtn8, itembtn9, itembtn10, itembtn11)
    bot.send_message(message.chat.id, 'Choose one variant:\n1 - all, 2 - anime, 3 - mystery, 4 - comedy,\n\
5 - crime, 6 - adventure, 7 - family, 8 - thriller,\n9 - horror, 10 - sci-fi, 11 - fantasy', reply_markup=markup)


# choose sort !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["sort"])
def sort(message):
    set_info(str(message.chat.id) + 'state', 'sort')
    search_type = get_info(str(message.chat.id))
    if search_type != 'null':
        bot.send_message(message.chat.id, 'Search type not found. Please press \\search and choose search type')
        return
    markup = tb.types.ReplyKeyboardMarkup(row_width=4, one_time_keyboard=True)
    itembtn1 = tb.types.KeyboardButton('/1')
    itembtn2 = tb.types.KeyboardButton('/2')
    itembtn3 = tb.types.KeyboardButton('/3')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.chat.id, 'Choose one variant:\n1 - number of rating, 2 - rating, 3 - year', reply_markup=markup)


# choose rating !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["rating"])
def rating(message):
    set_info(str(message.chat.id) + 'state', 'rating')
    search_type = get_info(str(message.chat.id))
    if search_type != 'null':
        bot.send_message(message.chat.id, 'Search type not found. Please press \\search and choose search type')
        return
    markup = tb.types.ReplyKeyboardMarkup(row_width=4, one_time_keyboard=True)
    itembtn1 = tb.types.KeyboardButton('/1')
    itembtn2 = tb.types.KeyboardButton('/2')
    markup.add(itembtn1, itembtn2)
    bot.send_message(message.chat.id, 'Choose one variant:\n1 - any rating, 2 - only high rating', reply_markup=markup)


# choose subscript !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["subscript"])
def subscript(message):
    set_info(str(message.chat.id) + 'state', 'subscript')
    search_type = get_info(str(message.chat.id))
    if search_type != 'null':
        bot.send_message(message.chat.id, 'Search type not found. Please press \\search and choose search type')
        return
    markup = tb.types.ReplyKeyboardMarkup(row_width=4, one_time_keyboard=True)
    itembtn1 = tb.types.KeyboardButton('/1')
    itembtn2 = tb.types.KeyboardButton('/2')
    itembtn3 = tb.types.KeyboardButton('/3')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.chat.id, 'Choose one variant:\n1 - all subscriptions\
\n2 - yandex plus subscription\n3 - kinopoisk with amediateka subscription', reply_markup=markup)


# choose country !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["country"])
def country(message):
    set_info(str(message.chat.id) + 'state', 'country')
    search_type = get_info(str(message.chat.id))
    if search_type != 'null':
        bot.send_message(message.chat.id, 'Search type not found. Please press \\search and choose search type')
        return
    markup = tb.types.ReplyKeyboardMarkup(row_width=4, one_time_keyboard=True)
    itembtn1 = tb.types.KeyboardButton('/1')
    itembtn2 = tb.types.KeyboardButton('/2')
    itembtn3 = tb.types.KeyboardButton('/3')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.chat.id, 'Choose one variant:\n1 - all country, 2 - foreign country, 3 - russian', reply_markup=markup)


# choose kind !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["kind"])
def kind(message):
    set_info(str(message.chat.id) + 'state', 'kind')
    search_type = get_info(str(message.chat.id))
    if search_type != 'null':
        bot.send_message(message.chat.id, 'Search type not found. Please press \\search and choose search type')
        return
    markup = tb.types.ReplyKeyboardMarkup(row_width=4, one_time_keyboard=True)
    itembtn1 = tb.types.KeyboardButton('/1')
    itembtn2 = tb.types.KeyboardButton('/2')
    itembtn3 = tb.types.KeyboardButton('/3')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.chat.id, 'Choose one variant:\n1 - all, 2 - films, 3 - serials', reply_markup=markup)


# number variant !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'])
def ft_set_parameters(message):
    try:
        num = int(message[1:]) - 1
    except Exception:
        bot.send_message(message.chat.id, 'Something was wrong')
        return
    search_parameters = get_info(str(message.chat.id) + 'search_parameters')
    parameter = get_info(str(message.chat.id) + 'state')
    parameter_variants = get_info(parameter)
    if parameter_variants == 'null' or search_parameters == 'null':
        bot.send_message(message.chat.id, 'Something was wrong')
        return
    parameter_variants = parameter_variants.split('| ')
    new_paramater = parameter_variants[num]
    num_of_new_parameter = int(parameter_variants[-1])
    search_parameters = search_parameters.split('| ')
    search_parameters[num_of_new_parameter] = new_paramater
    search_parameters = '| '.join(search_parameters)
    set_info('search_parameters', search_parameters)
    change_parameters(message)


# example of ReplyKeyboardRemove
@bot.message_handler(commands=["сортировка"])
def reply_a(message):
    markup = tb.types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, text='aa', reply_markup=markup)
    bot.send_message(message.chat.id, str(message.chat.id), reply_markup=markup)


bot.infinity_polling()
