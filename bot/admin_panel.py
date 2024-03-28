from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from bot.database import DataBase
import bot.keyboards as keyboards
import bot.messages as messages
import config


bot = Bot(token=config.BOT_TOKEN)
router_admin = Router()

database = DataBase(config.DATABASE_URL)

class MessageToUsers(StatesGroup):
    text = State()
    photo = State()


# Команда /admin
@router_admin.message(F.text.in_({'/admin', '⬅️ Назад'}))
async def admin_menu(message: CallbackQuery, state: FSMContext):
    # Сброс состояния при его наличии
    await state.clear()

    try:
        # Создание сессии
        async for session in database.get_session():

            # Проверка на админа
            if await database.check_admin(session, message.from_user.id) == True:

                await message.answer(
                    f'Меню админа',
                    reply_markup= keyboards.admin_keyboard,
                    parse_mode= 'HTML'
                )

            else:
                pass
    
    except Exception as error:
        print(f'admin_menu error: {error}')

# Рассылка
@router_admin.message(F.text == '📩 Рассылка')
async def message_to_all_handler(message: Message, state: FSMContext):

    try:
        # Создание сессии
        async for session in database.get_session():

            # Проверка на админа и запрос текста
            if await database.check_admin(session, message.from_user.id) == True:

                await message.answer(
                    f'Напишите текст который хотите разослать пользователям',
                    reply_markup= keyboards.dont_send
                )

                await state.set_state(MessageToUsers.text)

            else:
                pass

    except Exception as error:
        print(f'message_to_all_handler error: {error}')

# Запрос фото, после запроса текста
@router_admin.message(MessageToUsers.text)
async def photo(message: Message, state: FSMContext):

    # Добавление Текста из сообщения пользователя
    await state.update_data(text=message.text)

    # Добавления message.entities (если есть ссылки в сообщении)
    await state.update_data(entities=message.entities)

    await message.answer(
        f'Отправьте фото для этого текста',
        reply_markup= keyboards.without_photo_keyboard
    )

    await state.set_state(MessageToUsers.photo)

# Нажатие на кнопку "Без фото"
@router_admin.callback_query(F.data == 'WithoutPhoto')
async def without_photo(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    text = data['text']
    entities = data['entities']

    await callback.message.edit_text(
        f'{text}',
        reply_markup= keyboards.question_to_send,
        entities=entities,
        disable_web_page_preview=True
    )

# Скачивание фото после его добавления пользователем, либо при ошибке просит заново скинуть фото
@router_admin.message(MessageToUsers.photo)
async def add_photo(message: Message, state: FSMContext):

    try:
        await state.update_data(photo = message.photo)
        data = await state.get_data()
        photo = data['photo']
        text = data['text']
        entities = data['entities']

        # Скачивание фото от пользователя
        file = await bot.get_file(photo[-1].file_id)
        file_path = file.file_path
        await bot.download_file(file_path, f'bot/images/{photo[-1].file_id}.jpeg')

        await message.answer_photo(
            photo= photo[-1].file_id,
            caption=f'{text}',
            reply_markup= keyboards.question_to_send,
            caption_entities= entities
        )

    except Exception as error:
        print(error)
        await message.answer(
            f'Отправьте фото для этого текста',
            reply_markup= keyboards.question_to_send
        )

# Отправка текста с фото всем пользователям
@router_admin.callback_query(F.data == 'SendToAll')
async def send_to_all(callback: CallbackQuery, state: FSMContext):
    
    data = await state.get_data()
    text = data['text']
    entities = data['entities']
    try:
        photo = data['photo']
    except:
        photo = None

    await callback.answer(
        f'✅ Рассылка началась',
        show_alert= True
    )

    # Сброс состояния
    await state.clear()

    if photo:

        try:
            # Создание сессии
            async for session in database.get_session():

                photo_send = FSInputFile(f'bot/images/{photo[-1].file_id}.jpeg')
                await database.send_message_to_everyone(
                    session,
                    bot,
                    text,
                    entities,
                    photo_send
                )

        except Exception as error:
            print(f'send_to_all with photo error: {error}')

    else:
        try:
            # Создание сессии
            async for session in database.get_session():

                await database.send_message_to_everyone(
                    session,
                    bot,
                    text,
                    entities
                )

        except Exception as error:
            print(f'send_to_all without photo error: {error}')


    try:
        await callback.message.edit_text(
            f'{text}\n\n✅ Сообщение отправлено',
            entities= entities,
            disable_web_page_preview= True
        )

    except:
        await callback.message.edit_caption(
            None,
            f'{text}\n\n✅ Сообщение отправлено',
            entities= entities,
            disable_web_page_preview= True
        )

# Отмена отправки текста с фото пользователям
@router_admin.callback_query(F.data == 'DontSendToAll')
async def dont_send_photo(callback: CallbackQuery, state: FSMContext):

    try:
        data = await state.get_data()
        text = data['text']

        try:
            await callback.message.edit_text(f'{text}\n\n❗️ Сообщение не отправлено ❗️')
        except:
            await callback.message.edit_caption(None, f'{text}\n\n❗️ Сообщение не отправлено ❗️')
    except:
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    await callback.answer(
        f'Сообщение не отправлено',
        show_alert= True
    )

    # Сброс состояния
    await state.clear()


# Статистика
@router_admin.message(F.text == '📋 Статистика')
async def stats_handler(message: Message, state: FSMContext):
    # Сброс состояния при его наличии
    await state.clear()

    try:
        # Создание сессии
        async for session in database.get_session():

            # Проверка на админа и запрос текста
            if await database.check_admin(session, message.from_user.id) == True:

                mes = await message.answer(
                    '<b>🔍 Сбор статистики</b>\n\nОжидайте...',
                    parse_mode='HTML'
                )

                stats_text = await database.get_stats(session)

                await bot.edit_message_text(
                    stats_text,
                    message.chat.id,
                    mes.message_id,
                    parse_mode= 'html'
                )

            else:
                pass

    except Exception as error:
        print(f'stats error: {error}')


# Проверка созданных/заблокированных анкет
@router_admin.message(F.text == '🔍 Начать проверку')
async def verification_forms_handler(message: Message, state: FSMContext):
    # Сброс состояния при его наличии
    await state.clear()

    try:
        # Создание сессии
        async for session in database.get_session():

            # Проверка на админа
            if await database.check_admin(session, message.from_user.id) == True:

                # Получение анкеты для проверки
                form_for_verification = await database.get_form_for_verification(session)

            else:
                pass


        if form_for_verification is not None:

            form_id = form_for_verification.id
            username = form_for_verification.username
            name = form_for_verification.name
            age = form_for_verification.age
            city = form_for_verification.city
            about = form_for_verification.about
            target = form_for_verification.target
            photo = form_for_verification.photos[0]


            # Проверка созданной анкеты
            if form_for_verification.status == 'wait':
                await message.answer_photo(
                    photo= FSInputFile(f'photos/{photo}'),
                    caption= await messages.FORM_TEXT(name, age, city, about, target),
                    parse_mode= 'HTML',
                    reply_markup= await keyboards.check_waited_forms(form_id, username)
                )

            # Проверка заблокированной анкеты
            elif form_for_verification.status == 'blocked':
                await message.answer_photo(
                    photo= FSInputFile(f'photos/{photo}'),
                    caption= await messages.FORM_TEXT(name, age, city, about, target),
                    parse_mode= 'HTML',
                    reply_markup= await keyboards.check_blocked_forms(form_id)
                )
        
        else:
            await message.answer('Все анкеты проверены!')
            return

    except Exception as error:
        print(f'stats_handler error: {error}')

# Подтверждение созданной анкеты 
@router_admin.callback_query(F.data.contains('accept_form'))
async def accept_form_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его наличии
    await state.clear()

    # Получение id анкеты
    form_id = callback.data.split()[1]

    try:
        # Создание сессии
        async for session in database.get_session():
            # Изменение статуса анкеты
            await database.update_status_form(session, form_id, 'open')


        # Подписание анкеты 
        await callback.message.edit_caption(
            caption= f'Анкета подтверждена ✅\n\n{callback.message.caption}',
            parse_mode= 'HTML',
            reply_markup= None
        )

        try:
            # Отправка человеку сообщения о подтвержденной анкете
            await bot.send_photo(
                chat_id= form_id,
                photo= FSInputFile('bot/design/accepted_form.jpeg'),
                caption= 'Ваша анкета подтверждена!\n\nНачинайте занкомиться 😍',
                reply_markup= keyboards.under_menu_keyboard
            )
        except:
            pass

    except Exception as error:
        print(f'accept_form_handler error: {error}')

# Отклонение созданной анкеты 
@router_admin.callback_query(F.data.contains('cancel_form'))
async def cancel_form_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его наличии
    await state.clear()

    # Получение id и username анкеты
    form_id = callback.data.split()[1]
    username = callback.data.split()[2]

    try:
        # Создание сессии
        async for session in database.get_session():
            # Изменение статуса анкеты
            await database.update_status_form(session, form_id, 'canceled')


        # Подписание анкеты 
        await callback.message.edit_caption(
            caption= f'Анкета не подтверждена ❌\n\n{callback.message.caption}',
            parse_mode= 'HTML',
            reply_markup= None
        )

        try:
            # Отправка человеку сообщения о неподтвержденной анкете
            await bot.send_photo(
                chat_id= form_id,
                photo= FSInputFile('bot/design/canceled_form.jpeg'),
                caption= 'Ваша анкета не подтверждена!\n\nВам необходимо заново пройти регистрацию',
                reply_markup= await keyboards.recreate_keyboard_by_admins(form_id, username)
            )
        except:
            pass

    except Exception as error:
        print(f'cancel_form_handler error: {error}')

# Разблокировка анкеты 
@router_admin.callback_query(F.data.contains('unblock'))
async def unblock_form_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его наличии
    await state.clear()

    # Получение id анкеты
    form_id = callback.data.split()[1]

    try:
        # Создание сессии
        async for session in database.get_session():
            # Изменение статуса анкеты
            await database.update_status_form(session, form_id, 'open')


        # Подписание анкеты 
        await callback.message.edit_caption(
            caption= f'Анкета разблокирована ✅\n\n{callback.message.caption}',
            parse_mode= 'HTML',
            reply_markup= None
        )

        try:
            # Отправка человеку сообщения о разблокированной анкете
            await bot.send_photo(
                chat_id= form_id,
                photo= FSInputFile('bot/design/accepted_form.jpeg'),
                caption= 'Ваша анкета разблокирована!\n\nПродолжайте занкомиться 😍',
                reply_markup= keyboards.under_menu_keyboard
            )
        except:
            pass

    except Exception as error:
        print(f'unblock_form_handler error: {error}')

# Разблокировка анкеты 
@router_admin.callback_query(F.data.contains('ban'))
async def ban_form_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его наличии
    await state.clear()

    # Получение id анкеты
    form_id = callback.data.split()[1]

    try:
        # Создание сессии
        async for session in database.get_session():
            # Изменение статуса анкеты
            await database.update_status_form(session, form_id, 'banned')


        # Подписание анкеты 
        await callback.message.edit_caption(
            caption= f'Анкета заблокирована 🔐\n\n{callback.message.caption}',
            parse_mode= 'HTML',
            reply_markup= None
        )

        try:
            # Отправка человеку сообщения о забаненной анкете
            await bot.send_photo(
                chat_id= form_id,
                photo= FSInputFile('bot/design/banned.jpeg'),
                caption= '❌ Твой аккаунт заблокирован без возможности разблокировки.'
            )
        except:
            pass

    except Exception as error:
        print(f'ban_form_handler error: {error}')




# Обработка прочих сообщений
@router_admin.message()
async def echo(message: Message, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()
 
    await message.answer('Воспользуйтесь командами или клавиатурой, а если что-то пошло не так, воспользуйся командой /start, чтобы перезапустить бота')
