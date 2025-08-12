import os
import shutil
import time

from pprint import pprint

from parser import AJ_Parser, ListParser
from index import Indexator

import subprocess

import sqlite3
import datetime

import re
import xml
import xml.etree.ElementTree as ET


from rename_uc import clean_badchars

TITLES_DIR = r'~\Downloads\TITLES'


FF_DB = r'~\AppData\Roaming\Mozilla\Firefox\Profiles\48hcvyaq.123\places.sqlite'
FF_LIST = {
    'plan': 'AJ_PLAN',
    'ready': 'AJ_READY',
    'done': 'AJ_DONE',
}

######### PARSER ########

def check_ff2(list_type='ready'):
    title_id_url = {}

    connection = sqlite3.connect(FF_DB)
    cursor = connection.cursor()

    select_sql = '''
    SELECT moz_bookmarks.title, moz_places.url FROM moz_bookmarks 
    INNER JOIN moz_places ON moz_bookmarks.fk=moz_places.id
    WHERE moz_bookmarks.parent in 
    (SELECT id FROM moz_bookmarks WHERE title='%s')
    ''' % (FF_LIST[list_type])
    cursor.execute(select_sql)

    for line in cursor.fetchall():
        title_name_, title_url = line

        if 'animejoy' in title_url:
            # if ' субтитры ' in title_name_:
            title_id = AJ_Parser.extract_id(AJ_Parser, title_url)
            title_id_url[title_id] = title_url

    cursor.close()
    connection.close()

    return title_id_url


def index_not_html():

    parser = AJ_Parser()
    html = parser.check_html()

    index = Indexator()
    index_titles = index.read_db()

    print('INDEX: ', len(index_titles))

    title_ids = dict((value[1], key) for key, value in html.items())

    not_in_html = []
    for title_name1 in index_titles:
        try:
            title_id = title_ids[title_name1]
        except KeyError:
            # print('NOT IN HTML: ', title_name)
            not_in_html.append(title_name1)
            print(title_name1)

    pprint(sorted(not_in_html))
    print('NOT IN HTML: ', len(not_in_html))


def index_not_done():
    # rescan_dir()
    parser = AJ_Parser()
    html = parser.check_html()

    index = Indexator()
    index_titles = index.read_db()
    print('INDEX: ', len(index_titles))

    title_ids = dict((value[1], key) for key, value in html.items())
    index_ids = [title_ids[title_name] for title_name in index_titles]

    done_id_url = check_ff2('done')
    done_ids = done_id_url.keys()
    print('DONE:', len(done_ids))

    index_not_done_keys = list(set(done_ids) - set(index_ids))
    print(index_not_done_keys)
    #
    links_index_not_done = [html[key][0] for key in index_not_done_keys]
    print(links_index_not_done)
    print('INDEX NOT DONE: ', len(links_index_not_done))

    ListParser.export_autoweb_bat(links_index_not_done, 'INDEX_NOT_DONE.bat')


if __name__ == '__main__':
    # tl = scan_dir(r'C:\Users\NATI\Downloads\TITLES')
    # write_db(tl)

    # print(os.path.exists('../'))
    # print(os.path.abspath('../'))

    index_not_html()

    # parser = AJ_Parser()
    # html_lst = parser.check_html()
    # pprint(len(html_lst))

    # tl = check_dir(r'C:\Users\NATI\Downloads\TITLES')
    # index_not_done()

    # db = check_index()
    # print(db[:10])
    # done = set(check_ff('done'))

    # move_autosave()
    #
    # ready_lst = check_ff2('ready')
    # done_lst = check_ff2('done')
    # plan_lst = check_ff2('plan')
    #
    # html_lst = check_html2()
    #
    # not_in_html = []
    #
    # miss_ready = list(set(ready_lst.keys()) - set(html_lst.keys()))
    # not_in_html.extend([ready_lst[key] for key in miss_ready])
    #
    # miss_done = list(set(done_lst.keys()) - set(html_lst.keys()))
    # not_in_html.extend([done_lst[key] for key in miss_done])
    #
    # miss_plan = list(set(plan_lst.keys()) - set(html_lst.keys()))
    # not_in_html.extend([plan_lst[key] for key in miss_plan])
    #
    # print(not_in_html)
    # autoweb_bat(not_in_html)


    # index_not_base()


    # ready = set(check_ff('ready'))
    # plan = set(check_ff('plan'))

    # to_process = db - done
    # #
    # pprint(sorted(list(to_process)))
    # print(len(to_process))

    # pprint(done)
    # print('Судьба Девочка-волшебница Иллия (1 сезон)' in done)

