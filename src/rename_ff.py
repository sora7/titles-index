import shutil
import os


from rename_uc import is_badchars, clean_badchars

TITLES_DIRS = (
        '~/Downloads/TITLES',
        'f:/TL',
    )


def process_dir(titles_dir, test=False):
    for item in os.listdir(titles_dir):
        item_fullpath = os.path.join(titles_dir, item)
        if os.path.isdir(item_fullpath):
            title_name = clean_badchars(item.split(' [')[0])
            title_name_full = os.path.join(titles_dir, title_name)
            if test:
                title_name_full = item_fullpath
                print('TEST MOVE: %s => %s' % (item_fullpath, title_name_full))
            else:
                shutil.move(item_fullpath, title_name_full)

            i = 1
            for title_item in sorted(os.listdir(title_name_full)):
                print(title_item)
                title_item_filename, title_item_ext = os.path.splitext(title_item)
                title_item_new = '{}_{:02d}{}'.format(title_name, i, title_item_ext)
                print(title_item_new)
                title_item_fullpath = os.path.join(title_name_full, title_item)
                title_item_new_fullpath = os.path.join(title_name_full, title_item_new)
                # print(title_item_fullpath, title_item_new_fullpath)
                if test:
                    print('TEST MOVE: %s => %s' % (title_item_fullpath, title_item_new_fullpath))
                else:
                    shutil.move(title_item_fullpath, title_item_new_fullpath)
                i += 1


if __name__ == '__main__':
    for t_dir in TITLES_DIRS:
        process_dir(t_dir, test=False)
