import os
import pathlib

TEST = 0

NAME_SEP = ' субтитры '

def sort_fn(s):
    t = s.stem.split('_')
    if len(t) > 1:
        return int(t[1])
    else:
        return 0

def process_dir(titles_dir):
    path = pathlib.Path(titles_dir)
    for item in path.rglob('* субтитры *.mp4'):
        title_name = item.stem.split(NAME_SEP)[0]
        title_dir = path / title_name
##        if not bool(TEST):
        title_dir.mkdir(exist_ok=True)
        pathlib.Path.rename(item, title_dir / item.name)

    for title_dir in path.rglob('*'):
        if title_dir.is_dir:
            ep = 0
            for item in sorted(title_dir.rglob('*'), key=sort_fn):
                ep += 1
                title_name = title_dir.name
                ext = item.suffix
                item_newname = '{}_{:02}{}'.format(title_name, ep, ext)
                print('{} > {}'.format(item.name, item_newname))
                if not bool(TEST):
                    pathlib.Path.rename(item, title_dir / item_newname)
                

DM_PATH = r'e:\titles_dm'
process_dir(DM_PATH)
