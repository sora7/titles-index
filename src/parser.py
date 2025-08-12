import re
from xml.etree import ElementTree as ET
import random
from pathlib import Path
import os
import shutil
import time
import sqlite3

DB_PATH = '../data/titles.db'
DB_TABLE = 'html'

from rename_uc import clean_badchars

DL_DIR = r'~/Downloads'
HTML_DIR = r'../data/html'

REC_URLS = '../data/recurls.html'
REC_BAT = '../data/REC_AUTOWEB.bat'


def move_autosave():
    src_dir = DL_DIR
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



class ListParser(object):

    def __init__(self):
        pass

    @staticmethod
    def extract(regex_list, text, dotall=False):
        result = []
        for regex in regex_list:
            if dotall:
                result.extend(re.findall(re.compile(regex, re.DOTALL), text))
            else:
                result.extend(re.findall(re.compile(regex), text))
        return result

    @staticmethod
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

    @staticmethod
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
            batch_lines.append('TIMEOUT %s' % str(random.choice([i for i in range(2, 5)])))

        with open(filename, 'w') as fh:
            fh.write('\n'.join(batch_lines))


class AJ_Parser(ListParser):
    html_list = {}
    rec_list = {}
    add_list = {}

    def __init__(self):
        super().__init__()

    def extract_id(self, url_text):
        re_title_id = ('.*?[/]([0-9]{1,})[-].*?',)
        title_id_ = self.extract(re_title_id, url_text)[0]
        return title_id_

    # re_name_jp = r'<h2 class="romanji">(.*?)</h2>'

    def extract_url(self, html_text):
        re_url_lst = (
            r'<meta property="og:url" content="(.*?)" />',
            r'<a id="dle-comm-link" href="(.*?)#comment">'
        )
        return self.extract(re_url_lst, html_text)

    def extract_name(self, html_text):
        re_name_ru = (r'<h1 class="h2 ntitle" itemprop="name">(.*?)</h1>',)

        return self.extract(re_name_ru, html_text)

    def extract_rec_urls(self, html_text):
        rec_urls = []

        re_rec_urls = (r'<div class="story_line">.*?<a href="(.*?)" title="',)
        rec_urls.extend(self.extract(re_rec_urls, html_text, dotall=True))

        re_rec_url_block = (r'<!--spoiler_text-->(.*?)<!--spoiler_text_end-->',)
        rec_url_block = self.extract(re_rec_url_block, html_text, dotall=True)

        if len(rec_url_block) > 0:
            re_rec_urls2 = (r'<li><a href="(.*?)">.*?</a></li>',)
            rec_urls.extend(self.extract(re_rec_urls2, rec_url_block[0]))

        return rec_urls

    def extract_links(self, html_text):
        re_link = (r'<h2 class="ntitle"><a href="(https://animejoy.site/.*?/[0-9]{1,5}-.*?.html)">',)
        re_link = (r'<a href="(https://animejoy.site/.*?/[0-9]{1,5}-.*?.html)"',)
        return self.extract(re_link, html_text)

    def add_rec(self, html_text, file):
        rec_urls = self.extract_rec_urls(html_text)
        if len(rec_urls) > 0:
            # print('REC FOUND: ', len(rec_urls))
            for rec_url in rec_urls:
                rec_id = self.extract_id(rec_url)
                self.rec_list[rec_id] = rec_url
        else:
            print('NO REC: ', file.name)

    def add_additional(self, html_text, file):
        additional_urls = self.extract_links(html_text)

        if len(additional_urls) > 0:
            # print('ADD FOUND: ', len(additional_urls))
            for additional_url in additional_urls:
                additional_id = self.extract_id(additional_url)
                self.rec_list[additional_id] = additional_url
        else:
            print('NO ADD: ', file.name)

    def add_title(self, title_url, title_name, file):
        file_ctime = int(os.path.getctime(file.resolve()))
        title_id = self.extract_id(title_url)
        if title_id in self.html_list.keys():
            print('DUBL: ', file.name, title_url)
            base_file, base_ctime = self.html_list[title_id][2:]

            print('BASE:', base_ctime, 'FILE:', file_ctime)

            if base_ctime > file_ctime:
                os.remove(file.resolve())
            else:
                self.html_list[title_id] = (title_url, title_name, file.name, file_ctime)
                file_full2 = os.path.join(HTML_DIR, base_file)
                os.remove(file_full2)
        else:
            self.html_list[title_id] = (title_url, title_name, file.name, file_ctime)

    def process_rec(self):
        rec_list_ids = list(set(self.rec_list.keys()) - set(self.html_list.keys()))
        rec_list = [self.rec_list[rec_id] for rec_id in rec_list_ids]

        print('REC:', len(rec_list_ids))
        self.export_html_list(sorted(rec_list), REC_URLS)
        self.export_autoweb_bat(rec_list, REC_BAT)

    def check_html(self):
        move_autosave()

        html_path = Path(HTML_DIR)
        for file in html_path.rglob('*'):
            if file.is_file():
                if file.suffix == '.htm' or file.suffix == '.html':
                    with file.open(mode="r", encoding="utf-8") as fh:
                        html_text = fh.read()

                    names = self.extract_name(html_text)
                    if len(names) > 0:
                        title_name = clean_badchars(names[0].split(' [')[0])
                        urls = self.extract_url(html_text)
                        if len(urls) > 0:
                            title_url = urls[0]

                            self.add_title(title_url, title_name, file)

                            self.add_rec(html_text, file)
                            self.add_additional(html_text, file)
                        else:
                            print('NO URL: ', file.name)
                    else:
                        #not a title page
                        self.add_additional(html_text, file)

                        print('JUNK: ', file.name)
                        os.remove(file.resolve())

        self.process_rec()

        print('HTML DB: ', len(self.html_list))
        self.write_db()
        return self.html_list


    def write_db(self):
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        for title_id, (title_url, title_name, title_file, title_file_ctime) in list(self.html_list.items()):
            # print(title_id, title_url, title_name, title_file, title_file_ctime)

            sql = ("INSERT "
                   "INTO html (site_id, name, url) "
                   "VALUES ('{}', '{}', '{}')"
                   ).format(title_id, title_name, title_url)
            cursor.execute(sql)
            connection.commit()

        cursor.close()
        connection.close()

    def read_db(self):
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        sql = ("SELECT  site_id, name, url"
               "FROM html"
               )

        for title_id, (title_url, title_name, title_file, title_file_ctime) in list(self.html_list.items()):
            # print(title_id, title_url, title_name, title_file, title_file_ctime)

            sql = ("INSERT "
                   "INTO html (site_id, name, url) "
                   "VALUES ('{}', '{}', '{}')"
                   ).format(title_id, title_name, title_url)
            cursor.execute(sql)
            connection.commit()

        cursor.close()
        connection.close()