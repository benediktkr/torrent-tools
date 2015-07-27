#!/usr/bin/env python2.7

import os
import shutil
import logging
import time
import guessit
from transmissionrpc import TransmissionRPC

DAYS=3
URL="http://mathom:9091/transmission/rpc"
username="transmission"
password="transmission"
tvroot = '/srv/media/newvideo/tv/'
transmissionroot = '/srv/media/watching'

shortwords = ["in", "of", "at", "the", "is"]

#-- Logger --
logformat = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(filename="/var/lib/transmission-daemon/torrentools.log", level=logging.INFO, format=logformat)
logging.getLogger().addHandler(logging.StreamHandler())

def format_show_name(showname):
    name = showname.strip().split(" ")
    nametail = [b if b in shortwords else b.capitalize()
                for b in  [a.lower().strip() for a in name[1:]]]
    # First letter should always be capitalized
    return name[0].capitalize() + " " + " ".join(nametail)
    
def is_episode(torrent):
    return guessit.guess_file_info(torrent["name"]).get("type").startswith("episode")

def is_old(torrent):
    return torrent["isFinished"] and time.time() - DAYS*86400 > torrent["doneDate"]

def walk_and_sort(path, move):
    for directory in os.walk(path):
        for file in directory[2]:
            try:
                sort_file(os.path.join(directory[0], file), move=move)
            except ValueError as ex:
                logging.debug(str(ex))

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

def remove_old():
    rpc = TransmissionRPC(URL, username, password)
    torrentlist = rpc.rpc("torrent-get", fields = ['name', 'id', 'doneDate', 'isFinished'])

    old_torrents = filter(is_old, torrentlist["torrents"])

    logging.debug("Old torrents: " + repr([a["name"] for a in old_torrents]))
    
    if len(old_torrents) == 0: return

    for torrent in old_torrents:
        isep = is_episode(torrent)
        if isep:
            logging.info("Removing (rm): " + torrent["name"])
        else:
            logging.info("Removing: " + torrent["name"])

        rpc.rpc("torrent-remove", ids=[torrent["id"]], delete_local_data = isep)

if __name__ == "__main__":
    import sys
    logging.debug("Starting " + " ".join(sys.argv))

    ## --remove-torrents
    if "--remove-torrents" in sys.argv:
        remove_old()

    ## walk
    if "--walk" in sys.argv:
        walk_and_sort(transmissionroot, "--move" in sys.argv)
    elif "--walk-path" in sys.argv:
        path = sys.argv[2]
        walk_and_sort(transmissionroot, "--move" in sys.argv)

        
