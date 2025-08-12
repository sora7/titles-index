import sqlite3
import parser
from pprint import pprint

DB_PATH = r'~\AppData\Roaming\Mozilla\Firefox\Profiles\48hcvyaq.123\places.sqlite'
DB_LIST = {
    'plan':     'AJ_PLAN',
    'ready':    'AJ_READY',
    'done':     'AJ_DONE',
    'ongoing':  'AJ_ONGOING',
}

def select_ids(list_type):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    select_sql = '''
        SELECT moz_places.url 
        FROM moz_bookmarks 
        INNER JOIN moz_places 
        ON moz_places.id = moz_bookmarks.fk 
        WHERE moz_bookmarks.parent = 
        (SELECT moz_bookmarks.id FROM moz_bookmarks WHERE moz_bookmarks.title = '%s')
    ''' % (DB_LIST[list_type])
    cursor.execute(select_sql)

    ff_ids = []
    for line in cursor.fetchall():
        title_url, = line

        if 'anime' in title_url:
            ff_id = parser.AJ_Parser.extract_id(parser.AJ_Parser, title_url)
            ff_ids.append(ff_id)

    cursor.close()
    connection.close()


    connection = sqlite3.connect('../data/titles.db')
    cursor = connection.cursor()

    select_sql = '''
            SELECT html.url
            FROM html 
            WHERE html.name IN 
            (
                SELECT titles.name 
                FROM titles
                WHERE titles.shot_time IN (SELECT MAX(shot_time) FROM titles)
            )
            ORDER BY html.name
        '''

    cursor.execute(select_sql)
    index_ids = []
    for url, in cursor.fetchall():
        # print(url)
        index_id = parser.AJ_Parser.extract_id(parser.AJ_Parser, url)
        index_ids.append(index_id)

    # print(index_ids)

    result_ids = list(set(ff_ids) & set(index_ids))

    select_sql = '''
            SELECT html.name, html.url
            FROM html 
            WHERE html.site_id IN ('%s')
            ORDER BY html.name
        ''' % ("', '".join(result_ids))

    cursor.execute(select_sql)
    for name, url in cursor.fetchall():
        print(url)

    select_sql2 = '''
            SELECT html.name, html.url
            FROM html 
            WHERE html.site_id IN ('%s')
            AND html.name NOT IN 
            (
                SELECT titles.name 
                FROM titles
                WHERE titles.shot_time IN (SELECT MAX(shot_time) FROM titles)
            )
            ORDER BY html.name
        ''' % ("', '".join(ff_ids))

    select_sql1 = '''
            SELECT html.name, html.url
            FROM html 
            INNER JOIN titles
            ON titles.name = html.name 
            WHERE html.site_id IN ('%s')
            AND titles.shot_time IN (SELECT MAX(shot_time) FROM titles) 
            ORDER BY html.name
        ''' % ("', '".join(ff_ids))


        # title_name, title_url = line
        # print(title_name, title_url)

    cursor.close()
    connection.close()




class BookmarkBrowser(object):
    def __init__(self):
        pass

    def check_ff3(self, list_type='ready'):
        title_id_url = {}

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        select_sql = '''
        SELECT moz_bookmarks.title, moz_places.url FROM moz_bookmarks 
        INNER JOIN moz_places ON moz_bookmarks.fk=moz_places.id
        WHERE moz_bookmarks.parent in 
        (SELECT id FROM moz_bookmarks WHERE title='%s')
        ''' % (DB_LIST[list_type])
        cursor.execute(select_sql)

        for line in cursor.fetchall():
            title_name_, title_url = line

            if 'animejoy' in title_url:
                # if ' субтитры ' in title_name_:
                title_id = parser.AJ_Parser.extract_id(parser.AJ_Parser, title_url)
                title_id_url[title_id] = title_url

        cursor.close()
        connection.close()

        return title_id_url

    def transfer(self, title_id, old_dir, new_dir):

        pass


if __name__ == '__main__':
    pass
    # browser = BookmarkBrowser()
    # lst = browser.check_ff3('done')
    # pprint(lst)