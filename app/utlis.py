import time
import hmac
import base64
import os
from datetime import datetime
from app.setting import SECRET_KEY
import requests
import json

# 生成token 入参：用户id
def generate_token(key, expire=86400):
    key += SECRET_KEY
    ts_str = str(time.time() + expire)
    ts_byte = ts_str.encode("utf-8")
    sha1_tshexstr = hmac.new(key.encode("utf-8"), ts_byte, 'sha1').hexdigest()
    token = ts_str + ':' + sha1_tshexstr
    b64_token = base64.urlsafe_b64encode(token.encode("utf-8"))
    return b64_token.decode("utf-8")


# 验证token 入参：用户id 和 token
def certify_token(key, token):
    key += SECRET_KEY
    token_str = base64.urlsafe_b64decode(token).decode('utf-8')
    token_list = token_str.split(':')
    if len(token_list) != 2:
        return False
    ts_str = token_list[0]
    if float(ts_str) < time.time():
        # token expired
        return False
    known_sha1_tsstr = token_list[1]
    sha1 = hmac.new(key.encode("utf-8"), ts_str.encode('utf-8'), 'sha1')
    calc_sha1_tsstr = sha1.hexdigest()
    if calc_sha1_tsstr != known_sha1_tsstr:
        # token certification failed
        return False
        # token certification success
    return True



def getMsg():
    url = 'https://c.m.163.com/ug/api/wuhan/app/data/list-total'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36 Edg/81.0.416.68'
    }
    html = requests.get(url, headers=headers)

    msg = json.loads(html.text)

    contries = msg['data']['areaTree']
    sum = 0
    for contry in contries:
        sum += contry['total']['confirm']
    msg['data']['worldTotal'] = sum

    msg = json.dumps(msg)

    UPLOAD_PATH = os.path.join(os.path.dirname((__file__)), 'CovidMessage/')
    if not os.path.exists(UPLOAD_PATH):
        os.makedirs(UPLOAD_PATH)
    filename = UPLOAD_PATH + datetime.now().strftime('%Y_%m_%d') + '.json'
    with open(filename, 'w', encoding='gbk') as f:
        f.write(msg)