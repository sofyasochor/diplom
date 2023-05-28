from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from database import insert_table, user_in_table, create_table


# токен группы
token = 'vk1.a.jSGEQeA8_ZUzkhDtbhLnSwVCMOP7ZJqnr6hmeUGPmMXyuP6_0nDRr0PZPLu4uSvrp_7oXygg1vmI6vslFmbKfazQzK7xzmwD-Sqtp9UmzsnBZXsD8rYLPKQtdOOUY2ORlRBr02AKgSW5FHhWvIDIlPIw-fBMtNeSmIjcACk6zjporLxM2cCW3pKW88BZ6wSjQhYhNENAj7idXn9eUC8y5A'

# токен приложения чтобы делать запросы по поиску людей
token_application = "vk1.a.d0E0HZZoRj1fnrrgI-kzhqAhvpCPxTvLM9VkxQmrYiof9yV_MGHOxOSFwUDqHBK8oXD4rAvVuwcDmVjZDsNtDCiCYZrcrwOHZi2SL32kn-7Sg6n14U3HYCMDVxy_EYYmlwxyyV8mFQMJQ5J8RsUkwPUVN2dEL-7r8aicA9KNAoxmr6OrEagzK6t5goa6d7ZYkywwTd2z01j7Sjo83qcWlg"

vk = vk_api.VkApi(token=token)
vk_new = vk_api.VkApi(token=token_application)
longpoll = VkLongPoll(vk)


def send_message(user_id, message, attachment=None):
    params = {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)}

    if attachment:
        params['attachment'] = attachment

    vk.method('messages.send', params)


def get_info_user(user_id):
    data = vk_new.method('users.get', {'access_token': token_application, 'user_ids': user_id,
                                       'fields': "sex, city, status, age"})
    return data


def get_status(status):
    if status.lower() in "не женат (не замужем)":
        return 1
    elif status.lower() == "встречается":
        return 2
    elif status.lower() in "помолвлена":
        return 3
    elif status.lower() in "женат (замужем)":
        return 4
    elif status.lower() == "всё сложно":
        return 5
    elif status.lower() == "в активном поиске":
        return 6
    elif status.lower() in "влюблена":
        return 7
    elif status.lower() == "в гражданском браке":
        return 8


def get_sex(sex):
    if isinstance(sex, int):
        if sex == 1:
            return "женский"

        elif sex == 2:
            return "мужской"

        return "неизвестно"

    else:
        if sex == "женский":
            return 1

        elif sex == "мужской":
            return 2

        return 0


data = []
offset = -50


def main():
    flag = False
    info_search = {}
    fields = ["sex", "status", "city", "age", "name"]
    input_field = None
    create_table()
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:

            if event.to_me:
                request = event.text

                if flag:
                    arsg = request.split(",")

                    if input_field != None:
                        for i, field in enumerate(input_field):
                            info_search[field] = arsg[i]

                    name = info_search.get('name').strip()
                    age = int(str(info_search.get('age')).strip())
                    sex = get_sex(str(info_search.get('sex')).strip())
                    city = info_search.get('city').strip()
                    status = get_status(info_search.get('status').strip())

                    global data
                    response = None

                    if not data:
                        global offset

                        offset += 50

                        data = vk_new.method('users.search', {'offset': offset,
                                                              'access_token': token_application, 'q': name, 'count': 50,
                                                              'hometown': city, 'sex': sex,
                                                              'age_to': age, 'status': status,
                                                              'fields': "about, city, sex, crop_photo, domain"
                                                              })

                    for item in data['items'].copy():
                        if item.get('crop_photo') is None:
                            data['items'].remove(item)
                            continue

                        id_ = item['id']
                        if user_in_table(id_):
                            data['items'].remove(item)
                            continue

                        response = item
                        break

                    sex = response['sex']
                    first_name = response['first_name']
                    last_name = response['last_name']
                    sex = get_sex(sex)

                    msg = f"ИМЯ - {first_name}\nФамилия - {last_name}\nПол - {sex}\nГород - {city}"

                    send_message(event.user_id, msg)

                    owner_id = response['crop_photo']['photo']['owner_id']
                    photo_id = response['crop_photo']['photo']['id']

                    attachment = f'photo{owner_id}_{photo_id}_{token_application}'

                    send_message(event.user_id, "аватарка", attachment=attachment)
                    insert_table(id_)
                    flag = False

                else:
                    user_data = get_info_user(event.user_id)
                    user_data = user_data[0]

                    try:
                        city = user_data['city']['title']
                        info_search['city'] = city
                    except KeyError:
                        ...

                    try:
                        status = user_data['status']

                        if status != "":
                            info_search['status'] = status

                    except KeyError:
                        ...

                    try:
                        sex = user_data['sex']

                        if sex == 2:
                            sex = 1
                            info_search['sex'] = sex
                        elif sex == 1:
                            sex = 2
                            info_search['sex'] = sex

                    except KeyError:
                        ...

                    s = "Введите недостающие поля через запятую: "
                    f = fields.copy()

                    for field in f.copy():
                        if field not in info_search:
                            s += field + " "
                        else:
                            f.remove(field)

                    flag = True
                    input_field = f
                    send_message(event.user_id, s)


if __name__ == "__main__":
    main()
