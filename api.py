from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from core import VkTools
from database import Database


class VkBot:
    def __init__(self, comunity_token, access_token):
        self.vk = vk_api.VkApi(token=comunity_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_tools = VkTools(access_token)
        self.db = Database()
        self.params = {}
        self.peoples = []
        self.offset = 0

    def send_message(self, user_id, message, attachment=None):
        params = {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)}

        if attachment:
            params['attachment'] = attachment

        self.vk.method('messages.send', params)

    def get_people(self):
        while True:

            if not self.peoples:
                self.offset += 50
                self.peoples = self.vk_tools.search_people(
                    self.params, self.offset)

            people = self.peoples.pop()

            if not self.db.user_in_table(people['id']):
                break

        photos = self.vk_tools.get_photos(people['id'])
        photo_string = ''

        for photo in photos:
            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'

        return people, photo_string

    # обработка событий / получение сообщений
    def start(self):
        self.db.create_table()

        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text.lower() == 'привет':
                    '''Логика для получения данных о пользователе'''
                    self.params = self.vk_tools.get_info_profile(event.user_id)
                    # для тестирования удалил город как пример
                    # del self.params['city']
                    self.send_message(
                        event.user_id, f'Привет {self.params["name"]}')

                    msg = ""

                    # если чего то не хватает то записываем так name: Вася Пупкин, sex: мужской и т.д
                    if self.params.get('name') is None:
                        msg += "\nНет данных про имя"
                    if self.params.get('sex') is None:
                        msg += "\nНет данных про пол"
                    if self.params.get('city') is None:
                        msg += "\nНет данных про город"
                    if self.params.get('year') is None:
                        msg += "\nНет данных про возраст"

                    if msg != "":
                        self.send_message(
                            event.user_id, f'{msg}')

                elif event.text.lower() == 'найти':
                    '''Логика для поиска анкет'''
                    self.send_message(
                        event.user_id, 'Начинаем поиск')

                    if self.peoples:
                        peoples = self.peoples.pop()
                        photos = self.vk_tools.get_photos(peoples['id'])
                        photo_string = ''

                        for photo in photos:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'

                    else:
                        self.peoples = self.vk_tools.search_people(
                            self.params, self.offset)

                        people, photo_string = self.get_people()

                    self.send_message(
                        event.user_id,
                        f'имя: {people["name"]} ссылка: vk.com/id{people["id"]}',
                        attachment=photo_string
                    )

                    'добавить анкету в бд в соотвествие с event.user_id'
                    self.db.insert_table(people['id'])

                elif event.text.lower() == 'следующий':
                    people, photo_string = self.get_people()

                    self.send_message(
                        event.user_id,
                        f'имя: {people["name"]} ссылка: vk.com/id{people["id"]}',
                        attachment=photo_string
                    )

                    'добавить анкету в бд в соотвествие с event.user_id'
                    self.db.insert_table(people['id'])

                elif event.text.lower() == 'пока':
                    self.send_message(
                        event.user_id, 'До свидания')

                elif ":" in event.text.lower():
                    for item in event.text.lower().split(","):
                        item = item.split(":")

                        if item[0] == "year":
                            self.params[item[0].strip()] = int(item[1].strip())
                        elif item[0] == "sex":
                            self.params[item[0].strip()] = 1 if item[1].strip() == "женский" else 2
                        else:
                            self.params[item[0].strip()] = item[1].strip()

                    self.send_message(
                        event.user_id, 'Данные дополнены')
                else:
                    self.send_message(
                        event.user_id, 'Неизвестная команда')
