
def parse_status(data):
    back_status = data['services']['backend_api']['status']
    back_message = data['services']['backend_api']['message']
    db_status = data['services']['database']['status']
    db_message = data['services']['database']['message']
    front_status = data['services']['frontend_ui']['status']
    front_message = data['services']['frontend_ui']['message']
    if back_status == 'ok' and db_status == 'ok' and front_status == 'ok':
        answer = (f'Все 3 сервиса работают без проблем:\n'
                  f'{back_message}\n'
                  f'{db_message}\n'
                  f'{front_message}')
    else:
        answer = (f'Есть проблемы с сервисами, сейчас они работают так:\n'
                  f'{back_message}\n'
                  f'{db_message}\n'
                  f'{front_message}')
    return answer


def parse_db(data):
    answer = (f'Состояние базы данных:\n'
              f'Работает исправно\n'
              f'Характеристики БД: Количество фильмов: {data["movies_count"]}\n'
              f'Количество пользователей: {data["users_count"]}\n'
              f'Количество отзывов и оценок: {data["reviews_count"]}\n'
              f'Количество списков: {data["lists_count"]}\n'
              f'Количество списков, созданных пользователями: {data["users_created_list"]}')
    return answer


def parse_full_report(data):
    pass