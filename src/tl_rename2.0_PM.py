import os
import shutil
from pprint import pprint

TITLES_PATH = r'~\Downloads\TITLES_PM'
TRASH_PATH = r'~\Downloads\TITLES\zzz_TRASH'

# browser:      palemoon 33.4.0.1
# dta version:  3.0.7
# dta params:
# mask:         *num*=*text*_*name*.*ext*
# select:       Videos
# quick filter: posts



# browser:      firefox 133.0
# dta version:  3.0.7
# dta params:
# mask:         *num*=*flattexttext*_*name*.*ext*


dls = {}
titles = {}

for item in os.listdir(TITLES_PATH):
    item_fullpath = os.path.join(TITLES_PATH, item)
    if os.path.isfile(item_fullpath):
        dl_id, dl_text = item.split('=') 

        if item.endswith('jpg'):
            title_name = dl_text.split('   ')[0]
            try:
                dls[dl_id]['name'] = title_name
            except KeyError:
                dls[dl_id] = {}
                dls[dl_id]['name'] = title_name

            if not os.path.exists(TRASH_PATH):
               os.mkdir(TRASH_PATH)
            item_trash_path = os.path.join(TRASH_PATH, item)
            shutil.move(item_fullpath, item_trash_path)
            

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
    os.mkdir(title_path)
    
    i = 0
    for title_file in sorted(titles[title_name]):
        i += 1
        title_file_oldpath = os.path.join(TITLES_PATH, title_file)
        title_file_newpath = os.path.join(title_path, '%s_%s.mp4'%(title_name, str(i)))
        shutil.move(title_file_oldpath, title_file_newpath)
        


















        
    

