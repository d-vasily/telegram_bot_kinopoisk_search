db_file = 'users.vdb'
from vedis import Vedis


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


def del_state(user_id):
    with Vedis(db_file) as db:
        try:
            del(db[user_id])
            return True
        except:
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
    return f'genre - {res[0]}; sort - {res[1]}; rating - {res[2]};\
\nsubscript - {res[3]}; country - {res[4]}; kind - {res[5]}; page - {res[6]}'
