from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile

from bot.database import DataBase

import config
import asyncio
import time
import pytz
import datetime


database = DataBase(config.DATABASE_URL)


# Уведомление о регистрации спустя три часа после входа пользователя
async def notification_after_three_hours():

    '''
    НЕ СДЕЛАНА ОТПРАВКА СООБЩЕНИЯ !!!
    '''

    while True:
        # Создание сессии
        async for session in database.get_session():

            # Получения списка пользователей у которых нет анкеты
            print('\n1) Получение данных о пользователях из БД')
            users_without_profile = await database.get_users_without_profile(session)

            # Текущее время
            current_time = datetime.datetime.now(pytz.timezone('Europe/Moscow'))

            for user in users_without_profile:
                # Сколько время прошло со входа юзера
                timedelta = current_time - user.enter

                # Отправка уведомления если прошло от 3 до 4 часов с момента входа пользователя в бота
                if timedelta >= datetime.timedelta(hours=3) and timedelta <= datetime.timedelta(hours=4):
                    # СДЕЛАТЬ УВЕДОМЛЕНИЕ
                    print(f'\n1) {user.username} получил уведомление')
                else:
                    # print(f'\n1) {user.username} не получил уведомление')
                    pass

        print('\n1) уведомления разосланы, перерыв на час')
        time.sleep(5)
        # time.sleep(3600)


# Уведомление о регистрации каждую неделю
async def notification_every_week():

    '''
    НЕ СДЕЛАНА ОТПРАВКА СООБЩЕНИЯ И ЛОГИКА !!!
    '''

    while True:
        # Создание сессии
        async for session in database.get_session():

            # Получения списка пользователей у которых нет анкеты
            print('\n2) Получение данных о пользователях из БД')
            users_without_profile = await database.get_users_without_profile(session)
            
        time.sleep(5)


async def main():
    # Запускаем обе функции параллельно
    await asyncio.gather(notification_after_three_hours(), notification_every_week())

if __name__ == '__main__':
    asyncio.run(main())