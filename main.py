import requests
import time 
import random

COOKIE = ""
xsrftoken = ""

while True:
    #HH.RU ПОЗОР
    rq = requests.post("https://voronezh.hh.ru/shards/resume/batch_update",
                    headers={"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36","Cookie":COOKIE,"x-hhtmfrom":"","x-hhtmsource":"main","x-requested-with":"XMLHttpRequest","x-xsrftoken":xsrftoken})
    print(rq.status_code, rq.text)
    time.sleep(10800+random.randint(600,1800))
    