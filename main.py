import aiohttp
import asyncio
import yaml
import random

from aiohttp import FormData
from yarl import URL

async def main():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    with open ('user_agent.txt', 'r') as f:
        user_agents = f.read().splitlines()
    user_agent_random = random.choice(user_agents)
    
    while True:
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30),
                                            headers={"user-agent": user_agent_random}) as s:
                rq1 = await s.get("https://hh.ru/?role=applicant",
                                  headers={"referer": "https://hh.ru/account/login?role=applicant&backurl=%2F&hhtmFrom=main"})
                if rq1.status != 200 or '_xsrf' not in s.cookie_jar.filter_cookies(URL("https://hh.ru")):
                    print(f'{rq1.status} Неудачная загрузка: {rq1.text}')
                    continue
                csrf_token = (s.cookie_jar.filter_cookies(URL("https://hh.ru"))).get('_xsrf').value
                if csrf_token:
                    print(f'{rq1.status} Нашёл csrf: {csrf_token[:15]}{'*' * (len(csrf_token) - 15)}')
                data = FormData()
                data.add_field("username", f"{config['app']['login']}")
                data.add_field("password", f"{config['app']['password']}")
                data.add_field("accountType", "APPLICANT")
                data.add_field("failUrl", "/account/login?backurl=%2F&role=applicant")
                data.add_field("remember", "true")
                data.add_field("captchaText", "")
                rq2 = await s.post("https://hh.ru/account/login?backurl=%2F&role=applicant",
                                   data=data,
                                   headers={"x-xsrftoken": f"{csrf_token}", "referer": "https://hh.ru/account/login?role=applicant&backurl=%2F&hhtmFrom=main", "x-hhtmsource": "account_login", "x-hhtmfrom": "main", "x-requested-with": "XMLHttpRequest"})
                if rq2.status == 200:
                    if not (await rq2.json())["recaptcha"]["isBot"] or not (await rq2.json())["hhcaptcha"]["isBot"]:
                        print(f'{rq2.status} Успешная авторизация {await rq2.json()}')
                    else:
                        print(f'{rq2.status} Неудачная авторизация детект капчи: {await rq2.json()}\nМеняю User-Agent и пробую снова')
                        user_agent_random = random.choice(user_agents)
                        continue
                else:
                    print(f'{rq2.status} Неудачная авторизация')
                    continue
                rq3 = await s.post("https://hh.ru/shards/resume/batch_update",
                                   headers={"x-hhtmfrom":"","x-hhtmsource":"main","x-requested-with":"XMLHttpRequest","x-xsrftoken":csrf_token})
                sleep_up = config['app']['delay'] + random.randint(config['app']['random_min_delay'], config['app']['random_max_delay'])
                if rq3.status == 200:
                    print(f'{rq3.status} Успешно поднял резюме\nСледующее поднятие через {sleep_up} секунд')
                else:
                    print(f'{rq3.status} Неудачное поднятие резюме')
                    continue
                await asyncio.sleep(sleep_up)

        except Exception as e:
            print(f"Произошла ошибка: {e}")

asyncio.run(main())
