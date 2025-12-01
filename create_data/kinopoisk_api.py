import re
import requests
from environs import Env

with open('genre_csv/Фэнтези.csv', 'r', encoding='utf-8') as f:
    with open(f'genre_with_info/{f.name[10:]}', 'a', encoding='utf-8') as file:
        information = f.readlines()
        file.writelines(information[0])
        for i in range(163, len(information)):
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
            if response.status_code == 200 and data and data.get("docs"):
                doc = data["docs"][0]
                id_kp = doc.get('id', '')
                en_name = doc.get('alternativeName', '')

                rating = doc.get('rating', {})
                kp_rate = rating.get('kp', 'N/A')
                imdb_rate = rating.get('imdb', 'N/A')
                critics_rate = rating.get('filmCritics', 'N/A')

                if len(res) > 5:
                    res[5] = str(kp_rate)
                    new_data = [
                        str(id_kp),
                        str(en_name),
                        str(imdb_rate),
                        str(critics_rate)
                    ]
                    res.extend(new_data)
                    final_res_string = ','.join(res) + '\n'
                    print(i)
                    print(final_res_string.strip())
                    file.writelines(final_res_string)
                else:
                    print("Ошибка: Список 'res' слишком короткий для модификации index 5.")