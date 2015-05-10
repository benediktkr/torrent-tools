#!/usr/bin/env python2.7

import sys
import os
import re
import shutil
import guessit 
import logging

logformat = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(filename="/tmp/torrentools-sorter.log", level=logging.INFO, format=logformat)
logging.getLogger().addHandler(logging.StreamHandler())

shortwords = ["in", "of", "at", "the", "is"]

tvroot = '/srv/media/newvideo/tv/'
transmissionroot = '/srv/media/watching'

# -- Helpers
def format_show_name(showname):
    name = showname.strip().split(" ")
    nametail = [b if b in shortwords else b.capitalize()
                for b in  [a.lower().strip() for a in name[1:]]]
    # First letter should always be capitalized
    return name[0].capitalize() + " " + " ".join(nametail)

# -- Modes
def walk_and_sort(path, move):
    for directory in os.walk(path):
        for file in directory[2]:
            try:
                sort_file(os.path.join(directory[0], file), move=move)
            except ValueError as ex:
                logging.debug(str(ex))

def transmission_complete(torrent_name):
    path = os.path.join(transmissionroot, torrent_name)
    if os.path.isdir(path):
        for file in os.dir(path):
            sort_file(os.path.join(path, file), move=False)
        #videofile = get_largest_file(path)
    else:
        sort_file(path, move=False)

# -- Sorting
def sort_file(filepath, move):
    filename = os.path.basename(filepath)
    guess = guessit.guess_file_info(filename)
                                    
    if not guess.get("type", "") in ["episode", "episodesubtitle"]: return 
    if not guess.get("mimetype", "").startswith("video"): return

    season = str(guess["season"]).zfill(2)
    name = format_show_name(guess["series"]).strip()
    dst_path = os.path.join(tvroot, name, "Season " + season)

    try:
        os.makedirs(dst_path)
    except OSError as ex:
        if ex.errno == 17: pass
        else: raise

    if move:
        logging.info("mv: {0} -> {1}".format(filepath, dst_path))
        shutil.move(filepath, dst_path)
    else:
        # short-circuit if file is found
        if filename in os.listdir(dst_path):
            raise ValueError("File exists (not overwriting): " + filename)
        logging.info("cp: {0} -> {1}".format(filepath, dst_path))
        shutil.copy2(filepath, dst_path)

def main():
    if "--walk" in sys.argv:
        walk_and_sort(transmissionroot, "--move" in sys.argv)
    elif "--walk-path" in sys.argv:
        path = sys.argv[2]
        walk_and_sort(transmissionroot, "--move" in sys.argv)
    else:
        filename = os.environ["TR_TORRENT_NAME"]
        transmission_complete(filename)
        
if __name__ == "__main__":
    main()


