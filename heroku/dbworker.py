from vedis import Vedis
import pandas as pd

db_file = 'users.vdb'


def get_info(key):
    with Vedis(db_file) as db:
        try:
            return db[key].decode()
        except KeyError:
            return 'null'


def set_info(key, value):
    with Vedis(db_file) as db:
        try:
            db[key] = value
            return True
        except Exception:
            return False


def del_info(key):
    with Vedis(db_file) as db:
        try:
            del(db[key])
            return True
        except Exception:
            return False


def get_parameters(key):
    res = get_info(key)
    if res == 'null':
        return 'Parameters are not found'
    res = res.split('| ')
    res = list(map(lambda x: 'all' if x == '' else x, res))
    if res[1] == 'all':
        res[1] = 'number of ratings'
    if res[5] == 'all':
        res[5] = 'films and serials'
# data_film(genre='',sort='', rating='', subscript='available_online', country='', kind=''(film/serial), page=''):
    return f'genre - {res[0]}\nsort - {res[1]}\nrating - {res[2]}\n\
subscript - {res[3]}\ncountry - {res[4]}\nkind - {res[5]}'


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


def get_ten(num, params):
# data_film(genre='',sort='', rating='', subscript='available_online', country='', kind=''(film/serial), page=''):
    params = params.split('| ')
    genre, sort, rating, subscript, country, kind = params
    df = pd.read_csv("df_films.csv")
    lim = min(len(df.index), num + 9)
    conditions = df['genre'].str.contains(genre)
    sorting = 'date'
    if sort == '':
        sorting = 'rating_count'
    elif sort == 'popularity':
        sorting = 'rating'
    if rating == 'high_rated':
        conditions &= (df['rating'] > 7.0)
    if country == 'foreign':
        conditions &= (df['country'].str.contains('СССР') == False)
        conditions &= (df['country'].str.contains('Россия') == False)
    elif country == 'russian':
        conditions &= (df['country'].str.contains('Россия'))
    if kind == 'films':
        conditions &= (df['kind'] == 'film')
    elif kind == 'serials':
        conditions &= (df['kind'] == 'serial')
    if subscript == 'yandex_plus_subscription':
        conditions &= (df['subscription'] == 'По подписке Плюс')
    elif subscript == 'kinopoisk_with_amediateka_subscription':
        conditions &= (df['subscript'] == 'По подписке Плюс Мульти с Амедиатекой')
    df = df[conditions].sort_values(by=sorting, ascending=False)
    df = df.iloc[num - 1:lim]
    return df
