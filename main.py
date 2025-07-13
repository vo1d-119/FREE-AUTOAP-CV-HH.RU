import aiohttp
import asyncio
import yaml
import random

from yarl import URL

async def main():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    while True:
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30),
                                            headers={"user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.4 Mobile/15E148 Safari/604.1"}) as s:
                rq1 = await s.get("https://voronezh.hh.ru/?role=applicant",
                                  headers={"referer": "https://voronezh.hh.ru/account/login?role=applicant&backurl=%2F&hhtmFrom=main"})
                if rq1.status != 200 or '_xsrf' not in s.cookie_jar.filter_cookies(URL("https://voronezh.hh.ru")):
                    print(f'{rq1.status} Неудачная загрузка: {rq1.text}')
                    continue
                csrf_token = (s.cookie_jar.filter_cookies(URL("https://voronezh.hh.ru"))).get('_xsrf').value
                if csrf_token:
                    print(f'{rq1.status} Нашёл csrf: {csrf_token[:15]}{'*' * (len(csrf_token) - 15)}')

                rq2 = await s.post("https://voronezh.hh.ru/account/login?backurl=%2F&role=applicant",
                                   data={"username": f"{config['app']['login']}", "password": f"{config['app']['password']}", "accountType": "APPLICANT", "failUrl": "/account/login?backurl=%2F&role=applicant", "remember": "true", "captchaText": ""},
                                   headers={"x-xsrftoken": f"{csrf_token}", "referer": "https://voronezh.hh.ru/account/login?role=applicant&backurl=%2F&hhtmFrom=main", "x-hhtmsource": "account_login", "x-hhtmfrom": "main", "x-gib-gsscgib-w-hh": "", "x-requested-with": "XMLHttpRequest"})
                if rq2.status == 200:
                    print(f'{rq2.status} Успешная авторизация')
                else:
                    print(f'{rq2.status} Неудачная авторизация')
                    continue

                rq3 = await s.post("https://voronezh.hh.ru/shards/resume/batch_update",
                                   headers={"x-hhtmfrom": "", "x-hhtmsource": "main", "x-requested-with": "XMLHttpRequest", "x-xsrftoken": csrf_token})
                sleep_up = config['app']['delay'] + random.randint(config['app']['random_min_delay'], config['app']['random_max_delay'])
                print(f'{rq3.status} Успешно поднял резюме\nСледующее поднятие через {sleep_up} секунд')
                await asyncio.sleep(sleep_up)

        except Exception as e:
            print(f"Произошла ошибка: {e}")

asyncio.run(main())
