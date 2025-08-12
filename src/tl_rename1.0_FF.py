import shutil
import os


def extract_name(name_str):
    name = name_str.split(' [')[0]
    return name


def name_match(filename):
    return filename.endswith('.mp4')


def process_dir(dirpath, test=True):
    for item in os.listdir(dirpath):
        item_fullpath = os.path.join(dirpath, item)
        print(item_fullpath)
        if os.path.isdir(item_fullpath):
            title_name = extract_name(item)
            print(title_name)

            title_name_full = os.path.join(dirpath, title_name)
            shutil.move(item_fullpath, title_name_full)

            i = 1
            for title_item in sorted(os.listdir(title_name_full)):
                print(title_item)
                title_item_filename, title_item_ext = os.path.splitext(title_item)
                title_item_new = '{}_{:02d}{}'.format(title_name, i, title_item_ext)
                print(title_item_new)

                title_item_fullpath = os.path.join(title_name_full, title_item)
                title_item_new_fullpath = os.path.join(title_name_full, title_item_new)
                if test:
                    print('TEST: ', title_item_fullpath, title_item_new_fullpath)
                else:
                    shutil.move(title_item_fullpath, title_item_new_fullpath)
                i += 1


titles_path = r'C:\Users\Evoo\Downloads\TITLES_FF'
process_dir(titles_path, False)