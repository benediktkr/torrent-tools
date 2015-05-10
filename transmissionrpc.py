#!/usr/bin/env python2.7

import logging
import requests
import json
from requests.auth import HTTPBasicAuth
import time
import guessit

DAYS=3
URL="http://mathom:9091/transmission/rpc"
username="transmission"
password="transmission"
logformat = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(filename="rpc.log", level=logging.INFO, format=logformat)
logging.getLogger().addHandler(logging.StreamHandler())

class RPCError(Exception):
    pass

class TransmRequest(object):
    def __init__(self, method, tag=None, **kwargs):
        self.method = method
        d = dict(**kwargs)
        self.arguments = {key.replace("_", "-"): d[key] for key in d}
        self.tag = tag

    def json(self):
        return json.dumps(self.__dict__)

class TransmResponse(object):
    def __init__(self, result, arguments = {}, tag = None):
        self.result = result
        self.arguments = arguments
        self.tag = tag

    @classmethod
    def from_json(cls, json):
        return cls(json['result'], arguments = json.get("arguments"), tag=json.get('tag'))

    def __getitem__(self, index):
        return self.arguments[index]
    
class TransmissionRPC(object):
    headers = {"X-Transmission-Session-Id": ""}
    auth = HTTPBasicAuth(username, password)
    
    def execute(self, request):
        r = requests.post(URL, data=request.json(), auth=self.auth, headers=self.headers)
        if r.status_code == 409:
            self.headers["X-Transmission-Session-Id"] = r.headers["X-Transmission-Session-Id"]
            r = requests.post(URL, data=request.json(), auth=self.auth, headers=self.headers)
        return r

    def rpc(self, method, **arguments):
        req = TransmRequest(method, **arguments)
        res = self.execute(req)
        resp = TransmResponse.from_json(res.json())
        
        if not resp.result == "success":
            raise RPCError(resp.result)

        return resp
        
def is_episode(torrent):
    return guessit.guess_file_info(torrent["name"]).get("type").startswith("episode")

def is_old(torrent):
    return torrent["isFinished"] and time.time() - DAYS*86400 > torrent["doneDate"]

def remove_old(criteria):
    rpc = TransmissionRPC()
    torrentlist = rpc.rpc("torrent-get", fields = ['name', 'id', 'doneDate', 'isFinished'])

    fltr = filter(criteria, torrentlist["torrents"])
    if len(fltr) == 0: return
    
    ids, names = [a["id"] for a in fltr], [a["name"] for a in fltr]
    logging.info("Removing: " + ", ".join(names))

    rpc.rpc("torrent-remove", ids=ids, delete_local_data = True)

if __name__ == "__main__":
    import sys
    if "--all" in sys.argv:
        remove_old(is_old)
    else:
        remove_old(lambda t: is_old(t) and is_episode(t))
        
        
