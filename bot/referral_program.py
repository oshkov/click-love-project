import requests
import json


class PyRepka:
    '''
    Этот класс предоставляет методы для взаимодействия с API реферальной программы "Репка".

    Пример использования:
    repka = pyRepka(bot_access_token, bot_username, ip, port)
    repka.check_user_ref(user_id)
    '''

    def __init__(
        self,
        bot_access_token: str,
        bot_username: str,
        ip: str,
        port: str
    ):
        '''
        Инициализация 
        
        :param bot_access_token: Токен для подключения к Репке.
        :param bot_username: Юзернейм бота.
        :param ip: IP-адрес сервера, на котором работает API.
        :param port: Порт сервера, на котором работает API.
        '''

        self.bot_access_token = bot_access_token
        self.bot_username = bot_username
        self.url = f"http://{ip}:{port}"


    def check_user_ref(
        self,
        user_id: int,
    ): 
        '''
        Проверить, является ли пользователь участником реферальной программы

        :param user_id: ID пользователя, которого необходимо проверить.
        '''

        try:
            # Формирование URL-адреса запроса
            request = f'{self.url}/api/Users/CheckUserRef'

            # Формирование параметров запроса
            params = {
                "userId": user_id,
                "botUsername": self.bot_username,
                "botAccessToken": self.bot_access_token
            }

            # Отправка GET-запроса
            response = requests.get(request, params=params)

            return response

        except Exception as error:
            print(f'ERROR check_user_ref(): {error}')


    def add_user_to_ref(
        self,
        user_id: int,
        first_name: str,
        last_name: str,
        username: str,
        inviter_id: int = None
    ):
        '''
        Добавить пользователя в реф. программу

        :param user_id: ID пользователя, который добавляется в реф. программу.
        :param first_name: Имя пользователя.
        :param last_name: Фамилия пользователя.
        :param username: Юзернейм пользователя.
        :param inviter_id: ID пользователя, который пригласил, если он есть.
        '''

        try:
            # Формирование URL-адреса запроса
            request = f'{self.url}/api/Users/AddUserToRef'

            # Формирование данных для отправки в виде словаря
            data = {
                "id": user_id,
                "firstName": first_name,
                "lastName": last_name,
                "username": username,
                "fromBotUsername": self.bot_username,
                "botAccessToken": self.bot_access_token,
                "inviterCode": inviter_id
            }

            # Преобразование данных в JSON
            json_data = json.dumps(data)

            # Определение заголовков запроса
            headers = {'Content-Type': 'application/json'}

            # Отправка POST-запроса
            response = requests.post(request, headers=headers, data=json_data)

            return response

        except Exception as error:
            print(f'ERROR add_user_to_ref(): {error}')

    
    def get_referral_users(
        self,
        user_id: int,
    ):
        '''
        Получить количество пользователей на каждом уровне

        :param user_id: ID пользователя, у которого нужно узнать количество пользователей на каждом уровне.
        '''
 
        try:
            # Формирование URL-адреса запроса
            request = f'{self.url}/api/Users/GetReferralUsers'

            # Формирование параметров запроса
            params = {
                "userId": user_id,
                "botUsername": self.bot_username,
                "botAccessToken": self.bot_access_token
            }

            # Отправка GET-запроса
            response = requests.get(request, params=params)

            return response

        except Exception as error:
            print(f'ERROR get_referral_users(): {error}')


    def get_user_balance(
        self,
        user_id: int
    ):
        '''
        Получить баланс пользователя

        :param user_id: ID пользователя, баланс которого нужно узнать.
        '''

        try:
            # Формирование URL-адреса запроса
            request = f'{self.url}/api/Users/GetUserBalance'

            # Формирование параметров запроса
            params = {"userId": user_id}

            # Отправка GET-запроса
            response = requests.get(request, params=params)

            return response

        except Exception as error:
            print(f'ERROR get_user_balance(): {error}')


    def purchase(
        self,
        user_id: int,
        points: int,
        reason: str
    ):
        '''
        Покупка (за баллы)

        :param user_id: ID пользователя, который совершает покупку.
        :param points: Количество баллов, которые будут списаны с баланса пользователя.
        :param reason: Название операции.
        '''

        try:
            # Формирование URL-адреса запроса
            request = f'{self.url}/api/Users/Purchase'

            # Формирование данных для отправки в виде словаря
            data = {
                "userId": user_id,
                "botUsername": self.bot_username,
                "botAccessToken": self.bot_access_token,
                "points": points,
                "reason": reason
            }

            # Преобразование данных в JSON
            json_data = json.dumps(data)

            # Определение заголовков запроса
            headers = {'Content-Type': 'application/json'}

            # Отправка POST-запроса
            response = requests.post(request, headers=headers, data=json_data)

            return response

        except Exception as error:
            print(f'ERROR purchase(): {error}')


    def replenishment(
        self,
        user_id: int,
        points: int,
        reason: str
    ):
        '''
        Зафиксировать факт пополнения баланса пользователя с помощью эквайринга

        :param user_id: ID пользователя, чей баланс пополняется.
        :param points: Количество баллов, которое пополняется на баланс пользователя.
        :param reason: Название операции.
        '''

        try:
            # Формирование URL-адреса запроса
            request = f'{self.url}/api/Users/Replenishment'

            # Формирование данных для отправки в виде словаря
            data = {
                "userId": user_id,
                "botUsername": self.bot_username,
                "botAccessToken": self.bot_access_token,
                "points": points,
                "reason": reason
            }

            # Преобразование данных в JSON
            json_data = json.dumps(data)

            # Определение заголовков запроса
            headers = {'Content-Type': 'application/json'}

            # Отправка POST-запроса
            response = requests.post(request, headers=headers, data=json_data)

            return response

        except Exception as error:
            print(f'ERROR replenishment(): {error}')