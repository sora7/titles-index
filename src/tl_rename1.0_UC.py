import os
import re
import shutil

##DATA SAMPLE:
##Адская девочка (1 сезон) субтитры смотреть аниме онлайн Jigoku Shoujo-Видео(23).mp4
##Адская девочка (1 сезон) субтитры смотреть аниме онлайн Jigoku Shoujo-Видео(24).mp4
##Адская девочка (1 сезон) субтитры смотреть аниме онлайн Jigoku Shoujo-Видео(25).mp4
##Адская девочка (2 сезон) субтитры смотреть аниме онлайн Jigoku Shoujo Futak.mp4
##Адская девочка (2 сезон) субтитры смотреть аниме онлайн Jigoku Shoujo Futak(1).mp4


def extract_name(name_str):
    name = name_str.split(' субтитры ')[0]
    #name = re.findall(r'(.{1,})[ ]субтитры.*', name_str, re.DOTALL)[0]
    num1 = re.findall(r'[(]([0-9]{1,2})[)]', name_str, re.DOTALL)
    if len(num1) > 0:
        num = num1[0]
    if len(num1) == 0:
        num2 = re.findall(r'[_]([0-9]{1,2})[.]', name_str, re.DOTALL)
        if len(num2) > 0:
            num = num2[0]
        else:
            num = '0'
        
    return name, int(num)+1


def name_match(filename):
    return filename.endswith('.mp4') and ' субтитры ' in filename


def process_dir(dirpath, test=True):
    print('FILES: {}'.format(len(os.listdir(dirpath))))

    for item in [f for f in os.listdir(dirpath) if name_match(f)]:
        name, num = extract_name(item)
        print('ITEM:', item)
        print('NAME:', name)
        print('NUM:', num)

        newpath = os.path.join(dirpath, name)

        if not os.path.exists(newpath):
            if not test:
                print('MKDIR: ', newpath)
                os.mkdir(newpath)
            else:
                print('TEST mkdir: {}'.format(newpath))
        else:
            print('MKDIR ERROR')

        newname = '{}_{:02d}.mp4'.format(name, num)

        print('NEWPATH, NEWNAME: ', newpath, newname)
        old_fullpath = os.path.join(dirpath,item)
        new_fullpath = os.path.join(newpath, newname)
        if not test:
            if os.path.exists(new_fullpath) and os.path.isfile(new_fullpath):
                raise Exception('RENAME ERROR')
            print(old_fullpath, new_fullpath)
            shutil.move(old_fullpath, new_fullpath)
        else:
            print('TEST move: {} > {}'.format(item, newname))


titles_dirpath = 'h:/TITLES_UC'
#titles_dirpath = 'e:/titles'
test1 = False
process_dir(titles_dirpath, test1)