from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from pyrepka import PyRepka

from bot.database import DataBase
import bot.keyboards as keyboards
import bot.messages as messages
import bot.admin_panel as admin_panel
import bot.starting as starting
import config


bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
dp.include_routers(admin_panel.router_admin, starting.router_starting)
print('Бот запущен')


database = DataBase(config.DATABASE_URL)
referral_program = PyRepka(config.REFERRAL_TOKEN, config.BOT_USERNAME, config.REFERRAL_IP, config.REFERRAL_PORT)


# Команда /menu
@dp.message(F.text == '/menu')
async def menu_command_handler(message: Message, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Проверка на наличие юзернейма
    if message.from_user.username is None:
        await message.answer(
            messages.CREATE_USERNAME,
            reply_markup= keyboards.check_username
        )
        return

    # Создание сессии
    try:
        async for session in database.get_session():
            # Получение данных об анкете
            profile = await database.get_profile_information(session, message.from_user.id)

            # Получение данных о пользователе
            user = await database.get_user_information(session, message.from_user.id)

    except Exception as error:
        print(f'menu_command_handler() Session error: {error}')

    try:
        # Проверка на наличие анкеты
        if profile:
            # Проверка на бан
            if profile.status == 'banned':
                await message.answer(messages.BANNED)
                return
            
            elif profile.status == 'canceled':
                await message.answer(
                    messages.CANCELED,
                    reply_markup= await keyboards.recreate_keyboard(message.from_user.id, message.from_user.username)
                )
                return
            
        # Если анкеты нет
        else:
            await message.answer(
                messages.NO_PROFILE,
                reply_markup= await keyboards.registrate(message.from_user.id, message.from_user.username)
            )
            return


        global main_menu
        main_menu = await message.answer_photo(
            photo= FSInputFile('bot/design/menu.jpeg'),
            caption= await messages.MENU_TEXT(profile.status, user.sub_status, user.sub_end_date),
            reply_markup= await keyboards.menu_keyboard(profile.status),
            parse_mode= 'HTML'
        )
    except Exception as error:
        print(f'menu_command_handler() error: {error}')


# Пересоздание профиля
@dp.callback_query(F.data == 'menu')
async def menu_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Создание сессии
    try:
        async for session in database.get_session():
            # Получение данных об анкете
            profile = await database.get_profile_information(session, callback.from_user.id)

            # Получение данных о пользователе
            user = await database.get_user_information(session, callback.from_user.id)

    except Exception as error:
        print(f'menu_handler() Session error: {error}')

    try:
        # Проверка на бан
        if profile.status == 'banned':
            await callback.answer(
                messages.BANNED,
                show_alert= True
            )
            return
        
        elif profile.status == 'canceled':
            await callback.answer(
                messages.CANCELED,
                show_alert= True
            )
            return

        global main_menu
        main_menu = await callback.message.edit_media(
            media= InputMediaPhoto(
                media= FSInputFile('bot/design/menu.jpeg'),
                caption= await messages.MENU_TEXT(profile.status, user.sub_status, user.sub_end_date),
                parse_mode= 'HTML'
            ),
            reply_markup= await keyboards.menu_keyboard(profile.status)
        )
    except Exception as error:
        print(f'menu_handler() error: {error}')


# Просмотр своей анкеты
@dp.callback_query(F.data == 'my_profile')
async def my_profile_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Создание сессии
    try:
        async for session in database.get_session():
            # Получение данных об анкете
            profile = await database.get_profile_information(session, callback.from_user.id)

            # Проверка на бан
            if profile.status == 'banned':
                await callback.answer(
                    messages.BANNED,
                    show_alert= True
                )
                return

    except Exception as error:
        print(f'my_profile_handler() Session error: {error}')

    try:
        name = profile.name
        age = profile.age
        city = profile.city
        about = profile.about
        target = profile.target
        photo = profile.photos[0]

        # Проверка на число фото больше одного
        if len(profile.photos) != 1:
            more_photo = True
        else:
            more_photo = False

        await callback.message.edit_media(
            media= InputMediaPhoto(
                media= FSInputFile(f'photos/{photo}'),
                caption= await messages.PROFILE_TEXT(name, age, city, about, target),
                parse_mode= 'HTML'
            ),
            reply_markup= await keyboards.my_profile_keyboard(callback.from_user.id, callback.from_user.username, more_photo= more_photo)
        )

    except Exception as error:
        print(f'my_profile_handler() error: {error}')


# Команда /myprofile
@dp.message(F.text == '/myprofile')
async def myprofile_command_handler(message: Message, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Проверка на наличие юзернейма
    if message.from_user.username is None:
        await message.answer(
            messages.CREATE_USERNAME,
            reply_markup= keyboards.check_username
        )
        return

    # Создание сессии
    try:
        async for session in database.get_session():
            # Получение данных об анкете
            profile = await database.get_profile_information(session, message.from_user.id)

            # Проверка на наличие анкеты
            if profile:
                # Проверка на бан
                if profile.status == 'banned':
                    await message.answer(messages.BANNED)
                    return
                
                elif profile.status == 'canceled':
                    await message.answer(
                        messages.CANCELED,
                        reply_markup= await keyboards.recreate_keyboard(message.from_user.id, message.from_user.username)
                    )
                    return
                
            # Если анкеты нет
            else:
                await message.answer(
                    messages.NO_PROFILE,
                    reply_markup= await keyboards.registrate(message.from_user.id, message.from_user.username)
                )
                return

    except Exception as error:
        print(f'myprofile_command_handler() Session error: {error}')

    try:
        name = profile.name
        age = profile.age
        city = profile.city
        about = profile.about
        target = profile.target
        photo = profile.photos[0]

        # Проверка на число фото больше одного
        if len(profile.photos) != 1:
            more_photo = True
        else:
            more_photo = False

        await message.answer_photo(
            photo= FSInputFile(f'photos/{photo}'),
            caption= await messages.PROFILE_TEXT(name, age, city, about, target),
            parse_mode= 'HTML',
            reply_markup= await keyboards.my_profile_keyboard(message.from_user.id, message.from_user.username, more_photo= more_photo)
        )

    except Exception as error:
        print(f'myprofile_command_handler() error: {error}')


# Листание фото
@dp.callback_query(F.data.contains('my_photo_check'))
async def my_photo_check_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    profile_id = callback.data.split()[1]
    photo_num = int(callback.data.split()[2])

    # Создание сессии
    try:
        async for session in database.get_session():
            profile = await database.get_profile_information(session, profile_id)
    except Exception as error:
        print(f'my_photo_check_handler() Session error: {error}')

    try:
        # Если есть еще фото, то порядковый номер увеличивается
        if len(profile.photos) == photo_num + 1:
            next_photo_num = 0
        else:
            next_photo_num = photo_num + 1

        await callback.message.edit_media(
            media= InputMediaPhoto(
                media= FSInputFile(f'photos/{profile.photos[photo_num]}'),
                caption= await messages.PROFILE_TEXT(profile.name, profile.age, profile.city, profile.about, profile.target),
                parse_mode='HTML'
            ), 
            reply_markup= await keyboards.my_profile_keyboard(callback.from_user.id, callback.from_user.username, more_photo= True, next_photo_num= next_photo_num)
        )
    except Exception as error:
        print(f'my_photo_check_handler() error: {error}')


# Команда /profiles
@dp.message(F.text == '/profiles')
async def profiles_command_handler(message: Message, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Проверка на наличие юзернейма
    if message.from_user.username is None:
        await message.answer(
            messages.CREATE_USERNAME,
            reply_markup= keyboards.check_username
        )
        return

    # Создание сессии
    try:
        async for session in database.get_session():

            # Получение данных о своей анкете
            my_profile = await database.get_profile_information(session, message.from_user.id)

            # Проверка на наличие анкеты
            if my_profile:
                if my_profile.status == 'wait':
                    await message.answer(messages.WAITED)
                    return

                elif my_profile.status == 'closed':
                    await message.answer(messages.CLOSED)
                    return

                elif my_profile.status == 'blocked':
                    await message.answer(messages.BLOCKED)
                    return

                elif my_profile.status == 'banned':
                    await message.answer(messages.BANNED)
                    return
                
                elif my_profile.status == 'canceled':
                    await message.answer(
                        messages.CANCELED,
                        reply_markup= await keyboards.recreate_keyboard(message.from_user.id, message.from_user.username)
                    )
                    return

                # Получение id подходящей по параметрам анкеты
                profile = await database.get_profile_id_by_filters(session, my_profile)
            
            # Если анкеты нет
            else:
                await message.answer(
                    messages.NO_PROFILE,
                    reply_markup= await keyboards.registrate(message.from_user.id, message.from_user.username)
                )
                return

    except Exception as error:
        print(f'profiles_command_handler() Session error: {error}')
        await message.answer(f'Ошибка: {error}')

    try:
        if profile is not None:

            # Проверка на число фото больше одного
            if len(profile.photos) != 1:
                more_photo = True
            else:
                more_photo = False

            await message.answer_photo(
                photo= FSInputFile(f'photos/{profile.photos[0]}'),
                caption= await messages.PROFILE_TEXT(profile.name, profile.age, profile.city, profile.about, profile.target),
                parse_mode='HTML',
                reply_markup= await keyboards.profile_keyboard(profile.id, more_photo= more_photo)
            )

        # Если нет подходящей анкеты
        else:
            await message.answer(
                messages.NO_PROFILES,
                show_alert= True
            )

    except Exception as error:
        print(f'profiles_command_handler() error: {error}')
        await message.answer(f'Ошибка: {error}')


# Изменение статуса анкеты
@dp.callback_query(F.data == 'update_profile_status')
async def change_status_profile_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Создание сессии
    try:
        async for session in database.get_session():
            # Получение статуса анкеты
            profile = await database.get_profile_information(session, callback.from_user.id)

            # Получение данных о пользователе
            user = await database.get_user_information(session, callback.from_user.id)

            # Если анкета открыта
            if profile.status == 'open':
                new_status = 'closed'
                await database.update_status(session, profile, new_status)

            # Если анкета закрыта
            elif profile.status == 'closed':
                new_status = 'open'
                await database.update_status(session, profile, new_status)

            # Если анкета забанена
            elif profile.status == 'banned':
                await callback.answer(
                    messages.BANNED,
                    show_alert= True
                )
                return
            
            # Если анкета не подтверждена
            elif profile.status == 'wait':
                await callback.answer(
                    messages.WAITED,
                    show_alert= True
                )
                return
            
            # Если анкета заморожена
            elif profile.status == 'blocked':
                await callback.answer(
                    messages.BLOCKED,
                    show_alert= True
                )
                return

    except Exception as error:
        print(f'change_status_profile_handler() Session error: {error}')

    try:
        global main_menu
        main_menu = await callback.message.edit_caption(
            caption= await messages.MENU_TEXT(new_status, user.sub_status, user.sub_end_date),
            reply_markup= await keyboards.menu_keyboard(new_status),
            parse_mode= 'html'
        )
    except Exception as error:
        print(f'change_status_profile_handler() error: {error}')


# Пересоздание анкеты
@dp.callback_query(F.data == 'recreate_profile')
async def recreate_profile_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Создание сессии
    try:
        async for session in database.get_session():
            # Получение статуса анкеты
            profile = await database.get_profile_information(session, callback.from_user.id)

            # Если анкета забанена
            if profile.status == 'banned':
                await callback.answer(
                    messages.BANNED,
                    show_alert= True
                )
                return
            # Если анкета заморожена
            elif profile.status == 'blocked':
                await callback.answer(
                    messages.BLOCKED,
                    show_alert= True
                )
                return
    except Exception as error:
        print(f'recreate_profile_handler() Session error: {error}')

    try:
        await callback.message.edit_media(
            media= InputMediaPhoto(
                media= FSInputFile('bot/design/recreate_profile.jpeg'),
                caption= messages.RECREATE_PROFILE_TEXT,
                parse_mode= 'HTML'
            ),
            reply_markup= await keyboards.recreate_keyboard(callback.from_user.id, callback.from_user.username)
        )
    except Exception as error:
        print(f'recreate_profile_handler() error: {error}')


# Проверка юзернейма
@dp.callback_query(F.data.contains('check_username'))
async def check_username_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Создание сессии
    try:
        async for session in database.get_session():
            # Получение данных об анкете
            profile = await database.get_profile_information(session, callback.from_user.id)

            # Проверка на наличие анкеты
            if profile:
                # Если анкета забанена
                if profile.status == 'banned':
                    await callback.answer(
                        messages.BANNED,
                        show_alert= True
                    )
                    return

            # Проверка на наличие юзернейма
            if callback.from_user.username is None:
                await callback.answer(
                    messages.CREATE_USERNAME,
                    show_alert= True
                )
                return
            
            else:
                # Добавление пользователя в бд
                if await database.add_user(session, callback):
                    # Если новый пользователь, то уведомление админам
                    stats = await database.get_stats(session)
                    users_amount = stats['users_amount']
                    await database.notify_admins(
                        session,
                        bot,
                        message_text= f'🆕 Новый пользователь\nUsername: @{callback.from_user.username}\nВсего пользователей: {users_amount}'
                    )

                    # Обновление юзернейма
                    await database.update_username(session, callback.from_user.id, callback.from_user.username)

                    # Получение данных о пользователе
                    user = await database.get_user_information(session, callback.from_user.id)

    except Exception as error:
        print(f'check_username_handler() Session error: {error}')

    try:
        # Проверка на наличие анкеты
        if profile is None:
            await callback.message.answer(
                messages.START_TEXT_NEW_USER,
                reply_markup= await keyboards.registrate(callback.from_user.id, callback.from_user.username),
                parse_mode= 'html'
            )

        # В случае наличии анкеты вход в меню
        else:
            global main_menu
            main_menu = await callback.message.answer(
                await messages.MENU_TEXT(profile.status, user.sub_status, user.sub_end_date),
                reply_markup= await keyboards.menu_keyboard(profile.status)
            )
    except Exception as error:
        print(f'check_username_handler() error: {error}')


# Вывод анкеты при лайке
@dp.callback_query(F.data.contains('check_profile_who_liked_me'))
async def check_profile_who_liked_me(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Получение id анкеты, того кто лайкнул
    profile_id = callback.data.split()[1]

    # Если лайк взаимный то сразу выводится сообщение с ссылкой
    try:
        mutual = callback.data.split()[2]
    except: 
        mutual = None

    # Создание сессии
    try:
        async for session in database.get_session():
            # Получение данных об анкете
            profile = await database.get_profile_information(session, profile_id)
            my_profile = await database.get_profile_information(session, callback.from_user.id)

            # Если анкета забанена
            if my_profile.status == 'banned':
                await callback.answer(
                    messages.BANNED,
                    show_alert= True
                )
                return

    except Exception as error:
        print(f'check_profile_who_liked_me() Session error: {error}')

    try:
        name = profile.name
        age = profile.age
        city = profile.city
        about = profile.about
        target = profile.target
        photo = profile.photos[0]

        if mutual == 'mutual':
            await callback.message.edit_media(
                media= InputMediaPhoto(
                    media= FSInputFile(f'photos/{photo}'),
                    caption= await messages.MUTUAL_LIKE_PREVIEW(profile),
                    parse_mode= 'HTML'
                ),
                reply_markup= None
            )

        else:
            # Проверка на число фото больше одного
            if len(profile.photos) != 1:
                more_photo = True
            else:
                more_photo = False

            await callback.message.edit_media(
                media= InputMediaPhoto(
                    media= FSInputFile(f'photos/{photo}'),
                    caption= await messages.PROFILE_TEXT(name, age, city, about, target),
                    parse_mode= 'HTML'
                ),
                reply_markup= await keyboards.profile_after_like_keyboard(profile_id, more_photo= more_photo)
            )

    except Exception as error:
        print(f'check_profile_who_liked_me() error: {error}')


# Вывод анкет при поиске
@dp.callback_query(F.data.contains('who_liked_me'))
async def who_liked_me(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    mark = callback.data.split()[1]
    profile_id = callback.data.split()[2]

    # Создание сессии
    try:
        async for session in database.get_session():
            # Получение данных об анкете
            my_profile = await database.get_profile_information(session, callback.from_user.id)

            # Если анкета забанена
            if my_profile.status == 'banned':
                await callback.answer(
                    messages.BANNED,
                    show_alert= True
                )
                return

            await database.like_or_dislike_profile(session, str(callback.from_user.id), profile_id, mark)

            # Если поставил лайк, то получение юзернейма
            if mark == 'like':
                profile = await database.get_profile_information(session, profile_id)
                url = profile.username

    except Exception as error:
        print(f'who_liked_me() Session error: {error}')

    try:
        if mark == 'like':
            # Изменение описания, получение ссылки человека
            await callback.message.edit_caption(
                caption= f'Вам понравилась эта анкета ❤️\n\n{callback.message.caption}\n\nНачинайте общение: @{url}',
                parse_mode= 'HTML',
                reply_markup= None
            )

            # Отправка человеку сообщения о взаимном лайке
            await bot.send_photo(
                chat_id= profile_id,
                photo= FSInputFile('bot/design/mutual_like.jpeg'),
                caption= messages.MUTUAL_LIKE,
                reply_markup= await keyboards.show_profile_keyboard(callback.from_user.id, 'mutual')
            )

        else:
            await callback.message.edit_caption(
                caption= f'Вам не понравилась эта анкета 💔\n\n{callback.message.caption}',
                reply_markup= None
            )

    except Exception as error:
        print(f'who_liked_me() error: {error}')


# Вывод анкет при поиске
@dp.callback_query(F.data.contains('check_profiles'))
async def check_profiles_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Создание сессии
    try:
        async for session in database.get_session():
            # Получение данных о своей анкете
            my_profile = await database.get_profile_information(session, callback.from_user.id)

            # Получение данных о пользователе
            user = await database.get_user_information(session, callback.from_user.id)

            if my_profile.status == 'wait':
                await callback.answer(
                    messages.WAITED,
                    show_alert= True
                )
                return

            elif my_profile.status == 'closed':
                await callback.answer(
                    messages.CLOSED,
                    show_alert= True
                )
                return

            elif my_profile.status == 'blocked':
                await callback.answer(
                    messages.BLOCKED,
                    show_alert= True
                )
                return

            elif my_profile.status == 'banned':
                await callback.answer(
                    messages.BANNED,
                    show_alert= True
                )
                return

            elif my_profile.status == 'canceled':
                await callback.answer(
                    messages.CANCELED,
                    show_alert= True
                )
                return

            # Получение id подходящей по параметрам анкеты
            profile = await database.get_profile_id_by_filters(session, my_profile)

    except Exception as error:
        print(f'check_profiles_handler Session error: {error}')
        await callback.answer(
            f'Ошибка: {error}',
            show_alert= True
        )

    try:
        if profile is not None:

            # Проверка на число фото больше одного
            if len(profile.photos) != 1:
                more_photo = True
            else:
                more_photo = False

            await callback.message.answer_photo(
                photo= FSInputFile(f'photos/{profile.photos[0]}'),
                caption= await messages.PROFILE_TEXT(profile.name, profile.age, profile.city, profile.about, profile.target),
                parse_mode='HTML',
                reply_markup= await keyboards.profile_keyboard(profile.id, more_photo= more_photo)
            )

            try:
                await bot.delete_message(callback.message.chat.id, main_menu.message_id)
            except:
                # Если сообщение не удалилось, то пустой ответ чтобы кнопка не мигала
                await callback.answer()

        # Если нет подходящей анкеты
        else:
            await callback.answer(
                messages.NO_PROFILES,
                show_alert= True
            )

            # global main_menu
            if callback.data.split()[1] != 'from_menu':
                main_menu = await callback.message.answer_photo(
                    photo= FSInputFile('bot/design/menu.jpeg'),
                    caption= await messages.MENU_TEXT(my_profile.status, user.sub_status, user.sub_end_date),
                    reply_markup= await keyboards.menu_keyboard(my_profile.status),
                    parse_mode= 'html'
                )

    except Exception as error:
        print(f'check_profiles_handler error: {error}')
        await callback.answer(
            f'Ошибка: {error}',
            show_alert= True
        )


# Просмотр суперлайка
@dp.callback_query(F.data.contains('superlike_preview'))
async def superlike_preview_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Получение оценки
    mark = callback.data.split()[1]
    profile_id = callback.data.split()[2]

    try:
        # Получение баланса пользователя
        balance = referral_program.get_user_balance(callback.from_user.id)

        # Всплывающее окно с описанием суперлайка
        await callback.answer(
            await messages.SUPERLIKE_ABOUT(balance.text),
            show_alert=True
        )

        # Изменение клавиатуры под анкетой с предложением оплатить суперлайк
        await callback.message.edit_caption(
            caption= callback.message.caption,
            reply_markup= await keyboards.superlike_keyboard(profile_id),
            caption_entities= callback.message.caption_entities
        )
    except Exception as error:
        print(f'superlike_preview_handler() error: {error}')


# Лайк/дизлайк
@dp.callback_query(F.data.contains('rate'))
async def like_dislike_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Получение оценки
    mark = callback.data.split()[1]
    profile_id = callback.data.split()[2]

    # Создание сессии
    try:
        async for session in database.get_session():
            # Если суперлайк
            if mark == 'superlike':
                # Списывание денег за суперлайк
                response = referral_program.purchase(callback.from_user.id, config.SUPERLIKE_PRICE, 'Тест суперлайка')

                # Проверка ответа на списывание денег за суперлайк
                if response.status_code == 200:
                    # В случае успешной оплаты добавление оценки в бд
                    await database.like_or_dislike_profile(session, callback.from_user.id, profile_id, mark)

                    # Пополнение баланса тому, кому ставят лайк
                    referral_program.replenishment(profile_id, config.SUPERLIKE_PRICE, 'Суперлайк')

                    # Получение данных о своей анкете
                    my_profile = await database.get_profile_information(session, callback.from_user.id)

                else:
                    # В случае ошибки вывод сообщения о нехватке средств
                    await callback.answer(
                        messages.NO_MONEY,
                        show_alert= True
                    )

                    # Открытие реферальной системы
                    await referral_program_handler(callback, state)
                    return
            
            # При лайке и дизлайке
            else:
                await database.like_or_dislike_profile(session, callback.from_user.id, profile_id, mark)

    except Exception as error:
        print(f'like_dislike_handler() Session error: {error}')

    try:
        # Лайк
        if mark == 'like':
            # К тексту анкеты добавляется оценка и убирается клавиатура
            await callback.message.edit_caption(
                caption= f'Вы лайкнули эту анкету ❤️\n\n{callback.message.caption}',
                reply_markup= None
            )

            # Уведомление пользователю о лайке
            await bot.send_photo(
                chat_id= profile_id,
                photo= FSInputFile('bot/design/like.jpeg'),
                caption= messages.YOU_LIKED,
                reply_markup= await keyboards.show_profile_keyboard(callback.from_user.id)
            )

        # Суперлайк
        elif mark == 'superlike':
            # К тексту анкеты добавляется оценка и убирается клавиатура
            await callback.message.edit_caption(
                caption= f'Вы поставили суперлайк 💖\n\n{callback.message.caption}',
                reply_markup= None
            )

            # Уведомление пользователю о суперлайке
            await bot.send_photo(
                chat_id= profile_id,
                photo= FSInputFile(f'photos/{my_profile.photos[0]}'),
                caption= f'<b>🎁 Пришел подарок!</b> Этот пользователь поставил вам 💖 суперлайк. Вам начислено {config.SUPERLIKE_PRICE} р. на баланс репки. Вы можете написать @{my_profile.username} и отблагодарить!\nБаланс репки пополнен на {config.SUPERLIKE_PRICE}р.\n\n{await messages.PROFILE_TEXT(my_profile.name, my_profile.age, my_profile.city, my_profile.about, my_profile.target)}',
                parse_mode= 'HTML'
            )

        # Дизлайк/Далее
        elif mark == 'dislike':
            # К тексту анкеты добавляется оценка и убирается клавиатура
            await callback.message.edit_caption(
                caption= f'Вам не понравилась эта анкета 💔\n\n{callback.message.caption}',
                reply_markup= None
            )

    except Exception as error:
        print(f'like_dislike_handler() error: {error}')

    # Показ новой анкеты
    await check_profiles_handler(callback, state)


# Листание фото
@dp.callback_query(F.data.contains('check_photo'))
async def check_photo_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    await callback.answer('⏳ Загрузка')

    profile_id = callback.data.split()[1]
    photo_num = int(callback.data.split()[2])

    # Создание сессии
    try:
        async for session in database.get_session():
            profile = await database.get_profile_information(session, profile_id)
    except Exception as error:
        print(f'check_photo_handler() Session error: {error}')

    try:
        # Если есть еще фото, то порядковый номер увеличивается
        if len(profile.photos) == photo_num + 1:
            next_photo_num = 0
        else:
            next_photo_num = photo_num + 1

        await callback.message.edit_media(
            media= InputMediaPhoto(
                media= FSInputFile(f'photos/{profile.photos[photo_num]}'),
                caption= callback.message.caption,
                # caption= await messages.PROFILE_TEXT(profile.name, profile.age, profile.city, profile.about, profile.target),
                parse_mode='HTML'
            ), 
            reply_markup= await keyboards.profile_keyboard(profile.id, more_photo= True, next_photo_num= next_photo_num)
        )
    except Exception as error:
        print(f'check_photo_handler() error: {error}')


# Команда /referrals
@dp.message(F.text == '/referrals')
async def referrals_command_handler(message: Message, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Проверка на наличие юзернейма
    if message.from_user.username is None:
        await message.answer(
            messages.CREATE_USERNAME,
            reply_markup= keyboards.check_username
        )
        return
    
    # Создание сессии
    try:
        async for session in database.get_session():
            # Получение данных об анкете
            profile = await database.get_profile_information(session, message.from_user.id)

    except Exception as error:
        print(f'menu_command_handler() Session error: {error}')
    
    try:
        # Добавление в реферальную систему (Репка)
        print(referral_program.add_user_to_ref(
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.last_name,
            message.from_user.username
        ))

        # Проверка на наличие анкеты
        if profile:
            # Проверка на бан
            if profile.status == 'banned':
                await message.answer(messages.BANNED)
                return

            elif profile.status == 'canceled':
                await message.answer(
                    messages.CANCELED,
                    reply_markup= await keyboards.recreate_keyboard(message.from_user.id, message.from_user.username)
                )
                return

        # Если анкеты нет
        else:
            await message.answer(
                messages.NO_PROFILE,
                reply_markup= await keyboards.registrate(message.from_user.id, message.from_user.username)
            )
            return

        referral_data = referral_program.get_referral_users(message.from_user.id)

        await message.answer_photo(
            photo= FSInputFile(f'bot/design/referral_program.jpeg'),
            caption= await messages.REFERRAL_PROGRAM(message.from_user.id, referral_data.json()),
            parse_mode='HTML',
            reply_markup= keyboards.referrals_keyboard
        )
    except Exception as error:
        print(f'referral_program_handler() error: {error}')
    

# Реферальная программа
@dp.callback_query(F.data == 'referral_program')
async def referral_program_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    try:
        # Добавление в реферальную систему (Репка)
        referral_program.add_user_to_ref(
            callback.from_user.id,
            callback.from_user.first_name,
            callback.from_user.last_name,
            callback.from_user.username
        )

        referral_data = referral_program.get_referral_users(callback.from_user.id)

        await callback.message.edit_media(
            media= InputMediaPhoto(
                media= FSInputFile(f'bot/design/referral_program.jpeg'),
                caption= await messages.REFERRAL_PROGRAM(callback.from_user.id, referral_data.json()),
                parse_mode='HTML'
            ),
            reply_markup= keyboards.referrals_keyboard
        )
    except Exception as error:
        print(f'referral_program_handler() error: {error}')


# Подробнее о репке
@dp.callback_query(F.data == 'repka_about')
async def repka_about_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    try:
        await callback.message.edit_caption(
            caption= messages.REPKA_INFO,
            parse_mode= 'html',
            reply_markup= keyboards.repka_keyboard
        )
    except Exception as error:
        print(f'referral_program_handler() error: {error}')


# Пригласительное письмо
@dp.callback_query(F.data == 'invite')
async def referral_program_invite_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    try:
        await callback.message.answer(
            await messages.REFERRAL_INVITE(callback.from_user.id),
            parse_mode= 'HTML'
        )

        await callback.answer(
            'Отправь это сообщение своим друзьям!',
            show_alert= True
        )
    except Exception as error:
        print(f'referral_program_invite_handler() error: {error}')


# Команда /support
@dp.message(F.text == '/support')
async def support(message: Message, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()
    await message.answer(messages.SUPPORT_TEXT)


# Команда /corbots
@dp.message(F.text == '/corbots')
async def corbots(message: Message, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    await message.answer_photo(
        photo= FSInputFile('bot/design/corbots.jpeg'),
        caption= messages.CORBOTS_TEXT,
        parse_mode= 'HTML',
        reply_markup= keyboards.corbots_keyboard
    )


# Запуск бота
async def main():
    # Запуск бота
    await dp.start_polling(bot)