import os
import shutil
from pprint import pprint

TITLES_PATH = r'~\Downloads\TITLES_FF'
TRASH_PATH = os.path.join(TITLES_PATH, 'zzz_TRASH')

test = False

# browser:      palemoon 33.4.0.1
# dta version:  3.0.7
# dta params:
# mask:         *num*=*text*_*name*.*ext*
# select:       Videos
# quick filter: posts


# browser:      firefox 133.0
# dta version:  3.0.7
# dta params:
# mask:         *num*=*flattext*_*name*.*ext*
# select:       Videos
# quick filter: posts


TITLE_PREFIX = 'Постер аниме '
TITLE_SUFFIX = ' - '

dls = {}
titles = {}

for item in os.listdir(TITLES_PATH):
    item_fullpath = os.path.join(TITLES_PATH, item)
    if os.path.isfile(item_fullpath):
        dl_id, dl_text = item.split('=') 

        if item.endswith('jpg'):
            title_name = dl_text.split(TITLE_SUFFIX)[0]
            if title_name.startswith(TITLE_PREFIX):
                title_name = title_name.replace(TITLE_PREFIX, '')
                
            try:
                dls[dl_id]['name'] = title_name
            except KeyError:
                dls[dl_id] = {}
                dls[dl_id]['name'] = title_name

            if not os.path.exists(TRASH_PATH):
               os.mkdir(TRASH_PATH)
            item_trash_path = os.path.join(TRASH_PATH, item)
            if not test:
               shutil.move(item_fullpath, item_trash_path)
            else:
               print('TEST MOVE TRASH')
            

        if item.endswith('mp4'):
            title_file = item
            try:
                dls[dl_id]['file'] = title_file
            except KeyError:
                dls[dl_id] = {}
                dls[dl_id]['file'] = title_file   

for dl_id in dls.keys():
    title_name = dls[dl_id]['name']
    title_file = dls[dl_id]['file']

    try:
        titles[title_name].append(title_file)
    except KeyError:
        titles[title_name] = []
        titles[title_name].append(title_file) 


for title_name in titles.keys():
    title_path = os.path.join(TITLES_PATH, title_name)
    if not test:
        os.mkdir(title_path)
    else:
        print('MKDIR ', title_path)
    
    i = 0
    for title_file in sorted(titles[title_name]):
        i += 1
        title_file_oldpath = os.path.join(TITLES_PATH, title_file)
        #title_file_newpath = os.path.join(title_path, '%s_%s.mp4'%(title_name, str(i)))
        title_file_newpath = os.path.join(title_path, '{}_{:02d}.mp4'.format(title_name, i))

        if not test:
            shutil.move(title_file_oldpath, title_file_newpath)
        else:
            print('MOVE ', title_file_oldpath, title_file_newpath)
        


















        
    

