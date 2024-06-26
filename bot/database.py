from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select, and_, not_
import datetime
import pytz
import random
from models import UserModel, ProfileModel, ActionModel


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

                # year_sub = datetime.datetime.now(pytz.timezone('Europe/Moscow')) + datetime.timedelta(days=365)
                # year_sub_status = 'Годовая подписка'

                user_info = UserModel(
                    enter = datetime.datetime.now(pytz.timezone('Europe/Moscow')),
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
                return True

            else:
                return False

        except Exception as error:
            print(f'add_user() error: {error}')
            return False


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
    async def get_profile_information(self, session, user_id):
        try:
            profile = await session.get(ProfileModel, str(user_id))

            # Возвращается объект анкеты, в случае отсутствия None
            return profile

        except Exception as error:
            print(f'get_profile_information() error: {error}')


    # Получение данных о пользователе
    async def get_user_information(self, session, user_id):
        try:
            user = await session.get(UserModel, str(user_id))

            # Возвращается объект анкеты, в случае отсутствия None
            return user

        except Exception as error:
            print(f'get_user_information() error: {error}')


    # Обновление статуса анкеты из меню
    async def update_status(self, session, profile, new_status):

        try:
            profile.status = new_status

            # Добавление данных в бд и сохранение
            await session.commit()

        except Exception as error:
            print(f'update_status() error: {error}')


    # Поиск подходящей анкеты
    async def get_profile_id_by_filters(self, session, my_profile):
        # Получение данных для поиска анкеты, относительно моей анкеты
        try:
            my_id = my_profile.id                       # Мой id
            my_city = my_profile.city                   # Мой город
            my_preferences = my_profile.preferences     # Мои предпочтения
            my_gender = my_profile.gender               # Мой пол

            # Получения пола, относительно моих предпочтений
            if my_preferences == 'С мужчинами':
                my_preferences = ['Мужчина']
            elif my_preferences == 'С женщинами':
                my_preferences = ['Женщина']
            elif my_preferences == 'Со всеми':
                my_preferences = ['Мужчина', 'Женщина']

            # Получение предпочтений для поиска у других людей
            if my_gender == 'Мужчина':
                need_preferences = ['Со всеми', 'С мужчинами']
            elif my_gender == 'Женщина':
                need_preferences = ['Со всеми', 'С женщинами']

            # Получение списка id, кому ставил оценки
            execute = await session.execute(
                select(ActionModel.id_receiver)
                    .where(
                        ActionModel.id_creator == my_id
                    )
                )
            viewed_ids = [row for row in execute.scalars()]
            # Добавление своего id, чтобы не попалась своя анкета
            viewed_ids.append(my_id)

        except Exception as error:
            print(f'get_profile_id_by_filters() info about my profile error: {error}')


        # Поиск подходящей анкеты
        try:
            '''
            Фильтры: (С ГОРОДОМ)
            1) По моим предпочтениям
            2) По городу
            3) Совпадение предпочтений
            4) Открытость анкеты
            5) Отсутствие оценки

            Вывод рандомной анкеты из списка полученных по фильтрам
            '''
            result = await session.execute(
                select(ProfileModel)
                    .where(
                        and_(
                            # По моим предпочтениям
                            ProfileModel.gender.in_(my_preferences),

                            # По городу
                            ProfileModel.city == my_city,

                            # Совпадение предпочтений
                            ProfileModel.preferences.in_(need_preferences),

                            # Открытость анкеты
                            ProfileModel.status == 'open'
                        ),
                    )
                    .where(
                        not_(
                            # Исключение уже просмотренных анкет и своего id 
                            ProfileModel.id.in_(viewed_ids)
                        )
                    )
                )
            result_list = [row for row in result.scalars()]

            # Если есть анкеты с фильтром по городу, то выводятся
            if len(result_list) != 0:
                # print(f'С фильтром по городу: {result_list[0]}')
                return random.choice(result_list)


            '''
            Фильтры: (БЕЗ ГОРОДА)
            1) По моим предпочтениям
            2) Совпадение предпочтений
            3) Открытость анкеты
            4) Отсутствие оценки

            Вывод рандомной анкеты из списка полученных по фильтрам
            '''
            result = await session.execute(
                select(ProfileModel)
                    .where(
                        and_(
                            # По моим предпочтениям
                            ProfileModel.gender.in_(my_preferences),

                            # Совпадение предпочтений
                            ProfileModel.preferences.in_(need_preferences),

                            # Открытость анкеты
                            ProfileModel.status == 'open'
                        ),
                    )
                    .where(
                        not_(
                            # Исключение уже просмотренных анкет и своего id 
                            ProfileModel.id.in_(viewed_ids)
                        )
                    )
                )
            result_list = [row for row in result.scalars()]

            # Если есть анкеты без фильтра по городу
            if len(result_list) != 0:
                # print(f'Без фильтра по городу: {result_list[0]}')
                return random.choice(result_list)


            '''
            Вывод анкет по кругу:
            1) С дизлайками, поставленными не ранее 1 минуты
            2) Которые никогда не были лайкнуты
            3) С проверкой на актуальные предпочтения и открытость анкеты

            Вывод рандомной анкеты из списка полученных по фильтрам
            '''
            # Определение времени 1 минуту назад
            one_minute_ago = datetime.datetime.now(pytz.timezone('Europe/Moscow')) - datetime.timedelta(minutes=1)

            # Получение списка id, кому ставил дизлайк
            execute = await session.execute(
                select(ActionModel.id_receiver)
                    .where(
                        and_(
                            ActionModel.id_creator == my_id,
                            ActionModel.status == 'dislike',
                        ),
                    )
                )
            disliked_ids = [row for row in execute.scalars()]

            # Получение списка id, кому ставил дизлайк за последние 5 минут
            execute = await session.execute(
                select(ActionModel.id_receiver)
                    .where(
                        and_(
                            ActionModel.id_creator == my_id,
                            ActionModel.status == 'dislike',
                            ActionModel.creation_date > one_minute_ago
                        ),
                    )
                )
            disliked_one_minute_ids = [row for row in execute.scalars()]

            # Получение списка id, кому ставил лайк, суперлайк и предупреждение
            execute = await session.execute(
                select(ActionModel.id_receiver)
                    .where(
                        and_(
                            ActionModel.id_creator == my_id,
                            ActionModel.status.in_(['like', 'warn', 'superlike'])
                        )
                    )
                )
            liked_warned_ids = [row for row in execute.scalars()]

            # Проверка на актуальные совпадения предпочтений у анкет
            result = await session.execute(
                select(ProfileModel.id)
                    .where(
                        and_(
                            ProfileModel.id.in_(disliked_ids),
                            ProfileModel.gender.in_(my_preferences),
                            ProfileModel.preferences.in_(need_preferences),
                            ProfileModel.status == 'open'
                        ),
                    )
                )
            actual_profiles = [row for row in result.scalars()]

            # Удаление из disliked_ids всех значений, которые совпадают с liked_warned_ids
            disliked_ids = [id_ for id_ in disliked_ids if id_ not in liked_warned_ids]

            # Удаление из disliked_ids всех значений, которые совпадают с disliked_one_minute_ids
            disliked_ids = [id_ for id_ in disliked_ids if id_ not in disliked_one_minute_ids]

            # Оставление из disliked_ids всех значений, которые совпадают с actual_profiles
            disliked_ids = [id_ for id_ in disliked_ids if id_ in actual_profiles]

            # # print(f'{actual_profiles=}')
            # # print(f'{disliked_ids=}')
            # # print(f'{liked_ids=}')
            # # print(f'По кругу кому поставил дизлайк: {profile.id}')

            # Получение объекта анкеты
            profile = await session.get(ProfileModel, str(random.choice(disliked_ids)))

            return profile
            
        except IndexError:
            return None

        except Exception as error:
            print(f'get_profile_id_by_filters() error: {error}')
            return None


    # Создание оценки
    async def like_or_dislike_profile(self, session, user_id, profile_id, mark):
        try:
            new_action = ActionModel(
                creation_date = datetime.datetime.now(pytz.timezone('Europe/Moscow')),
                id_creator = str(user_id),
                id_receiver = str(profile_id),
                status = mark,
                message = None
            )

            # Добавление данных в сессию
            session.add(new_action)

            # Добавление данных в бд и сохранение
            await session.commit()

        except Exception as error:
            print(f'like_or_dislike_profile() error: {error}')


    # Создание жалобы
    async def make_warn(self, session, user_id, profile_id):
        try:
            profile = await session.get(ProfileModel, profile_id)

            profile.warns += 1

            # Если набирается 3 жалобы на анкете, то она блокируется и отправляется на проверку админам
            if profile.warns == 3:
                profile.status = 'blocked'

            # Добавляется запись в таблицу оценок
            new_action = ActionModel(
                creation_date = datetime.datetime.now(pytz.timezone('Europe/Moscow')),
                id_creator = str(user_id),
                id_receiver = str(profile_id),
                status = 'warn',
                message = None
            )

            # Добавление данных в сессию
            session.add(new_action)

            # Добавление данных в бд и сохранение
            await session.commit()

            return profile.warns

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
    async def send_message_to_everyone(self, session, bot, text, entities, photo= None, keyboard=None, parse_mode=None, black_list=[]):
        try:
            users = await session.execute(select(UserModel.id))

            # Список всех id пользователей
            user_ids = [row for row in users.scalars()]

            if photo:
                for id in user_ids:
                    if id not in black_list:
                        try:
                            await bot.send_photo(chat_id=id, photo=photo, caption=text, caption_entities=entities, reply_markup=keyboard, parse_mode=parse_mode)
                            print(f'Рассылка с фото: {id}')

                        # Исключение если человек заблочил бота
                        except Exception as error:
                            print(error)
                            print(f'{id} заблочил бота')

            else:
                for id in user_ids:
                    if id not in black_list:
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
            # Получение количества пользователей
            users = await session.execute(select(UserModel))
            users_amount = len(users.fetchall())

            # Количество открытых анкет
            profiles = await session.execute(
                select(ProfileModel)
                    .where(
                        ProfileModel.status == 'open',
                    )
                )
            active_profiles_amount = len(profiles.fetchall())

            # Количество закрытых анкет
            closed_profiles = await session.execute(
                select(ProfileModel)
                    .where(
                        ProfileModel.status == 'closed',
                    )
                )
            closed_profiles_amount = len(closed_profiles.fetchall())

            # Количество непроверенных анкет
            waited_profiles = await session.execute(
                select(ProfileModel)
                    .where(
                        ProfileModel.status == 'wait',
                    )
                )
            waited_profiles_amount = len(waited_profiles.fetchall())

            # Количество анкет мужчин
            men_profiles = await session.execute(
                select(ProfileModel)
                    .where(
                        and_(
                            ProfileModel.gender == 'Мужчина',
                            ProfileModel.status.in_(['open', 'closed'])
                        )
                    )
                )
            men_profiles_amount = len(men_profiles.fetchall())

            # Количество закрытых анкет мужчин
            men_profiles = await session.execute(
                select(ProfileModel)
                    .where(
                        and_(
                            ProfileModel.gender == 'Мужчина',
                            ProfileModel.status == 'closed'
                        )
                    )
                )
            men_profiles_closed_amount = len(men_profiles.fetchall())

            # Количество анкет женщин
            women_profiles = await session.execute(
                select(ProfileModel)
                    .where(
                        and_(
                            ProfileModel.gender == 'Женщина',
                            ProfileModel.status.in_(['open', 'closed'])
                        )
                    )
                )
            women_profiles_amount = len(women_profiles.fetchall())

            # Количество закрытых анкет женщин
            women_profiles = await session.execute(
                select(ProfileModel)
                    .where(
                        and_(
                            ProfileModel.gender == 'Женщина',
                            ProfileModel.status == 'closed'
                        )
                    )
                )
            women_profiles_closed_amount = len(women_profiles.fetchall())

            return {
                'users_amount': users_amount,
                'active_profiles_amount': active_profiles_amount,
                'closed_profiles_amount': closed_profiles_amount,
                'waited_profiles_amount': waited_profiles_amount,
                'men_profiles_amount': men_profiles_amount,
                'women_profiles_amount': women_profiles_amount,
                'men_profiles_closed_amount': men_profiles_closed_amount,
                'women_profiles_closed_amount': women_profiles_closed_amount
            }

        except Exception as error:
            print(f'get_stats() error: {error}')


    # Получение статистики бота
    async def get_profile_for_verification(self, session):
        try:
            waited_blocked_profiles = await session.execute(
                select(ProfileModel)
                    .where(
                        ProfileModel.status.in_(['blocked', 'wait']),
                    )
                )
            profiles = [row for row in waited_blocked_profiles.scalars()]

            return profiles[0]

        except Exception as error:
            print(f'get_profile_for_verification() error: {error}')


    # Изсенение статуса анкеты из админки
    async def update_status_profile(self, session, profile_id, status):
        try:
            profile = await session.get(ProfileModel, profile_id)
            profile.status = status

            # Если анкеты была забанена, то пользователь тоже блокируется
            if status == 'banned':
                user = await session.get(UserModel, profile_id)
                user.ban_status = status

            # Добавление данных в бд и сохранение
            await session.commit()

        except Exception as error:
            print(f'update_status_profile() error: {error}')


    # Получение списка id людей с анкетами
    async def get_ids_with_profile(self, session):
        try:
            # Получение списка всех анкет
            profiles = await session.execute(select(ProfileModel.id))
            profile_ids = [row for row in profiles.scalars()]

            return profile_ids

        except Exception as error:
            print(f'get_users_without_profile() error: {error}')