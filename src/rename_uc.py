import os
import re
import shutil

# UC version 13.6.2.1316

NAME_TERMINATORS = (
    ' субтитры ',
    ' » Смотреть',
)

TITLES_DIRS = (
        '~/Downloads/TITLES',
        'f:/TL',
    )

BADCHARS = {
    ':': '',
    '?': '',
    '?': '',
    "'": '',
    'ː': '',
    '...': '',
    '/': ' ',
}


def is_badchars(input_string):
    for char in BADCHARS.keys():
        if char in input_string:
            return True
    return False


def clean_badchars(input_string):
    out_string = input_string
    for string_sample in BADCHARS.keys():
        out_string = out_string.replace(string_sample, BADCHARS[string_sample])

    return out_string


def extract_name(name_str, name_terminator):
    num_str = re.findall(r'[(]([0-9]{1,2})[)]', name_str, re.DOTALL)

    episode_number = 0
    if len(num_str) > 0:
        episode_number = int(num_str[0])

    if len(num_str) == 0:
        episode_number = 0

    if len(name_terminator) > 0:
        title_name_ = re.findall(r'(.{1,})%s.*'%name_terminator, name_str, re.DOTALL)[0]
        #title_name_ = name_str.split(name_terminator)[0]
        title_name = clean_badchars(title_name_)
        # name = re.findall(r'(.{1,})[ ]субтитры.*', name_str, re.DOTALL)[0]
    else:
        # name_str_ = re.findall(r'(.{1,})[(][0-9]{1,2}[)]', name_str, re.DOTALL)
        # title_name_ = name_str
        title_name = ''
        if len(num_str) > 0:
            title_name = re.findall(r'(.{1,})[(][0-9]{1,2}[)][.]mp4', name_str, re.DOTALL)[0]

        if len(num_str) == 0:
            title_name = re.findall(r'(.{1,})[.]mp4', name_str, re.DOTALL)[0]

    return title_name, episode_number + 1


def name_match(filename, name_terminator):
    if len(name_terminator) > 0:
        return filename.endswith('.mp4') and name_terminator in filename
    else:
        return filename.endswith('.mp4')


def check_name_terminator(filename):
    for term in NAME_TERMINATORS:
        if term in filename:
            return term
    return ''


def process_dir(path, test=False):
    file_list = os.listdir(path)
    print('FILES: {}'.format(len(file_list)))

    for item in file_list:
        name_term = check_name_terminator(item)
        print('TERM: ==%s=='%name_term)

        if name_match(item, name_term):
            name, num = extract_name(item, name_term)
            print('ITEM:', item)
            print('NAME:', name)
            print('NUM:', num)

            newpath = os.path.join(path, name)

            if not os.path.exists(newpath) and not os.path.isdir(newpath):
                if not test:
                    print('MKDIR: ', newpath)
                    os.mkdir(newpath)
                else:
                    print('test mkdir: {}'.format(newpath))

            newname = '{}_{:02d}.mp4'.format(name, num)
            print('NEWPATH, NEWNAME: ', newpath, newname)
            if not test:
                print(os.path.join(path, item), os.path.join(newpath, newname))
                shutil.move(os.path.join(path, item), os.path.join(newpath, newname))
            else:
                print('test move: {} > {}'.format(item, newname))


if __name__ == '__main__':
    # path = '/storage/emulated/0/Download/UCDownloads/video'
    # path = '/mnt/media_rw/D4B8-A01A/t'
    # path = '/storage/emulated/0/Documents/Pydroid3/.kivy/logs'
    # path1 = 'd:/.titles/_/35/'
    for t_dir in TITLES_DIRS:
        process_dir(t_dir, test=False)
    # process_dir(path1, test=False)
