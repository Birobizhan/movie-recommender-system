import re
import requests
from environs import Env

with open('genre_csv/Биографический.csv', 'r', encoding='utf-8') as f:
    with open(f'genre_with_info/{f.name[10:]}', 'a', encoding='utf-8') as file:
        information = f.readlines()
        file.writelines(information[0])
        for i in range(1, len(information)):
            res = re.split(r',(?=\S)', information[i])
            name = res[0]
            rate = float(res[5].rstrip())
            url = 'https://api.kinopoisk.dev/v1.4/movie/search'
            params = {
                'page': 1,
                'limit': 10,
                'query': f'{name}'
            }
            env = Env()
            env.read_env()
            kinopoisk_key = env("KINOPOISK_TOKEN")
            headers = {
                'X-API-KEY': f'{kinopoisk_key}',
                'accept': 'application/json'
            }

            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            if response.status_code == 200 and data["docs"]:
                id_kp = data['docs'][0]['id']
                en_name = data['docs'][0]['alternativeName']
                kp_rate = data["docs"][0]['rating']['kp']
                imdb_rate = data["docs"][0]['rating']['imdb']
                critics_rate = data["docs"][0]['rating']['filmCritics']
                res[5] = f'{kp_rate}\n'
                res.append(f'{id_kp}\n')
                res.append(f'{en_name}\n')
                res.append(f'{imdb_rate}\n')
                res.append(f'{critics_rate}\n')
                res = ','.join(res)
                print(res)
                file.writelines(res)
            else:
                print(f'Ошибка: {response.status_code} - {response.text}')
                break
