# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from index import Indexator
from parser import AJ_Parser
from browser import select_ids

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('hello')
    db = Indexator()
    db_lst = db.read_db()
    p = AJ_Parser()

    select_ids('ready')


    # html_db = p.check_html()
    # print(html_db)

    # print(db_lst[0:100])
    # print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
