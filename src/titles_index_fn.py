import os
import shutil
import time
import random
from pprint import pprint
from html.parser import HTMLParser
from xml.etree import ElementTree as ET
import subprocess

import sqlite3
import datetime

import re
import xml
import xml.etree.ElementTree as ET


from rename_uc import clean_badchars

TITLES_DIR = r'~\Downloads\TITLES'
INDEX_DB = '../data/titles.db'

FF_DB = r'~\AppData\Roaming\Mozilla\Firefox\Profiles\48hcvyaq.123\places.sqlite'
FF_LIST = {
    'plan': 'AJ_PLAN',
    'ready': 'AJ_READY',
    'done': 'AJ_DONE',
}
HTML_DIR = r'../data/html'
NO_URLS = '../data/nourls.html'
NO_TITLES = '../data/notitles.html'

REC_URLS = '../data/recurls.html'
REC_BAT = '../data/REC_AUTOWEB.bat'

NO_HTML = '../data/HTML_AUTOWEB.bat'


######## SCANNER #######

def scan_dir(test_dir):
    titles = []

    title = dict()
    title['eps'] = []
    for file_name in os.listdir(test_dir):
        file_full = os.path.join(test_dir, file_name)
        if os.path.isdir(file_full):
            titles.extend(scan_dir(file_full))
        elif file_name.endswith('mp4'):
            title['dir'] = test_dir
            title['name'] = os.path.basename(test_dir)
            title['eps'].append(file_name)

    if len(title['eps']) > 0:
        titles.append(title)
    return titles


def write_db(tl):
    connection = sqlite3.connect(INDEX_DB)
    cursor = connection.cursor()

    shot_time = datetime.datetime.now()
    for title in tl:
        sql = ("INSERT "
               "INTO titles (name, eps, dir, shot_time) "
               "VALUES ('{}', {}, '{}', '{}')"
               ).format(title['name'], str(len(title['eps'])), title['dir'], shot_time)
        cursor.execute(sql)
        connection.commit()

    cursor.close()
    connection.close()


def rescan_dir():
    tl = scan_dir(r'h:/.titles')
    write_db(tl)

######### PARSER ########


def move_autosave():
    src_dir = r'C:\Users\Evoo\Downloads'
    dst_dir = HTML_DIR

    for file in os.listdir(src_dir):
        if file.startswith('AutoSave_') or file.startswith('page('):
            if file.endswith('htm') or file.endswith('html'):
                old_filepath = os.path.join(src_dir, file)
                new_filepath = os.path.join(dst_dir, file)

                if os.path.exists(new_filepath):
                    filename, ext = os.path.splitext(file)
                    filename = str(int(time.time()))
                    new_filepath = os.path.join(dst_dir, ''.join([filename, ext]))

                shutil.move(old_filepath, new_filepath)


def export_html_list(lst, filepath):
    html = ET.Element('html')
    body = ET.Element('body')
    html.append(body)

    ol = ET.Element('ol')
    body.append(ol)
    for line in lst:
        li = ET.Element('li')
        ol.append(li)
        a = ET.Element('a', attrib={'href': line})
        li.append(a)
        a.text = line

    with open(filepath, 'wb') as fh:
        ET.ElementTree(html).write(fh, encoding='utf-8')


def export_autoweb_bat(url_list, filename='AUTOWEB.bat', rand=False):
    batch_lines = ['@echo off']
    i = 0
    total = len(url_list)
    if rand:
        random.shuffle(url_list)
    for url in url_list:
        i += 1
        batch_lines.append(r'"c:\Program Files\Mozilla Firefox\firefox.exe" -private-window %s' % url)
        batch_lines.append("echo PROGRESS [{} / {}] ({:.2f} %%)".format(i, total, i / total * 100))
        batch_lines.append('TIMEOUT %s' % str(random.choice([i for i in range(10, 20)])))

    with open(filename, 'w') as fh:
        fh.write('\n'.join(batch_lines))


def extract_id(url_text):
    re_title_id = ('.*?[/]([0-9]{1,})[-].*?',)
    title_id_ = extract(re_title_id, url_text)[0]
    return title_id_

# re_name_jp = r'<h2 class="romanji">(.*?)</h2>'


def extract_url(html_text):
    re_url_lst = (
        r'<meta property="og:url" content="(.*?)" />',
        r'<a id="dle-comm-link" href="(.*?)#comment">'
    )
    return extract(re_url_lst, html_text)


def extract_name(html_text):
    re_name_ru = (r'<h1 class="h2 ntitle" itemprop="name">(.*?)</h1>',)

    return extract(re_name_ru, html_text)


def extract_rec_urls(html_text):
    rec_urls = []

    re_rec_urls = (r'<div class="story_line">.*?<a href="(.*?)" title="',)
    rec_urls.extend(extract(re_rec_urls, html_text, dotall=True))

    re_rec_url_block = (r'<!--spoiler_text-->(.*?)<!--spoiler_text_end-->',)
    rec_url_block = extract(re_rec_url_block, html_text, dotall=True)

    if len(rec_url_block) > 0:
        re_rec_urls2 = (r'<li><a href="(.*?)">.*?</a></li>', )
        rec_urls.extend(extract(re_rec_urls2, rec_url_block[0]))

    return rec_urls


def extract_links(html_text):
    re_link = (r'<h2 class="ntitle"><a href="(https://animejoy.ru/.*?/[0-9]{1,5}-.*?.html)">',)
    return extract(re_link, html_text)


def extract(regex_list, text, dotall=False):
    result = []
    for regex in regex_list:
        if dotall:
            result.extend(re.findall(re.compile(regex, re.DOTALL), text))
        else:
            result.extend(re.findall(re.compile(regex), text))
    return result


class AJ_Parser(object):
    html_list = {}
    rec_list = {}
    add_list = {}

    def __init__(self):
        pass

    def add_title(self):
        pass

    def check_html(self):
        pass

    def write_db(self):
        pass

    def read_db(self):
        pass

def check_html2():
    move_autosave()

    html_list = {}
    rec_dict = {}
    for root, subdirs, files in os.walk(HTML_DIR):
        for file_name in files:
            if file_name.endswith('.htm') or file_name.endswith('.html'):
                file_full = os.path.join(root, file_name)
                file_ctime = int(os.path.getctime(file_full))
                with open(file_full, 'r', encoding='utf-8') as fh:
                    html_text = fh.read()

                names = extract_name(html_text)
                if len(names) > 0:
                    title_name = clean_badchars(names[0].split(' [')[0])
                    # print(name)
                    urls = extract_url(html_text)
                    if len(urls) > 0:
                        title_url = urls[0]
                        title_id = extract_id(title_url)

                        rec_urls = extract_rec_urls(html_text)
                        if len(rec_urls) > 0:
                            for rec_url in rec_urls:
                                rec_id = extract_id(rec_url)
                                rec_dict[rec_id] = rec_url
                        else:
                            print('NO REC: ', file_name)

                        if title_id in html_list.keys():
                            print('DUBL: ', file_name, title_url)
                            base_file, base_ctime = html_list[title_id][2:]
                            print('BASE:', base_ctime, 'FILE:', file_ctime)

                            if base_ctime > file_ctime:
                                os.remove(file_full)
                            else:
                                html_list[title_id] = (title_url, title_name, file_name, file_ctime)
                                file_full2 = os.path.join(root, base_file)
                                os.remove(file_full2)
                        else:
                            html_list[title_id] = (title_url, title_name, file_name, file_ctime)
                    else:
                        print('NO URL: ', file_name)
                else:
                    additional_urls = extract_links(html_text)
                    if len(additional_urls) > 0:
                        print('ADD FOUND: ', len(additional_urls))
                        for additional_url in additional_urls:
                            additional_id = extract_id(additional_url)
                            rec_dict[additional_id] = additional_url
                    print('JUNK: ', file_name)
                    os.remove(file_full)

    rec_list_ids = list(set(rec_dict.keys()) - set(html_list.keys()))
    rec_list = [rec_dict[rec_id] for rec_id in rec_list_ids]

    export_html_list(sorted(rec_list), REC_URLS)
    print('REC:', len(rec_list_ids))

    export_autoweb_bat(rec_list, REC_BAT)

    print('HTML DB: ', len(html_list))
    return html_list


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
            title_id = extract_id(title_url)
            title_id_url[title_id] = title_url

    cursor.close()
    connection.close()

    return title_id_url


def check_index():
    title_names_list = []

    connection = sqlite3.connect(INDEX_DB)
    cursor = connection.cursor()

    select_sql = '''
    SELECT name FROM titles 
    WHERE shot_time in 
    (SELECT MAX(shot_time) FROM titles)
    '''
    cursor.execute(select_sql)

    for line in cursor.fetchall():
        name = line[0]
        if name.endswith('_'):
            #othersite
            pass
        elif name.startswith('_'):
            #ongoing
            pass
        else:
            title_names_list.append(name)

    cursor.close()
    connection.close()

    return title_names_list


def index_not_html():
    # rescan_dir()

    html = check_html2()
    index_titles = check_index()
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
    html = check_html2()
    index_titles = check_index()
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

    export_autoweb_bat(links_index_not_done, 'INDEX_NOT_DONE.bat')


if __name__ == '__main__':

    rescan_dir()

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

