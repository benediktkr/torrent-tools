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

# -- Helpers

# -- Modes

def transmission_complete(torrent_name):
    path = os.path.join(transmissionroot, torrent_name)
    if os.path.isdir(path):
        for file in os.dir(path):
            sort_file(os.path.join(path, file), move=False)
        #videofile = get_largest_file(path)
    else:
        sort_file(path, move=False)

# -- Sorting

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


