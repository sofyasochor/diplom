from datetime import datetime

import vk_api
from vk_api.exceptions import ApiError


class VkTools:
    def __init__(self, access_token):
        self.vk_api = vk_api.VkApi(token=access_token)

    def _birthday_year(self, date):
        user_year = date.split('.')[2]
        return datetime.now().year - int(user_year)

    def get_info_profile(self, user_id):

        try:
            info, = self.vk_api.method('users.get',
                                      {'user_id': user_id,
                                       'fields': 'city,sex,relation,bdate'
                                       }
                                      )
        except ApiError as e:
            info = {}
            print(f'error = {e}')

        result = {'name': (info['first_name'] + ' ' + info['last_name']) if
                  'first_name' in info and 'last_name' in info else None,
                  'sex': info.get('sex'),
                  'city': info.get('city')['title'] if info.get('city') is not None else None,
                  'year': self._birthday_year(info.get('bdate'))
                  }
        return result

    def search_people(self, params, offset):
        try:
            users = self.vk_api.method('users.search',
                                      {
                                          'count': 50,
                                          'offset': offset,
                                          'hometown': params['city'],
                                          'sex': 1 if params['sex'] == 2 else 2,
                                          'has_photo': True,
                                          'age_from': params['year'] - 3,
                                          'age_to': params['year'] + 3,
                                      }
                                      )
        except ApiError as e:
            users = []
            print(f'error = {e}')

        result = [{'name': item['first_name'] + item['last_name'],
                   'id': item['id']
                   } for item in users['items'] if not item['is_closed']
                  ]

        return result

    def get_photos(self, id):
        try:
            photos = self.vk_api.method('photos.get',
                                       {'owner_id': id,
                                        'album_id': 'profile',
                                        'extended': 1
                                        }
                                       )
        except ApiError as e:
            photos = {}
            print(f'error = {e}')

        result = [{'owner_id': item['owner_id'],
                   'id': item['id'],
                   'likes': item['likes']['count'],
                   'comments': item['comments']['count']
                   } for item in photos['items']
                  ]

        '''сортировка по лайкам и комментам'''
        like_sorted = sorted(result, key=lambda x: x['likes'], reverse=True)
        сomments_sorted = sorted(like_sorted, key=lambda x: x['comments'], reverse=True)

        return сomments_sorted[:3]
