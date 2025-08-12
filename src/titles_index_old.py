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
INDEX_DB = 'titles.db'

FF_DB = r'~\AppData\Roaming\Mozilla\Firefox\Profiles\48hcvyaq.123\places.sqlite'
FF_LIST = {
    'plan': 'AJ_PLAN',
    'ready': 'AJ_READY',
    'done': 'AJ_DONE',
}
HTML_DIR = r'~\Documents\prog\python\PycharmProjects\titles-index\data\html'
NO_URLS = 'nourls.html'
NO_TITLES = 'notitles.html'
REC_URLS = 'recurls.html'


def check_dir(test_dir):
    titles = []
    title = {}
    title['eps'] = []
    for file_name in os.listdir(test_dir):
        file_full = os.path.join(test_dir, file_name)
        if os.path.isdir(file_full):
            titles.extend(check_dir(file_full))
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
        sql = "INSERT INTO titles (name, eps, dir, shot_time) VALUES ('%s', %s, '%s', '%s')" %(title['name'], str(len(title['eps'])), title['dir'], shot_time)
        #print(sql)
        cursor.execute(sql)
        connection.commit()

    cursor.close()
    connection.close()


class AJParser(HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.rec = False
        self.data = []

    def handle_starttag(self, tag, attrs):
        if tag != 'span':
            return
        if self.rec:
            self.rec

        if len(attrs) == 2:
            key, val = attrs
            if key == 'property' and val == 'name':
                print(attrs)
                print("Encountered a start tag:", tag)

    def handle_endtag(self, tag):
        if tag != 'span':
            return

    def handle_data(self, data):
        print("Encountered some data  :", data)


# def clean_chars(input_string):
#     out_string = input_string
#     for string_sample in ('...', ':', '?', "'", 'ː', ):
#         out_string = out_string.replace(string_sample, '')
# 
#     return out_string

def move_autosave():
    src_dir = r'C:\Users\NATI\Downloads'
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


def export_list(lst, filepath):
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


def export_autoweb(rec_list):
    batch_lines = ['@echo off']
    i = 0
    total = len(rec_list)
    for url in rec_list:
        i += 1
        batch_lines.append(r'"c:\Program Files\Mozilla Firefox\firefox.exe" -private-window %s' % url)
        batch_lines.append("echo PROGRESS [{} / {}] ({:.2f} %%)".format(i, total, i / total * 100))
        batch_lines.append('TIMEOUT %s' % str(random.choice([i for i in range(5, 10)])))

    with open('AUTOWEB.bat', 'w') as fh:
        fh.write('\n'.join(batch_lines))


def check_ff_urls(list_type='ready'):
    titles_lst = []

    url_title = check_html()
    no_db_urls = list()

    connection = sqlite3.connect(FF_DB)
    cursor = connection.cursor()

    select_sql = '''
    SELECT moz_places.url FROM moz_bookmarks 
    INNER JOIN moz_places ON moz_bookmarks.fk=moz_places.id
    WHERE moz_bookmarks.parent in 
    (SELECT id FROM moz_bookmarks WHERE title='%s')
    ''' % (FF_LIST[list_type])
    cursor.execute(select_sql)

    for line in cursor.fetchall():
        url, = line
        if 'animejoy' in url:
            try:
                title = url_title[url]
                titles_lst.append(title)
            except KeyError:
                print('NO URL: ', url)
                no_db_urls.append(url)

    cursor.close()
    connection.close()

    export_list(no_db_urls, NO_URLS)

    # with open(NO_URLS, 'w') as fh:
    #     fh.writelines(line + '\n' for line in no_db_urls)

    return titles_lst

def extract_rec___():
    rec = {}
    url_title = check_html()
    urls = url_title.keys()
    for root, subdirs, files in os.walk(HTML_DIR):
        for file in files:
            if file.endswith('.htm') or file.endswith('.html'):
                file_full = os.path.join(root, file)
                with open(file_full, 'r', encoding='utf-8') as fh:
                    html_text = fh.read()

                rec_url = r'<div class="story_line">.*?<a href="(.*?)"[ ]title'
                result = re.findall(re.compile(rec_url, re.DOTALL), html_text)
                if (len(result) > 0):
                    for item in result:
                        if item not in urls:
                            rec[item] = 1
                else:
                    print('NO REC: ', file)

    export_list(sorted(rec.keys()), REC_URLS)
    print('REC:', len(rec.keys()))

    return rec


def extract_id(url_text):
    re_title_id = ('.*?[/]([0-9]{1,})[-].*?',)
    title_id = extract(re_title_id, url_text)[0]
    return title_id


re_name_jp = r'<h2 class="romanji">(.*?)</h2>'

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


def extract(regex_list, text, dotall=False):
    result = []
    for regex in regex_list:
        if dotall:
            result.extend(re.findall(re.compile(regex, re.DOTALL), text))
        else:
            result.extend(re.findall(re.compile(regex), text))
    return result


def check_html2():
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
                            pass
                            print('NO REC: ', file_name)

                        if title_id in html_list.keys():
                            print('DUBL: ', file_name, title_url)
                            base_file, base_ctime = html_list[title_id][2:]
                            print('BASE:', base_ctime)
                            print('FILE:', file_ctime)

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
                    os.remove(file_full)
                    print('JUNK: ', file_name)

    rec_list_ids = list(set(rec_dict.keys()) - set(html_list.keys()))
    print(rec_list_ids)

    rec_list = [rec_dict[rec_id] for rec_id in rec_list_ids]
    # url_list = rec_dict.values()

    export_list(sorted(rec_list), REC_URLS)
    print('REC:', len(rec_list_ids))

    export_autoweb(rec_list)

    print('HTML DB: ', len(html_list))
    return html_list


def check_html():
    html_list = {}
    dubl = {}
    dd = []
    for root, subdirs, files in os.walk(HTML_DIR):
        for file in files:
            if file.endswith('.htm') or file.endswith('.html'):
                file_full = os.path.join(root, file)
                with open(file_full, 'r', encoding='utf-8') as fh:
                    html_text = fh.read()

                # re_name = r'<li property="itemListElement" typeof="ListItem"><span property="name">(.*?)</span>'
                re_name_ru = r'<h1 class="h2 ntitle" itemprop="name">(.*?)</h1>'
                re_name_jp = r'<h2 class="romanji">(.*?)</h2>'

                # print(file)
                result = re.findall(re.compile(re_name_ru), html_text)
                if len(result) > 0:
                    title_name = clean_badchars(result[0].split(' [')[0])
                    # print(name)

                    re_url = r'<meta property="og:url" content="(.*?)" />'
                    result = re.findall(re.compile(re_url), html_text)
                    if len(result) == 0:
                        print(file)
                    url = result[0]

                    if url in html_list.keys():
                        os.remove(os.path.join(root, file))
                        # os.rename(os.path.join(root, file), os.path.join(root, '_' + file))
                        print('DUBL: ', file, url)

                    # if url not in dubl.keys():
                    #     dubl[url] = []
                    #     dubl[url].append(file)
                    # else:
                    #     dubl[url].append(file)

                    html_list[url] = title_name

                else:
                    os.remove(os.path.join(root, file))
                    print('JUNK: ', file)


    # for key in dubl.keys():
    #     if len(dubl[key]) > 1:
    #         print(dubl[key])
    # pprint(dd)

    print('HTML DB: ', len(html_list))
    return html_list

def check_ff(list_type='ready'):
    lst = []

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
        title, url = line
        # if ('Коми' in title):
        #     print('OKKKKKKKKKKKKKKKKKKKKKKK')
        #     print(line)
        if 'animejoy' in url:
            if ' субтитры ' in title:
            # if ' субтитры смотреть ' in title:
                title_clear = title.split(' субтитры ')[0]
                title_clear = clean_badchars(title_clear)
                lst.append(title_clear)

    cursor.close()
    connection.close()

    return lst


def check_ff2(list_type='ready'):
    lst = {}

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
            if ' субтитры ' in title_name_:
                title_id = extract_id(title_url)
                lst[title_id] = title_url

    cursor.close()
    connection.close()

    return lst

def check_index():
    lst = []

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
        lst.append(name)

    cursor.close()
    connection.close()

    return lst


def index_not_html():
    html = check_html2()

    html_titles = [title for url, title, file, ctime in list(html.values())]

    index_titles = check_index()

    not_in_html = set(set(index_titles) - set(html_titles))
    print(list(not_in_html)[:10])
    print(len(not_in_html))
    export_list(sorted(list(not_in_html)), NO_TITLES)


if __name__ == '__main__':

    checkdb = True
    if checkdb:
        tl = check_dir(r'f:/.titles')
        write_db(tl)

    move_autosave()
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

    pprint(sorted(not_in_html))
    print('NOT IN HTML: ', len(not_in_html))

    # tl = check_dir(r'C:\Users\NATI\Downloads\TITLES')


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







