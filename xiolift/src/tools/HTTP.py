import json

import requests

def do_http_post_txt(url, js):
    payload_json = json.dumps(js, ensure_ascii=False)
    r = requests.post(url=url, data=payload_json.encode('utf-8'))

    return r.text

def do_http_post(url, js):
    payload_json = json.dumps(js, ensure_ascii=False)
    r = requests.post(url=url, data=payload_json.encode('utf-8'))
    return json.loads(r.text)

def do_http_get(url, param):
    r = requests.get(url=url, params=param)
    return json.loads(r.text)

def do_http_put(url, js):
    payload_json = json.dumps(js, ensure_ascii=False)
    r = requests.put(url=url, data=payload_json.encode('utf-8'))
    return json.loads(r.text)

def do_http_delete(url, js):
    payload_json = json.dumps(js, ensure_ascii=False)
    r = requests.delete(url=url, data=payload_json.encode('utf-8'))
    return json.loads(r.text)

def do_https_post(url, js, headers):

    r = requests.post(url, headers=headers, json=js, verify=False)

    a = json.loads(r.text)

    print(a)

    return a
