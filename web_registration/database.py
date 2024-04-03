from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select
from aiogram import Bot
from aiogram.types import FSInputFile
import time
import shutil

import config
import web_registration.app_texts as app_texts
from models import UserModel, ProfileModel


bot = Bot(token=config.BOT_TOKEN)


class DataBase:
    '''
    Класс для работы с базой данных
    '''

    # Инициализация
    def __init__(self, db_url):
        self.engine = create_async_engine(db_url)
        self.async_session = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        self.base = declarative_base()

    # Создание сессии
    async def get_session(self):
        async with self.async_session() as session:
            yield session

    # Создание всех таблиц (Не используется)
    async def init_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(self.base.metadata.create_all)


    # Сообщение админам в телеграм о создании новой анкеты
    async def notify_admins(self, session):
        try:
            # Выполняем запрос для получения id пользователей, у которых admin равно 1
            result = await session.execute(select(UserModel.id).where(UserModel.admin == 1))
            admin_ids = [row for row in result.scalars()]

            for id in admin_ids:
                await bot.send_message(
                    id,
                    app_texts.new_profile
                )

        except Exception as error:
            print(f'notify_admins() error: {error}')
        pass


    # Сообщение пользователю в телеграм о создании или обновлении анкеты
    async def success_message(self, user_id, action):
        try: 
            if action == 'updated':
                await bot.send_photo(
                    user_id,
                    photo= FSInputFile('web_registration/static/wait_verification.jpeg'),
                    caption= app_texts.success_update
                )

            elif action == 'created':
                await bot.send_photo(
                    user_id,
                    photo= FSInputFile('web_registration/static/wait_verification.jpeg'),
                    caption= app_texts.success_create
                )

        except Exception as error:
            print(f'success_message({user_id}) error: {error}')


    # Скачивание фото
    async def download_photos(self, user_id, photos, upload_folder):
        try:
            # Создание массива с будующими фотками
            photo_list = []
            num = 0
            timenow = time.strftime('%d%m%Y%H%M%S')

            # Скачивание фото
            for photo in photos:
                # Имя для фото: дата + номер фото
                photo.filename = f'{user_id}_{timenow}_{num}.jpeg'

                # Добавление фото в список фотографий
                photo_list.append(photo.filename)

                # Скачивание фото
                with open(f'{upload_folder}/{photo.filename}', 'wb') as buffer:
                    shutil.copyfileobj(photo.file, buffer)
                num += 1

            return {'response': True, 'photo_list': photo_list, 'error': None}

        except Exception as error:
            print(f'download_photos({user_id=}) error: {error}')
            return {'response': False, 'photo_list': photo_list, 'error': error}


    # Создание или обновление анкеты
    async def create_profile(self, session, profile_info):
        # Поиск анкеты по user_id
        user_in_db = await session.get(ProfileModel, profile_info['user_id'])

        # Если анкета уже была, то ее данные обновляются
        if user_in_db:
            # Обновление данных в бд
            user_in_db.status = 'wait'
            user_in_db.name = profile_info['name']
            user_in_db.gender = profile_info['gender']
            user_in_db.preferences = profile_info['preferences']
            user_in_db.city = profile_info['city']
            user_in_db.age = profile_info['age']
            user_in_db.target = profile_info['target']
            user_in_db.about = profile_info['about']
            user_in_db.photos = profile_info['photo_list']
            user_in_db.warns = 0

            try:
                # Добавление данных в бд и сохранение
                await session.commit()

                return {'response': True, 'profile_status': 'updated', 'error': None}

            except Exception as error:
                print(f'create_profile() Updating error: {error}')
                return {'response': False, 'profile_status': 'not_updated', 'error': error}

        # Если анкеты не было, то она создается
        else:
            user_info = ProfileModel(
                creation_date = None,
                id = profile_info['user_id'],
                username = profile_info['username'],
                status = 'wait',
                name = profile_info['name'],
                gender = profile_info['gender'],
                preferences = profile_info['preferences'],
                city = profile_info['city'],
                age = profile_info['age'],
                vk_url = None,
                target = profile_info['target'],
                about = profile_info['about'],
                photos = profile_info['photo_list'],
                warns = 0
            )

            try:
                # Добавление данных в сессию
                session.add(user_info)

                # Добавление данных в бд и сохранение
                await session.commit()

                return {'response': True, 'profile_status': 'created', 'error': None}

            except Exception as error:                
                print(f'create_profile() Creating error: {error}')
                return {'response': False, 'profile_status': 'not_created', 'error': error}
            

    # Создание или обновление анкеты
    async def get_profile_information(self, session, user_id):

        # Поиск анкеты по user_id``
        try:
            profile_information = await session.get(ProfileModel, user_id)
            return profile_information

        except Exception as error:                
            print(f'get_profile_information() error: {error}')
