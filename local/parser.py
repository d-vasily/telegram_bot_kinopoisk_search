from bs4 import BeautifulSoup as bs
import pandas as pd
from selenium import webdriver


def data_film(l):
    l = l.split('| ')
    url = f"https://www.kinopoisk.ru/lists/navigator/{l[0]}/?sort={l[1]}&quick_filters=%2C{l[2]}%2C{l[3]}%2C{l[4]}%2C{l[5]}&tab=online&page={l[6]}"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    dr = webdriver.Chrome(chrome_options=chrome_options)
    try:
        dr.get(url)
    except Exception:
        return([])
    soup = bs(dr.page_source)
    res = soup.find_all('div', {'class': 'desktop-seo-selection-film-item__upper-wrapper'})
    if len(res) == 0:
        print('wrong site')
    return (res)


def get_row(i, raw_data):
    name = raw_data[i].find_all('p', {'class' : 'selection-film-item-meta__name'}, limit = 1)
    if (len(name) > 0): name = name[0].text
    else: return 0

    link = raw_data[i].find_all('a', {'class' : 'selection-film-item-meta__link'}, limit = 1)
    if (len(link) > 0): link = 'https://www.kinopoisk.ru' + link[0].get('href')
    else: return 0

    date = raw_data[i].find_all('p', {'class' : 'selection-film-item-meta__original-name'}, limit = 1)
    if (len(date) > 0): date = date[0].text.split(',')[-1]
    else: return 0

    x = raw_data[i].find_all('span', {'class' : 'selection-film-item-meta__meta-additional-item'}, limit = 2)
    if (len(x) > 1): country = x[0].text; gen = x[1].text
    else: return 0

    rating = raw_data[i].find_all('span', {'class' : r'rating__value rating__value_positive'}, limit = 1)
    if (len(rating) == 0): rating = raw_data[i].find_all('span', {'class' : r'rating__value rating__value_neutral'}, limit = 1)
    if (len(rating) > 0): rating = rating[0].text
    else: return 0

    rating_count = raw_data[i].find_all('span', {'class' : 'rating__count'}, limit = 1)
    if (len(rating_count) > 0): rating_count = rating_count[0].text
    else: return 0

    return [name, date, country, gen, rating, rating_count, link]



def get_add_info(df, name):
    if name not in list(df.name):
        return('Something wrong')
    index = df.loc[(df.name == name)].index[0]
    if str(df.iloc[index]['audio']) != '0':
        return df
    link = df.iloc[index]['link']
    dr = webdriver.Chrome()
    try:
        dr.get(link)
    except:
        return('Something wrong')
    soup1 = BeautifulSoup(dr.page_source)
    info = soup1.find_all('div', {'class' : 'styles_valueLight__1j0RO'}, limit=2)
    if (len(info) > 1): audio_track = info[0].text; subtitles = info[1].text
    else: return('Something wrong')
    description = soup1.find_all('p', {'class': 'styles_paragraph__2Otvx'}, limit=1)
    if (len(description) > 0): description = description[0].text
    else: return('Something wrong')
    df.loc[index, 'audio'] = audio_track
    df.loc[index, 'subtitles'] = subtitles
    df.loc[index, 'description'] = description
    return df


def add_info_to_str(df, name):
    index = df.loc[(df.name == name)].index[0]
    elem = df.iloc[index]
    country = elem['country']
    date = elem['date']
    audio_track = elem['audio']
    subtitles = elem['subtitles']
    description = elem['description']
    s = name + '\n\n'
    s += 'Страна:\n' + country + '\n\n'
    s += 'Год:\n' + str(date) + '\n\n'
    s += 'Язык озвучки:\n' + audio_track + '\n\n'
    s += 'Субтитры:\n' + subtitles + '\n\n'
    s += 'Описание:\n' + description
    return s



def get_ten(num, l):
    l += '| ' + str((num - 1) // 50 + 1)
    num = (num - 1) % 50
    raw_data = data_film(l)
    if (len(raw_data) == 0):
        return (0)
    df = pd.DataFrame(columns=['name','date','country','genre','rating',\
'rating_count', 'link', 'audio', 'subtitles', 'description', 'users'])
    max_ind = len(raw_data)
    count = 0
    while (num < max_ind and count < 10):
        a = get_row(num, raw_data)
        if (a):
            a.extend([0, 0, 0, 1])
            df.loc[count] = a
            count += 1
        num += 1
    return df


def df_to_str(df):
    df = df.set_index('name')
    s = ''
    for i in range(len(df)):
        name = df.index[i]
        s += '<b>' + str(name) + '</b>\n\n'
        s += 'Рейтинг' + ' ' * 17 + '-' + ' ' * 5 + str(df.loc[name]['rating']) + '\n'
        s += 'Кол-во оценок     ' + '-' + ' ' * 5 + str(df.loc[name]['rating_count']) + '\n'
        genre_list = str(df.loc[name]['genre']).split(', ')
        s += 'Жанр' + ' ' * 22 + '-' + ' ' * 5 + genre_list[0]
        if len(genre_list) == 2:
            s += '\n' + ' ' * 39 + genre_list[1]
        s += '\n'
        if i != len(df) - 1:
            s += '\n\n\n'
    return(s)


# data_film(genre='',sort='', rating='', subscript='available_online', country='', kind=''(film/serial), page=''):
# genre = ['', 'anime', 'mystery', 'comedy', 'crime', 'adventure', 'family', 'thriller', 'horror', 'sci-fi', 'fantasy']
# sort = ['', 'popularity', 'year']
# rating = ['', 'high_rated']
# subscript= ['available_online', 'yandex_plus_subscription', 'kinopoisk_with_amediateka_subscription']
# country = ['', 'foreign', 'russian']
# kind = ['', 'films', 'serials']

# search_param = '| | | yandex_plus_subscription| foreign| | '
#{'genre': '', 'sort': 'year', 'rating': '', 'subscript': 'yandex_plus_subscription',\
 #               'country': 'foreign', 'kind': 'films', 'page': ''}
#data_film(genre='',sort='', rating='', subscript='available_online', country='', kind=''(film/serial), page=''):
# data_ten = get_ten(51, search_param)
