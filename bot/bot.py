from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from bot.database import DataBase
import bot.keyboards as keyboards
import bot.messages as messages
import config

import time



bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
print('Бот запущен')


database = DataBase(config.DATABASE_URL)


# Команда /start
@dp.message(F.text.contains("/start"))
async def accept_agreement_handler(message: Message, state: FSMContext):
    await state.clear()

    start_time = time.time()

    global start_message
    start_message = await message.answer(
        messages.CHECK_BOT,
        reply_markup= keyboards.check_bot
    )

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Время выполнения функции: {execution_time} секунд")

# Проверка на бота
@dp.callback_query(F.data.contains('check_bot'))
async def check_bot_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    try:
        # Создание сессии
        async for session in database.get_session():

            # Добавление пользователя в бд
            await database.add_user(session, callback)

            # Проверка на наличие юзернейма
            if callback.from_user.username is None:
                await callback.message.answer(
                    messages.CREATE_USERNAME,
                    reply_markup= keyboards.check_username
                )
                return

            form = await database.get_form_information(session, callback.from_user.id)

        # Проверка на наличие анкеты
        if form is None:
            await callback.message.answer_video(
                video= FSInputFile('bot/design/start.mp4'),
                caption= messages.START_TEXT_NEW_USER,
                reply_markup= await keyboards.registrate(callback.from_user.id, callback.from_user.username)
            )

        # В случае наличии анкеты вход в меню
        else:
            global main_menu
            main_menu = await callback.message.answer_photo(
                photo= FSInputFile('bot/design/menu.jpeg'),
                caption= await messages.MENU_TEXT(form.status),
                reply_markup= await keyboards.menu_keyboard(form.status)
            )

        try:
            await bot.delete_message(callback.message.chat.id, start_message.message_id)
        except: pass

    except Exception as error:
        print(f'start_message error: {error}')

# # Проверка анкеты при регистрации
# @dp.message(F.web_app_data)
# async def accept_agreement(message: Message, state: FSMContext):

#     # Добавление информации о профиле в state.data
#     data_json = json.loads(message.web_app_data.data)
#     await state.update_data(data_json= data_json)
#     print(data_json)

#     # # Удаление клавиатуры
#     # await delete_reply_keyboard(message)

#     # Удаление сообщение если анкета пересоздается
#     try:
#         await bot.delete_message(message.chat.id, creation_form_message.message_id)
#     except: pass

#     await message.answer(
#         'Осталось совсем немного, отправьте фото для вашей анкеты',
#         show_alert=True
#         )
    
#     await state.set_state(Form.add_photo)
    
#     # # Вывод анкеты на проверку
#     # await message.answer(
#     #     await PREVIEW_FORM_TEXT(data_json),
#     #     reply_markup= preview_form_keyboard
#     #     )
    
# Команда /menu
@dp.message(F.text == '/menu')
async def menu_command_handler(message: Message, state: FSMContext):
    await state.clear()

    # Создание сессии
    async for session in database.get_session():
        form = await database.get_form_information(session, message.from_user.id)

    global main_menu
    main_menu = await message.answer_photo(
        photo= FSInputFile('bot/design/menu.jpeg'),
        caption= await messages.MENU_TEXT(form.status),
        reply_markup= await keyboards.menu_keyboard(form.status)
    )

# Пересоздание профиля
@dp.callback_query(F.data.contains('menu'))
async def menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    # Создание сессии
    async for session in database.get_session():
        form = await database.get_form_information(session, callback.from_user.id)

    global main_menu
    main_menu = await callback.message.edit_media(
        media= InputMediaPhoto(
            media= FSInputFile('bot/design/menu.jpeg'),
            caption= await messages.MENU_TEXT(form.status),
            parse_mode= 'HTML'
        ),
        reply_markup= await keyboards.menu_keyboard(form.status)
    )

# Просмотр своей анкеты
@dp.callback_query(F.data == 'my_form')
async def my_form_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    try:
        # Создание сессии
        async for session in database.get_session():
            form_info = await database.get_form_information(session, callback.from_user.id)

            name = form_info.name
            age = form_info.age
            city = form_info.city
            about = form_info.about
            target = form_info.target
            photo = form_info.photos[0]

        await callback.message.edit_media(
            media= InputMediaPhoto(
                media= FSInputFile(f'photos/{photo}'),
                caption= await messages.FORM_TEXT(name, age, city, about, target),
                parse_mode= 'HTML'
            ),
            reply_markup= keyboards.under_menu_keyboard
        )

    except Exception as error:
        print(f'my_form error: {error}')

# Изменение статуса анкеты
@dp.callback_query(F.data == 'update_form_status')
async def change_status_form_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    start_time = time.time()

    # Создание сессии
    async for session in database.get_session():
        # Получение статуса анкеты
        form = await database.get_form_information(session, callback.from_user.id)

        global main_menu

        # Если анкета открыта
        if form.status == 'open':
            new_status = 'closed'

            await database.update_status(session, form, new_status)

            main_menu = await callback.message.edit_caption(
                caption= await messages.MENU_TEXT(new_status),
                reply_markup= await keyboards.menu_keyboard(new_status)
            )

        # Если анкета закрыта
        elif form.status == 'closed':
            new_status = 'open'

            await database.update_status(session, form, new_status)

            main_menu = await callback.message.edit_caption(
                caption= await messages.MENU_TEXT(new_status),
                reply_markup= await keyboards.menu_keyboard(new_status)
            )

        # Если анкета не подтверждена
        elif form.status == 'wait':
            await callback.answer(
                'Ваша анкета еще не подтверждена',
                show_alert= True
            )

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Время выполнения функции: {execution_time} секунд")

# Бонусы
@dp.callback_query(F.data == 'bonuses')
async def bonuses_handler(callback: CallbackQuery, state: FSMContext):

    await state.clear()

    await callback.answer(
        'Этот раздел находится в разработке',
        show_alert=True
    )

# Пересоздание анкеты
@dp.callback_query(F.data == 'recreate_form')
async def recreate_form_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.edit_media(
        media= InputMediaPhoto(
            media= FSInputFile('bot/design/recreate_form.jpeg'),
            caption= messages.RECREATE_FORM_TEXT,
            parse_mode= 'HTML'
        ),
        reply_markup= await keyboards.recreate_keyboard(callback.from_user.id, callback.from_user.username)
    )

# Проверка юзернейма
@dp.callback_query(F.data.contains('check_username'))
async def check_username_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    # Создание сессии
    async for session in database.get_session():
        # Проверка на наличие юзернейма
        if callback.from_user.username is None:
            await callback.answer(
                messages.CREATE_USERNAME,
                show_alert= True
            )
        else:
            await database.update_username(session, callback.from_user.id, callback.from_user.username)

            form = await database.get_form_information(session, callback.from_user.id)

            # Проверка на наличие анкеты
            if form is None:
                await callback.message.answer(
                    messages.START_TEXT_NEW_USER,
                    reply_markup= await keyboards.registrate(callback.from_user.id, callback.from_user.username)
                )

            # В случае наличии анкеты вход в меню
            else:
                global main_menu
                main_menu = await callback.message.answer(
                    await messages.MENU_TEXT(form.status),
                    reply_markup= await keyboards.menu_keyboard(form.status)
                )



# Вывод анкеты при лайке
@dp.callback_query(F.data.contains('check_form_who_liked_me'))
async def check_form_who_liked_me(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    # Получение id анкеты, того кто лайкнул
    form_id = callback.data.split()[1]

    # Если лайк взаимный то сразу выводится сообщение с ссылкой
    try:
        mutual = callback.data.split()[2]
    except: 
        mutual = None

    # Создание сессии
    async for session in database.get_session():
        try:
            form = await database.get_form_information(session, form_id)

            if mutual == 'mutual':
                name = form.name
                age = form.age
                city = form.city
                about = form.about
                target = form.target
                photo = form.photos[0]
                url = form.username

                await callback.message.edit_media(
                    media= InputMediaPhoto(
                        media= FSInputFile(f'photos/{photo}'),
                        caption= f'Взаимный лайк ❤️\n\n{await messages.FORM_TEXT(name, age, city, about, target)}\n\nНачинайте общение: @{url}',
                        parse_mode= 'HTML'
                    ),
                    reply_markup= None
                )

            else:
                name = form.name
                age = form.age
                city = form.city
                about = form.about
                target = form.target
                photo = form.photos[0]

                # Проверка на число фото больше одного
                if len(form.photos) != 1:
                    more_photo = True
                else:
                    more_photo = False

                await callback.message.edit_media(
                    media= InputMediaPhoto(
                        media= FSInputFile(f'photos/{photo}'),
                        caption= await messages.FORM_TEXT(name, age, city, about, target),
                        parse_mode= 'HTML'
                    ),
                    reply_markup= await keyboards.form_after_like_keyboard(form_id, more_photo= more_photo)
                )

        except Exception as error:
            print(f'check_form_who_liked_me error: {error}')

# Вывод анкет при поиске
@dp.callback_query(F.data.contains('who_liked_me'))
async def who_liked_me(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    mark = callback.data.split()[1]
    form_id = callback.data.split()[2]

    # Создание сессии
    async for session in database.get_session():
        try:
            await database.like_or_dislike_form(session, str(callback.from_user.id), form_id, mark)
            if mark == 'like':
                form = await database.get_form_information(session, form_id)
                url = form.username

                # Изменение описания, получение ссылки человека
                await callback.message.edit_caption(
                    caption= f'Вам понравилась эта анкета ❤️\n\n{callback.message.caption}\n\nНачинайте общение: @{url}',
                    parse_mode= 'HTML',
                    reply_markup= None
                )

                # Отправка человеку сообщения о взаимном лайке
                await bot.send_photo(
                    chat_id= form_id,
                    photo= FSInputFile('bot/design/mutual_like.jpeg'),
                    caption= 'У вас взаимный лайк 😍',
                    reply_markup= await keyboards.show_form_keyboard(callback.from_user.id, 'mutual')
                )

            else:
                await callback.message.edit_caption(
                    caption= f'Вам не понравилась эта анкета 💔\n\n{callback.message.caption}',
                    reply_markup= None
                )

        except Exception as error:
            print(f'who_liked_me error: {error}')

# Вывод анкет при поиске
@dp.callback_query(F.data == 'check_forms')
async def check_forms_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    start_time = time.time()

    # Создание сессии
    async for session in database.get_session():
        try:
            # Получение id подходящей по параметрам анкеты
            my_form = await database.get_form_information(session, callback.from_user.id)
            form = await database.get_form_id_by_filters(session, my_form)

            if form is not None:
                print(form.id)

                # Проверка на число фото больше одного
                if len(form.photos) != 1:
                    more_photo = True
                else:
                    more_photo = False

                await callback.message.answer_photo(
                    photo= FSInputFile(f'photos/{form.photos[0]}'),
                    caption= await messages.FORM_TEXT(form.name, form.age, form.city, form.about, form.target),
                    parse_mode='HTML',
                    reply_markup= await keyboards.form_keyboard(form.id, more_photo= more_photo)
                )

                try:
                    await bot.delete_message(callback.message.chat.id, main_menu.message_id)
                except:
                    # Если сообщение не удалилось, то пустой ответ чтобы кнопка не мигала
                    await callback.answer()

            else:
                await callback.answer(
                    'Подходящих для вас анкет, к сожалению, нет',
                    show_alert= True
                )

        except Exception as error:
            print(f'check_forms error: {error}')
            await callback.answer(
                f'Ошибка: {error}',
                show_alert= True
            )

        # try:
        #     # Если при листании анкет они кончились, то выводится меню
        #     if mark:
        #         form_info = await database.get_form_information(callback.from_user.id)
        #         status = form_info['status']

        #         main_menu = await callback.message.answer_photo(
        #             photo= FSInputFile('design/menu.jpeg'),
        #             caption= await MENU_TEXT(status),
        #             reply_markup= await menu_keyboard(status)
        #         )
        # except: pass

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Время выполнения функции: {execution_time} секунд")

# Лайк/дизлайк
@dp.callback_query(F.data.contains('rate'))
async def like_dislike_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    # Создание сессии
    async for session in database.get_session():
        # Получение оценки
        try:
            mark = callback.data.split()[1]
            form_id = callback.data.split()[2]
            await database.like_or_dislike_form(session, callback.from_user.id, form_id, mark)

            if mark == 'like':
                # К тексту анкеты добавляется оценка и убирается клавиатура
                await callback.message.edit_caption(
                    caption= f'Вы лайкнули эту анкету ❤️\n\n{callback.message.caption}',
                    reply_markup= None
                )

                # Уведомление пользователю о лайке
                await bot.send_photo(
                    chat_id= form_id,
                    photo= FSInputFile('bot/design/like.jpeg'),
                    caption= 'Ваша анкета понравилась одному человеку 🤗',
                    reply_markup= await keyboards.show_form_keyboard(callback.from_user.id)
                )

            elif mark == 'dislike':
                # К тексту анкеты добавляется оценка и убирается клавиатура
                await callback.message.edit_caption(
                    caption= f'Вам не понравилась эта анкета 💔\n\n{callback.message.caption}',
                    reply_markup= None
                )

        except Exception as error:
            print(f'like/dislike error: {error}')

    # Показ новой анкеты
    await check_forms_handler(callback, state)

            
# Жалоба
@dp.callback_query(F.data.contains('warn'))
async def warn_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    # Создание сессии
    async for session in database.get_session():
        
        try:
            form_id = callback.data.split()[1]
            await database.make_warn(session, form_id)

            await callback.answer(
                messages.MAKE_WARN,
                show_alert= True
            )

            try:
                await bot.delete_message(callback.message.chat.id, callback.message.message_id)
            except: pass

        except Exception as error:
            print(f'make warn error: {error}')

    # Показ новой анкеты
    await check_forms_handler(callback, state)

# Листание фото
@dp.callback_query(F.data.contains('check_photo'))
async def check_photo_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    # Создание сессии
    async for session in database.get_session():
        
        try:
            form_id = callback.data.split()[1]
            photo_num = int(callback.data.split()[2])

            form = await database.get_form_information(session, form_id)

            # Если есть еще фото, то порядковый номер увеличивается
            if len(form.photos) == photo_num + 1:
                next_photo_num = 0
            else:
                next_photo_num = photo_num + 1

            await callback.message.edit_media(
                media= InputMediaPhoto(
                    media= FSInputFile(f'photos/{form.photos[photo_num]}'),
                    caption= await messages.FORM_TEXT(form.name, form.age, form.city, form.about, form.target),
                    parse_mode='HTML'
                ), 
                reply_markup= await keyboards.form_keyboard(form.id, more_photo= True, next_photo_num= next_photo_num)
            )

        except Exception as error:
            print(f'check photo error: {error}')



# Обработка прочих сообщений
@dp.message()
async def echo(message: Message):
    await message.answer('Воспользуйтесь командами или клавиатурой, а если что-то пошло не так, воспользуйся командой /start, чтобы перезапустить бота')


# Запуск бота
async def main():
    # Запуск бота
    await dp.start_polling(bot)