from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select, and_, not_
import config
from models import UserModel, FormModel, ActionModel
import time


class DataBase:
    '''
    Класс для работы с базой данных
    '''

    # Инициализация
    def __init__(self, db_url):
        self.engine = create_async_engine(db_url)
        self.async_session = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)


    # Создание сессии
    async def get_session(self):
        async with self.async_session() as session:
            yield session


    # Добавление информации о пользователе в БД
    async def add_user(self, session, message):
        try:
            # Проверка на наличие пользователя в таблице
            user_in_db = await session.get(UserModel, str(message.from_user.id))

            # Создание записи в бд, если ее не было
            if user_in_db is None:
                join_time = time.strftime('%d.%m.%Y / %X')

                user_info = UserModel(
                    enter = join_time,
                    id = str(message.from_user.id),
                    username = message.from_user.username,
                    name = message.from_user.first_name,
                    lastname = message.from_user.last_name,
                    last_action = None,
                    ban_status = None,
                    sub_status = None,
                    sub_end_date = None,
                    referrals = 0,
                    invited_by = None,
                    agreement = 0,
                    language = message.from_user.language_code,
                    admin = 0
                )

                # Добавление данных в сессию
                session.add(user_info)

                # Добавление данных в бд и сохранение
                await session.commit()
            
            else:
                pass
            
        except Exception as error:
            print(f'add_user() error: {error}')


    # Добавление информации о пользователе в БД
    async def update_username(self, session, user_id, username):
        try:
            user = await session.get(UserModel, str(user_id))
            user.username = username

            # Добавление данных в бд и сохранение
            await session.commit()

        except Exception as error:
            print(f'update_username() error: {error}')


    # Получение данных об анкете пользователя
    async def get_form_information(self, session, user_id):

        try:
            form = await session.get(FormModel, str(user_id))

            # Возвращается объект анкеты, в случае отсутствия None
            return form

        except Exception as error:
            print(f'get_form_information() error: {error}')


    # Обновление статуса анкеты
    async def update_status(self, session, form, new_status):

        try:
            form.status = new_status

            # Добавление данных в бд и сохранение
            await session.commit()

        except Exception as error:
            print(f'update_status() error: {error}')


    # Поиск подходящей анкеты
    async def get_form_id_by_filters(self, session, my_form):
        try:
            my_id = my_form.id
            my_city = my_form.city
            my_preferences = my_form.preferences
            my_gender = my_form.gender

            if my_preferences == 'С мужчинами':
                my_preferences = ['Мужчина']

            elif my_preferences == 'С женщинами':
                my_preferences = ['Женщина']

            elif my_preferences == 'Со всеми':
                my_preferences = ['Мужчина', 'Женщина']


            if my_gender == 'Мужчина':
                need_preferences = ['Со всеми', 'С мужчинами']

            elif my_gender == 'Женщина':
                need_preferences = ['Со всеми', 'С женщинами']

            # Поиск поставленных оценок
            marks = await session.execute(
                select(ActionModel.id_receiver)
                    .where(
                        ActionModel.id_creator == my_id
                        )
                )
            marks_list = [row for row in marks.scalars()]

            # Добавление своего id, чтобы не попалась своя анкета
            marks_list.append(my_id)

            # Фильтры: 
            # 1) По моим предпочтениям
            # 2) по городу
            # 3) совпадение предпочтений
            # 4) открытость анкеты
            result = await session.execute(
                select(FormModel)
                    .where(
                        and_(
                            FormModel.gender.in_(my_preferences),
                            FormModel.city == my_city,
                            FormModel.preferences.in_(need_preferences),
                            FormModel.status == 'open'
                            ),
                    )
                    .where(
                        not_(
                            FormModel.id.in_(marks_list)
                        )
                    )
                )
            result_list = [row for row in result.scalars()]

            return result_list[0]

        except Exception as error:
            print(f'get_form_id_by_filters() error: {error}')


    # Создание оценки
    async def like_or_dislike_form(self, session, user_id, form_id, mark):
        try:
            creation_time = time.strftime('%d.%m.%Y / %X')

            new_action = ActionModel(
                creation_date = creation_time,
                id_creator = str(user_id),
                id_receiver = str(form_id),
                status = mark,
                message = None
            )

            # Добавление данных в сессию
            session.add(new_action)

            # Добавление данных в бд и сохранение
            await session.commit()

        except Exception as error:
            print(f'like_or_dislike_form() error: {error}')


    # Создание жалобы
    async def make_warn(self, session, form_id):
        try:
            form = await session.get(FormModel, form_id)

            form.warns += 1

            # Если набирается 3 жалобы на анкете, то она блокируется и отправляется на проверку админам
            if form.warns == 3:
                form.status = 'blocked'

                # УВЕДОМЛЕНИЕ АДМИНАМ
                # УВЕДОМЛЕНИЕ ПОЛЬЗОВАТЕЛЮ

            # Добавление данных в бд и сохранение
            await session.commit()

        except Exception as error:
            print(f'make_warn() error: {error}')