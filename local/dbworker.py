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


def change_temp_films(key, df_ten):
    df_films = pd.read_csv("df_films.csv")
    old_temp_films = key
    if type(key) != list:
        old_temp_films = get_info(key).split('|')
    if old_temp_films[0] != 'null':
        df_films['users'] -= df_films['name'].isin(old_temp_films)
    if type(key) != str:
        df_films.to_csv('df_films.csv', index=False)
        return
    df_films['users'] += df_films['name'].isin(df_ten['name'])
    df_films = pd.concat([df_films, df_ten]).drop_duplicates('name').reset_index(drop=True)
    if df_films.shape[0] > 5000:
        df_films = df_films[df_films.users > 0]
    df_films.to_csv('df_films.csv', index=False)
    new_temp_films = list(df_ten['name'])
    set_info(key, '|'.join(new_temp_films))
