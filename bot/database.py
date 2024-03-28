from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select, and_, not_
import config
from models import UserModel, FormModel, ActionModel


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

                user_info = UserModel(
                    enter = None,
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
            # 2) По городу
            # 3) Совпадение предпочтений
            # 4) Открытость анкеты
            result = await session.execute(
                select(FormModel)
                    .where(
                        and_(
                            # По моим предпочтениям
                            FormModel.gender.in_(my_preferences),

                            # По городу
                            FormModel.city == my_city,

                            # Совпадение предпочтений
                            FormModel.preferences.in_(need_preferences),

                            # Открытость анкеты
                            FormModel.status == 'open'
                        ),
                    )
                    .where(
                        not_(
                            # Исключение своего id
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
            new_action = ActionModel(
                creation_date = None,
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

            # Добавление данных в бд и сохранение
            await session.commit()

            return form.warns

        except Exception as error:
            print(f'make_warn() error: {error}')


    # Сообщение админам в телеграм о создании новой анкеты
    async def notify_admins(self, session, bot, message_text):
        try:
            # Выполняем запрос для получения id пользователей, у которых admin равно 1
            result = await session.execute(select(UserModel.id).where(UserModel.admin == 1))
            admin_ids = [row for row in result.scalars()]

            # Рассылка админам
            for id in admin_ids:
                await bot.send_message(
                    id,
                    message_text
                )

        except Exception as error:
            print(f'notify_admins() error: {error}')

    # Проверка на админа
    async def check_admin(self, session, user_id):
        try:
            user = await session.get(UserModel, str(user_id))

            if user.admin == 1:
                return True
            else:
                return False

        except Exception as error:
            print(f'check_admin() error: {error}')


    # Рассылка сообщения всем пользователям
    async def send_message_to_everyone(self, session, bot, text, entities, photo= None, keyboard=None, parse_mode=None):
        try:
            users = await session.execute(select(UserModel.id))

            # Список всех id пользователей
            user_ids = [row for row in users.scalars()]

            if photo:
                for id in user_ids:
                    try:
                        await bot.send_photo(chat_id=id, photo=photo, caption=text, caption_entities=entities, reply_markup=keyboard, parse_mode=parse_mode)
                        print(f'Рассылка с фото: {id}')

                    # Исключение если человек заблочил бота
                    except Exception as error:
                        print(error)
                        # print(f'{id} заблочил бота')

            else:
                for id in user_ids:
                    try:
                        await bot.send_message(chat_id=id, text=text, entities=entities, disable_web_page_preview=True, parse_mode=parse_mode)
                        print(f'Рассылка без фото: {id}')

                    # Исключение если человек заблочил бота
                    except Exception as error:
                        print(f'{id} заблочил бота')

        except Exception as error:
            print(f'send_message_to_everyone() error: {error}')


    # Получение статистики бота
    async def get_stats(self, session):
        try:
            users = await session.execute(select(UserModel))
            users_amount = len(users.fetchall())

            forms = await session.execute(select(FormModel))
            forms_amount = len(forms.fetchall())

            message = f'<b>📋 Статистика</b>\n\nВсего пользователей: <b>{users_amount}</b>\nВсего анкет: <b>{forms_amount}</b>'
            return message

        except Exception as error:
            print(f'get_stats() error: {error}')


    # Получение статистики бота
    async def get_form_for_verification(self, session):
        try:
            waited_blocked_forms = await session.execute(
                select(FormModel)
                    .where(
                        FormModel.status.in_(['blocked', 'wait']),
                    )
                )
            forms = [row for row in waited_blocked_forms.scalars()]

            return forms[0]

        except Exception as error:
            print(f'get_form_for_check() error: {error}')


    # Подтверждение анкеты
    async def update_status_form(self, session, form_id, status):
        try:
            form = await session.get(FormModel, form_id)
            form.status = status

            # Если анкеты была забанена, то пользователь тоже блокируется
            if status == 'banned':
                user = await session.get(UserModel, form_id)
                user.ban_status = status

            # Добавление данных в бд и сохранение
            await session.commit()

        except Exception as error:
            print(f'update_status_form() error: {error}')