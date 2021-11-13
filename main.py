import pandas as pd
import telebot as tb
from os.path import exists

from dbworker import *
from parser import *

# default settings !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
if not (exists('df_films.csv') and exists('users.vdb')):
    df = pd.DataFrame(columns=['name', 'date', 'country', 'genre', 'rating',
                               'rating_count', 'link', 'audio', 'subtitles', 'description', 'users'])
    df.to_csv('df_films.csv', index=False)
    del df
    set_info('default_search', '| | | yandex_plus_subscription| foreign| ')
    set_info('genre', '| anime| mystery| comedy| crime| adventure| family| thriller| horror| sci-fi| fantasy| 1')
    set_info('sort', '| popularity| year| 2')
    set_info('rating', '| high_rated| 3')
    set_info('subscript', 'available_online| yandex_plus_subscription| kinopoisk_with_amediateka_subscription| 4')
    set_info('country', '| foreign| russian| 5')
    set_info('kind', '| films| serials| 6')


# kinopoist_search_bot
TOKEN = ''
bot = tb.TeleBot(token=TOKEN)
bot.remove_webhook()


# commands !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=['commands'])
def commands(message):
    set_info(str(message.chat.id) + 'state', 'commands')
    text = (
        "<b>To search some films</b>\n\n"
        "1. Main menu:\n/search - go to the search type menu\n\n"
        "2. Search type menu:\n Choose search type:\n"
        "/new_search - choose default search paramaters\n"
        "/saved_search - choose saved search paramaters\n"
        "/previous_search - choose previous search\n\n"
        "3. Search settings:\n"
        "/current_parameters - show current search parameters\n"
        "/change_parameters - go to the paramaters menu to change some paramaters\n"
        "/save_search_parameters - save search paramaters\n"
        "/start_search - start search\n\n"
        "4. Search menu:\n"
        "/find_starting_from - write number to find starting from it\n"
        "/next_ten - show next ten films in search"
        "/additional_info - choose films and see additional info about them\n"
        "/save_films - choose films and add them to personal list"
        "/end_search - exit the search menu\n\n\n"
        "<b>To see films from personal list</b>\n\n"
        "/my_films - go to my_films menu\n"
        "/films_list - show personal film list\n"
        "/films_info - show main info about films\n"
        "/additional_info - choose films and see additional info about them\n"
        "/delete_films - choose films and remove them from personal list\n"
        "/menu - main menu"
    )
    bot.send_message(message.chat.id, text, parse_mode='HTML')


# menu !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["menu"])
def menu(message):
    set_info(str(message.chat.id) + 'state', 'menu')
    markup = tb.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    itembtn1 = tb.types.KeyboardButton('/search')
    itembtn2 = tb.types.KeyboardButton('/my_films')
    itembtn3 = tb.types.KeyboardButton('/commands')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.chat.id, "Menu", reply_markup=markup)


# my_films !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["my_films"])
def my_films(message):
    set_info(str(message.chat.id) + 'state', 'my_films')
    markup = tb.types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = tb.types.KeyboardButton('/films_list')
    itembtn2 = tb.types.KeyboardButton('/films_info')
    itembtn3 = tb.types.KeyboardButton('/additional_info')
    itembtn4 = tb.types.KeyboardButton('/delete_films')
    itembtn5 = tb.types.KeyboardButton('/menu')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5)
    bot.send_message(message.chat.id, text='My films', reply_markup=markup)


# delete_films !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["delete_films"])
def delete_films(message):
    film_list = get_info(str(message.chat.id) + 'saved_films').split('|')
    if film_list[0] == 'null' or len(film_list[0]) == 0:
        bot.send_message(message.chat.id, "You have not saved films")
        my_films(message)
        return
    output = ''
    for i in range(len(film_list)):
        output += str(i + 1) + f'. {film_list[i]}\n'
    bot.send_message(message.chat.id, 'Write films number to delete:\n' + output)
    set_info(str(message.chat.id) + 'state', 'delete_films')


# delete_films numbers !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(func=lambda msg: msg.text is not None and get_info(str(msg.chat.id) + 'state') == 'delete_films')
def delete_films_numbers(message):
    film_list = get_info(str(message.chat.id) + 'saved_films').split('|')
    if film_list[0] == 'null' or len(film_list[0]) == 0:
        bot.send_message(message.chat.id, "No films")
        my_films(message)
        return
    list_num = check_num(message.text.split(), film_list)
    if len(list_num) == 0:
        bot.send_message(message.chat.id, 'Wrong number.')
        my_films(message)
        return
    film_list_to_del = [film_list[i] for i in list_num]
    change_temp_films(film_list_to_del, '')
    film_list = [film for film in film_list if film not in film_list_to_del]
    set_info(str(message.chat.id) + 'saved_films', '|'.join(film_list))
    my_films(message)


# films_info !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["films_info"])
def films_info(message):
    film_list = get_info(str(message.chat.id) + 'saved_films').split('|')
    if film_list[0] == 'null' or len(film_list[0]) == 0:
        bot.send_message(message.chat.id, "You have not saved films")
        my_films(message)
        return
    df_films = pd.read_csv("df_films.csv")
    df_films = df_films[df_films['name'].isin(film_list)]
    output = df_to_str(df_films)
    bot.send_message(message.chat.id, output, parse_mode='HTML')
    my_films(message)


# films_list !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["films_list"])
def films_list(message):
    film_list = get_info(str(message.chat.id) + 'saved_films').split('|')
    if film_list[0] == 'null' or len(film_list[0]) == 0:
        bot.send_message(message.chat.id, "You have not saved films")
        my_films(message)
        return
    output = ''
    for i in range(len(film_list)):
        output += str(i + 1) + f'. {film_list[i]}\n'
    bot.send_message(message.chat.id, output)
    my_films(message)


# search !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["search"])
def search(message):
    set_info(str(message.chat.id) + 'state', 'search')
    markup = tb.types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    itembtn1 = tb.types.KeyboardButton('/new_search')
    itembtn2 = tb.types.KeyboardButton('/previous_search')
    itembtn3 = tb.types.KeyboardButton('/saved_search')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.chat.id, "Choose search type", reply_markup=markup)


# new search !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["new_search"])
def new_search(message):
    set_info(str(message.chat.id) + 'film_num', '1')
    parameters = get_info('default_search')
    set_info(str(message.chat.id) + 'search_parameters', parameters)
    search_menu(message)


# previous search !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["previous_search"])
def previous_search(message):
    parameters = get_info(str(message.chat.id) + 'search_parameters')
    if parameters == 'null':
        set_info(str(message.chat.id) + 'search_parameters', get_info('default_search'))
    search_menu(message)


# saved search !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["saved_search"])
def saved_search(message):
    set_info(str(message.chat.id) + 'film_num', '1')
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
    bot.send_message(message.chat.id, 'Search menu', reply_markup=markup)


# search !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["start_search"])
def start_search(message):
    set_info(str(message.chat.id) + 'state', 'search_in_process')
    if get_info(str(message.chat.id) + 'film_num') == 'null':
        set_info(str(message.chat.id) + 'film_num', '1')
    markup = tb.types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = tb.types.KeyboardButton('/find_starting_from')
    itembtn2 = tb.types.KeyboardButton('/next_ten')
    itembtn3 = tb.types.KeyboardButton('/additional_info')
    itembtn4 = tb.types.KeyboardButton('/save_films')
    itembtn5 = tb.types.KeyboardButton('/save_search_parameters')
    itembtn6 = tb.types.KeyboardButton('/end_search')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6)
    bot.send_message(message.chat.id, 'Search in process', reply_markup=markup)


# end_search !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["end_search"])
def end_search(message):
    film_list = get_info(str(message.chat.id) + 'temp_films').split('|')
    if film_list[0] == 'null' or len(film_list[0]) == 0:
        menu(message)
        return
    df_films = pd.read_csv("df_films.csv")
    df_films['users'] -= df_films['name'].isin(film_list)
    df_films.to_csv('df_films.csv', index=False)
    menu(message)


# save_films numbers !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(func=lambda msg: msg.text is not None and get_info(str(msg.chat.id) + 'state') == 'save_films')
def save_films_num(message):
    film_list = get_info(str(message.chat.id) + 'temp_films').split('|')
    if film_list[0] == 'null' or len(film_list[0]) == 0:
        bot.send_message(message.chat.id, "No films")
        start_search(message)
        return
    list_num = check_num(message.text.split(), film_list)
    if len(list_num) == 0:
        bot.send_message(message.chat.id, 'Wrong number. Try again')
        start_search(message)
        return
    film_list = [film_list[i] for i in list_num]
    df_films = pd.read_csv("df_films.csv")
    df_films['users'] += df_films['name'].isin(film_list)
    df_films.to_csv('df_films.csv', index=False)
    saved_films = get_info(str(message.chat.id) + 'saved_films').split('|')
    if saved_films[0] == 'null' or saved_films[0] == '':
        saved_films = []
    saved_films.extend(film_list)
    saved_films = '|'.join(list(set(saved_films)))
    set_info(str(message.chat.id) + 'saved_films', saved_films)
    set_info(str(message.chat.id) + 'state', 'search_in_process')
    bot.send_message(message.chat.id, 'Films saved')


# save_films !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["save_films"])
def save_films(message):
    set_info(str(message.chat.id) + 'state', 'save_films')
    film_list = get_info(str(message.chat.id) + 'temp_films').split('|')
    if film_list[0] == 'null' or len(film_list[0]) == 0:
        bot.send_message(message.chat.id, "No films")
        start_search(message)
        return
    s = ''
    for i in range(len(film_list)):
        s += str(i + 1) + f') {film_list[i]}\n'
    bot.send_message(message.chat.id, f"Write numbers of films:\n{s}")


# additional_info numbers !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(func=lambda msg: msg.text is not None and get_info(str(msg.chat.id) + 'state')[:15] == 'additional_info')
def additional_info_number(message):
    films = get_info(str(message.chat.id) + 'state')[15:]
    film_list = get_info(str(message.chat.id) + films).split('|')
    if film_list[0] == 'null' or len(film_list[0]) == 0:
        bot.send_message(message.chat.id, "No films")
        start_search(message)
        return
    list_num = check_num(message.text.split(), film_list)
    if len(list_num) == 0:
        bot.send_message(message.chat.id, 'Wrong number.')
        start_search(message)
        return
    film_list = [film_list[i] for i in list_num]
    df_films = pd.read_csv("df_films.csv")
    for film in film_list:
        df_films = get_add_info(df_films, film)
        if type(df_films) == str:
            bot.send_message(message.chat.id, "Something was wrong")
            start_search(message)
            return
        output = add_info_to_str(df_films, film)
        bot.send_message(message.chat.id, output, parse_mode='HTML')
    state = 'search_in_process'
    if films == 'saved_films':
        state = 'my_films'
    set_info(str(message.chat.id) + 'state', state)
    df_films.to_csv("df_films.csv")


def check_num(list_num, film_list):
    for i in range(len(list_num)):
        try:
            num = int(list_num[i]) - 1
        except Exception:
            return []
        if num > len(film_list):
            return []
        list_num[i] = num
    list_num = list(set(list_num))
    return list_num


# see_add_info !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["additional_info"])
def additional_info(message):
    state = get_info(str(message.chat.id) + 'state')
    if state not in ['search_in_process', 'my_films']:
        bot.send_message(message.chat.id, "Something wrong")
        return
    films = 'temp_films'
    if state == 'my_films':
        films = 'saved_films'
    set_info(str(message.chat.id) + 'state', 'additional_info' + films)
    film_list = get_info(str(message.chat.id) + films).split('|')
    if film_list[0] == 'null' or len(film_list[0]) == 0:
        bot.send_message(message.chat.id, "No films")
        return
    s = ''
    for i in range(len(film_list)):
        s += str(i + 1) + f'. {film_list[i]}\n'
    bot.send_message(message.chat.id, f"Write numbers of films:\n{s}")


# next_ten !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["next_ten"])
def next_ten(message):
    if get_info(str(message.chat.id) + 'state') != 'search_in_process':
        bot.send_message(message.chat.id, "Something wrong")
        return
    bot.send_message(message.chat.id, "Waiting...")
    film_num = get_info(str(message.chat.id) + 'film_num')
    if film_num == 'null':
        film_num = '1'
    film_num = int(film_num)
    parameters = get_info(str(message.chat.id) + 'search_parameters')
    if parameters == 'null':
        parameters == get_info('default_search')
    df_ten = get_ten(film_num, parameters)
    if type(df_ten) == int:
        bot.send_message(message.chat.id, "Something wrong")
        return
    output = df_to_str(df_ten)
#    bot.send_message(message.chat.id, output)
    bot.send_message(message.chat.id, output, parse_mode='HTML')
    set_info(str(message.chat.id) + 'film_num', str(film_num + 10))
    change_temp_films(str(message.chat.id) + 'temp_films', df_ten)


# find_starting_from !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(commands=["find_starting_from"])
def find_starting_from(message):
    set_info(str(message.chat.id) + 'state', 'find_starting_from')
    bot.send_message(message.chat.id, "Enter the number you want to start with")


# find_starting_from !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(func=lambda msg: msg.text is not None and get_info(str(msg.chat.id) + 'state') == 'find_starting_from')
def reply_to_message(message):
    if message.text == 'cancel':
        set_info(str(message.chat.id) + 'state', 'search_in_process')
        return
    try:
        num = int(message.text)
    except Exception:
        bot.send_message(message.chat.id, 'Wrong number. Try again')
        start_search(message)
        return
    set_info(str(message.chat.id) + 'film_num', str(num))
    start_search(message)


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
    bot.send_message(message.chat.id, 'Change parameters', reply_markup=markup)


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
        num = int(message.text[1:]) - 1
    except Exception:
        bot.send_message(message.chat.id, 'Something was wrong')
        change_parameters(message)
        return
    search_parameters = get_info(str(message.chat.id) + 'search_parameters').split('| ')
    parameter = get_info(str(message.chat.id) + 'state')
    parameter_variants = get_info(parameter).split('| ')
    if parameter_variants[0] == 'null' or search_parameters[0] == 'null':
        bot.send_message(message.chat.id, 'Something was wrong')
        change_parameters(message)
        return
    new_paramater = parameter_variants[num]
    num_of_new_parameter = int(parameter_variants[-1]) - 1
    search_parameters[num_of_new_parameter] = new_paramater
    search_parameters = '| '.join(search_parameters)
    set_info(str(message.chat.id) + 'search_parameters', search_parameters)
    change_parameters(message)


bot.infinity_polling()
