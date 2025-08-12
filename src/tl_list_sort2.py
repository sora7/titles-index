import sqlite3
import datetime

DB_PATH = r'..\data\titles.db'

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

select_sql = '''
SELECT name FROM titles 
WHERE shot_time in 
(SELECT MAX(shot_time) FROM titles)
'''
cursor.execute(select_sql)

titles = {}
i = 0
for line in cursor.fetchall():
    if len(line) > 0:
        name = line[0]
        first_char = name[0]
        i += 1
        try:
            titles[first_char].append(name)
        except KeyError:
            titles[first_char] = list()
            titles[first_char].append(name)

cursor.close()
connection.close()  

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
txt.append('TOTAL: %s'%i)
dt = datetime.datetime.now().strftime('%Y-%m-%d %H_%M_%S')
txt.append('SCAN TIME: %s'%dt)


with open('titles_list_%s.txt'%dt, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(txt))

 
