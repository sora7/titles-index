import os
import sqlite3
import datetime

import re
import shutil

DB_PATH = '../data/titles.db'
TITLES_LIST = '../data/titles_list_%s.txt'

INDEX_DB_TABLE = 'titles'

NAME_TERMINATORS = (
    ' субтитры ',
    ' » Смотреть',
)

DIR_TYPE_UC = 'uc'
DIR_TYPE_FF = 'ff'


class Indexator():

    def __init__(self):
        pass

    def scan_dir(self, test_dir):
        titles = []

        title = dict()
        title['eps'] = []
        for file_name in os.listdir(test_dir):
            file_full = os.path.join(test_dir, file_name)
            if os.path.isdir(file_full):
                titles.extend(self.scan_dir(file_full))
            elif file_name.endswith('mp4'):
                title['dir'] = test_dir
                title['name'] = os.path.basename(test_dir)
                title['eps'].append(file_name)

        if len(title['eps']) > 0:
            titles.append(title)
        return titles


    def write_db(self, tl):
        connection = sqlite3.connect(DB_PATH)
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

    def read_db(self, skip_ong=True):
        title_names_list = []

        connection = sqlite3.connect(DB_PATH)
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
                if not skip_ong:
                    title_names_list.append(name)
            elif name.startswith('_'):
                #ongoing
                if not skip_ong:
                    title_names_list.append(name)
            else:
                title_names_list.append(name)

        cursor.close()
        connection.close()

        return title_names_list

    def rescan_dir(self, titles_path=r'h:/.titles'):
        tl = self.scan_dir(titles_path)
        self.write_db(tl)


    def extract_abc_list(self):
        tl_list = self.read_db(skip_ong=False)

        titles = {}
        i = 0
        for name in tl_list:
            first_char = name[0]
            i += 1
            try:
                titles[first_char].append(name)
            except KeyError:
                titles[first_char] = list()
                titles[first_char].append(name)

        txt = []
        for c in sorted(titles.keys()):
            for name in sorted(titles[c]):
                print(name)
                txt.append(name)
            print()
            txt.append('')
            print()
            txt.append('')
        print('TOTAL: ', i)
        txt.append('TOTAL: %s' % i)
        dt = datetime.datetime.now().strftime('%Y-%m-%d %H_%M_%S')
        txt.append('SCAN TIME: %s' % dt)

        with open(TITLES_LIST % dt, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(txt))


class Renamer():
    __titles_dir = None
    __test = None

    def __init__(self, titles_dir):
        self.__titles_dir = titles_dir
        self.__test = True

    @staticmethod
    def name_match(filename, name_terminator):
        if len(name_terminator) > 0:
            return filename.endswith('.mp4') and name_terminator in filename
        else:
            return filename.endswith('.mp4')

    @staticmethod
    def check_name_terminator(filename):
        for term in NAME_TERMINATORS:
            if term in filename:
                return term
        return ''

    @staticmethod
    def extract_name(name_str):
        name = name_str.split(' субтитры ')[0]
        # name = re.findall(r'(.{1,})[ ]субтитры.*', name_str, re.DOTALL)[0]
        num1 = re.findall(r'[(]([0-9]{1,2})[)]', name_str, re.DOTALL)
        if len(num1) > 0:
            num = num1[0]
        if len(num1) == 0:
            num2 = re.findall(r'[_]([0-9]{1,2})[.]', name_str, re.DOTALL)
            if len(num2) > 0:
                num = num2[0]
            else:
                num = '0'

        return name, int(num) + 1

    def process_uc(self, titles_path, test=True):
        pass











