from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select
from aiogram import Bot
from aiogram.types import FSInputFile
import time
import datetime
import pytz
from PIL import Image
from PIL.ExifTags import TAGS

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
                    app_texts.NEW_PROFILE
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
                    photo= FSInputFile('web_registration/static/images/wait_verification.jpeg'),
                    caption= app_texts.SUCCEESS_UPDATE
                )

            elif action == 'created':
                await bot.send_photo(
                    user_id,
                    photo= FSInputFile('web_registration/static/images/wait_verification.jpeg'),
                    caption= app_texts.SUCCEESS_CREATE
                )

        except Exception as error:
            print(f'success_message({user_id}) error: {error}')


    # Скачивание списка фото
    async def download_photos(self, user_id, photos, upload_folder):
        # Функция для исправления ориентации изображения
        def fix_orientation(img):
            try:
                # Итерация по метаданным изображения
                for orientation in TAGS.keys():
                    if TAGS[orientation] == 'Orientation':
                        break

                exif = img._getexif()

                if exif is not None:
                    exif = dict(exif.items())

                    # Проверка наличия информации об ориентации
                    if orientation in exif:
                        # Поворот изображения в соответствии с информацией об ориентации
                        if exif[orientation] == 3:
                            img = img.rotate(180, expand=True)
                        elif exif[orientation] == 6:
                            img = img.rotate(270, expand=True)
                        elif exif[orientation] == 8:
                            img = img.rotate(90, expand=True)

            except Exception as e:
                print(f"Error fixing orientation: {e}")

            return img

        try:
            # Создание массива с будущими фотографиями
            photo_list = []
            num = 0
            timenow = time.strftime('%d%m%Y%H%M%S')

            # Скачивание фотографий
            for photo in photos:
                filename = f'{user_id}_{timenow}_{num}.jpeg'

                # Открытие изображения с использованием Pillow
                img = Image.open(photo.file)

                # Исправление ориентации изображения
                img = fix_orientation(img)

                # Если изображение слишком большое, сжатие в два раза
                if img.width > 3000 or img.height > 2000:
                    img = img.resize((img.width // 2, img.height // 2), Image.ANTIALIAS)

                # Сохранение изображения с качеством 80%
                img.save(f'{upload_folder}/{filename}', 'JPEG', quality=80)

                # Добавление имени файла в список фотографий
                photo_list.append(filename)
                num += 1

            return {'response': True, 'photo_list': photo_list, 'error': None}

        except Exception as error:
            print(f'download_photos({user_id=}) error: {error}')
            return {'response': False, 'photo_list': photo_list, 'error': error}
        

    # Скачивание фото по одному
    async def download_photo_by_one(self, user_id, photo, num, upload_folder):
        # Функция для исправления ориентации изображения
        def fix_orientation(img):
            try:
                # Итерация по метаданным изображения
                for orientation in TAGS.keys():
                    if TAGS[orientation] == 'Orientation':
                        break

                exif = img._getexif()

                if exif is not None:
                    exif = dict(exif.items())

                    # Проверка наличия информации об ориентации
                    if orientation in exif:
                        # Поворот изображения в соответствии с информацией об ориентации
                        if exif[orientation] == 3:
                            img = img.rotate(180, expand=True)
                        elif exif[orientation] == 6:
                            img = img.rotate(270, expand=True)
                        elif exif[orientation] == 8:
                            img = img.rotate(90, expand=True)

            except Exception as e:
                print(f"Error fixing orientation: {e}")

            return img

        try:
            timenow = time.strftime('%d%m%Y%H%M%S')

            filename = f'{user_id}_{timenow}_{num}.jpeg'

            # Открытие изображения с использованием Pillow
            img = Image.open(photo.file)

            # Исправление ориентации изображения
            img = fix_orientation(img)

            # Если изображение слишком большое, сжатие в два раза
            if img.width > 3000 or img.height > 2000:
                img = img.resize((img.width // 2, img.height // 2), Image.ANTIALIAS)

            # Сохранение изображения с качеством 80%
            img.save(f'{upload_folder}/{filename}', 'JPEG', quality=80)

            return {'response': True, 'photo_name': filename, 'error': None}

        except Exception as error:
            print(f'download_photo_by_one({user_id=}) error: {error}')
            return {'response': False, 'photo_name': filename, 'error': error}


    # Создание или обновление анкеты
    async def create_profile(self, session, profile_info):

        user_info = ProfileModel(
            creation_date = datetime.datetime.now(pytz.timezone('Europe/Moscow')),
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
            

    # Обновление анкеты
    async def update_profile(self, session, profile_info):
        try:
            # Поиск анкеты по user_id
            user_in_db = await session.get(ProfileModel, profile_info['user_id'])

            # Обновление данных в бд
            user_in_db.creation_date = datetime.datetime.now(pytz.timezone('Europe/Moscow'))
            user_in_db.status = 'wait'
            user_in_db.name = profile_info['name']
            user_in_db.gender = profile_info['gender']
            user_in_db.preferences = profile_info['preferences']
            user_in_db.city = profile_info['city']
            user_in_db.age = profile_info['age']
            user_in_db.target = profile_info['target']
            user_in_db.about = profile_info['about']
            user_in_db.warns = 0

            # Если есть фото, то обновляется
            if profile_info['photo_list']:
                user_in_db.photos = profile_info['photo_list']

        
            # Добавление данных в бд и сохранение
            await session.commit()

            return {'response': True, 'profile_status': 'updated', 'error': None}

        except Exception as error:
            print(f'create_profile() Updating error: {error}')
            return {'response': False, 'profile_status': 'not_updated', 'error': error}
            

    # Создание или обновление анкеты
    async def get_profile_information(self, session, user_id):

        # Поиск анкеты по user_id
        try:
            profile_information = await session.get(ProfileModel, user_id)
            return profile_information

        except Exception as error:
            print(f'get_profile_information() error: {error}')
