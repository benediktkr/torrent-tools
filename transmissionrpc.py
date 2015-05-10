#!/usr/bin/env python2.7

import requests
import json
from requests.auth import HTTPBasicAuth


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
    
    def __init__(self, url, username, password):
        self.URL = url
        self.auth = HTTPBasicAuth(username, password)
    
    def execute(self, request):
        r = requests.post(self.URL, data=request.json(), auth=self.auth, headers=self.headers)
        if r.status_code == 409:
            self.headers["X-Transmission-Session-Id"] = r.headers["X-Transmission-Session-Id"]
            r = requests.post(self.URL, data=request.json(), auth=self.auth, headers=self.headers)
        return r

    def rpc(self, method, **arguments):
        req = TransmRequest(method, **arguments)
        res = self.execute(req)
        resp = TransmResponse.from_json(res.json())
        
        if not resp.result == "success":
            raise RPCError(resp.result)

        return resp
        

