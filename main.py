from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random
import http.client, urllib
import json

today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']
birthday2 = os.environ['BIRTHDAY2']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]


def get_weather():
  url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
  res = requests.get(url).json()
  weather = res['data']['list'][0]
  return weather['weather'], math.floor(weather['temp'])

def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_birthday():
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_birthday2():
  next = datetime.strptime(str(date.today().year) + "-" + birthday2, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def get_tips():
  conn = http.client.HTTPSConnection('apis.tianapi.com')  #接口域名
  params = urllib.parse.urlencode({'key':'53f026175030f52468a2a86c923b094e','city':city,'type':'1'})
  headers = {'Content-type':'application/x-www-form-urlencoded'}
  conn.request('POST','/tianqi/index',params,headers)
  tianapi = conn.getresponse()
  result = tianapi.read()
  data = result.decode('utf-8')
  dict_data = json.loads(data)
  pop = dict_data['result']['quality']
  tips = dict_data['result']['tips']
  return tips

def get_ciba():
    conn = http.client.HTTPSConnection('apis.tianapi.com')  #接口域名
    params = urllib.parse.urlencode({'key':'53f026175030f52468a2a86c923b094e'})
    headers = {'Content-type':'application/x-www-form-urlencoded'}
    conn.request('POST','/everyday/index',params,headers)
    tianapi = conn.getresponse()
    result = tianapi.read()
    data = result.decode('utf-8')
    dict_data = json.loads(data)
    ci_content = dict_data['result']['content']
    ci_note = dict_data['result']['note']
    return (ci_content, ci_note)
  
def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
wea, temperature = get_weather()
tips = get_tips()
note_en,note_ch = get_ciba()
data = {"note_ch":{"value":note_ch},"note_en":{"value":note_en},"city":{"value":city},"weather":{"value":wea},"tips":{"value":tips},"temperature":{"value":temperature},"love_days":{"value":get_count()},"birthday_left":{"value":get_birthday()},"birthday_left2":{"value":get_birthday2()},"words":{"value":get_words(), "color":get_random_color()}}
res = wm.send_template(user_id, template_id, data)
print(res)
