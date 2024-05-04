from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
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
@router_admin.message(F.text.in_({'📩 Рассылка всем', '📩 Рассылка всем без анкет'}))
async def message_to_all_handler(message: Message, state: FSMContext):
    # Сброс состояния при его наличии
    await state.clear()

    try:
        # Создание сессии
        async for session in database.get_session():

            # Проверка на админа и запрос текста
            if await database.check_admin(session, message.from_user.id) == True:

                # Определение кому рассылка. Добавление в state
                if message.text == '📩 Рассылка всем':
                    await state.update_data(type='to everyone')
                elif message.text == '📩 Рассылка всем без анкет':
                    await state.update_data(type='without profile')

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
    send_type = data['type']
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

                # Определение черного списка для рассылки
                if send_type == 'to everyone':
                    black_list = []
                elif send_type == 'without profile':
                    # Получение списка тех, у кого есть анкета
                    black_list = await database.get_ids_with_profile(session)

                photo_send = FSInputFile(f'bot/images/{photo[-1].file_id}.jpeg')
                await database.send_message_to_everyone(
                    session,
                    bot,
                    text,
                    entities,
                    photo_send,
                    black_list= black_list
                )

        except Exception as error:
            print(f'send_to_all with photo error: {error}')

    else:
        try:
            # Создание сессии
            async for session in database.get_session():

                # Определение черного списка для рассылки
                if send_type == 'to everyone':
                    black_list = []
                elif send_type == 'without profile':
                    # Получение списка тех, у кого есть анкета
                    black_list = await database.get_ids_with_profile(session)

                await database.send_message_to_everyone(
                    session,
                    bot,
                    text,
                    entities,
                    black_list= black_list
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

                stats = await database.get_stats(session)
                users_amount = stats['users_amount']
                active_profiles_amount = stats['active_profiles_amount']
                closed_profiles_amount = stats['closed_profiles_amount']
                waited_profiles_amount = stats['waited_profiles_amount']
                men_profiles_amount = stats['men_profiles_amount']
                women_profiles_amount =stats['women_profiles_amount']
                men_profiles_closed_amount =stats['men_profiles_closed_amount']
                women_profiles_closed_amount = stats['women_profiles_closed_amount']

                await bot.edit_message_text(
                    f'<b>📋 Статистика</b>\n\nВсего пользователей: <b>{users_amount}</b>\n\n<b>Анкеты\n</b>Мужчины: <b>{men_profiles_amount} чел. ({men_profiles_closed_amount} скрыто)</b>\nЖенщины: <b>{women_profiles_amount} чел. ({women_profiles_closed_amount} скрыто)</b>\nВсего открытых: <b>{active_profiles_amount} шт.</b>\nВсего закрытых: <b>{closed_profiles_amount} шт.</b>\n\nОжидают проверки: <b>{waited_profiles_amount} шт.</b>\n\n',
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
async def verification_profiles_handler(message: Message, state: FSMContext):
    # Сброс состояния при его наличии
    await state.clear()

    try:
        # Создание сессии
        async for session in database.get_session():

            # Проверка на админа
            if await database.check_admin(session, message.from_user.id) == True:

                # Получение анкеты для проверки
                profile_for_verification = await database.get_profile_for_verification(session)

            else:
                return

    except Exception as error:
        print(f'verification_profiles_handler() Session error: {error}')

    try:
        if profile_for_verification is not None:

            profile_id = profile_for_verification.id
            username = profile_for_verification.username
            name = profile_for_verification.name
            age = profile_for_verification.age
            city = profile_for_verification.city
            about = profile_for_verification.about
            target = profile_for_verification.target
            photo = profile_for_verification.photos[0]

            # Проверка на число фото больше одного
            if len(profile_for_verification.photos) != 1:
                more_photo = True
            else:
                more_photo = False

            # Проверка созданной анкеты
            if profile_for_verification.status == 'wait':
                await message.answer_photo(
                    photo= FSInputFile(f'photos/{photo}'),
                    caption= await messages.PROFILE_TEXT(name, age, city, about, target),
                    parse_mode= 'HTML',
                    reply_markup= await keyboards.check_waited_profiles(profile_id, username, more_photo= more_photo)
                )

            # Проверка заблокированной анкеты
            elif profile_for_verification.status == 'blocked':
                await message.answer_photo(
                    photo= FSInputFile(f'photos/{photo}'),
                    caption= await messages.PROFILE_TEXT(name, age, city, about, target),
                    parse_mode= 'HTML',
                    reply_markup= await keyboards.check_blocked_profiles(profile_id, more_photo= more_photo)
                )
        
        else:
            await message.answer('Все анкеты проверены!')
            return

    except Exception as error:
        print(f'verification_profiles_handler() error: {error}')
        await message.answer(f'Ошибка: {error}')


# Листание фото
@router_admin.callback_query(F.data.contains('photo_verification'))
async def photo_verification_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    print(callback.data)

    profile_id = callback.data.split()[1]
    photo_num = int(callback.data.split()[2])
    verification = callback.data.split()[3]

    # Создание сессии
    try:
        async for session in database.get_session():
            profile = await database.get_profile_information(session, profile_id)
    except Exception as error:
        print(f'photo_verification_handler() Session error: {error}')

    try:
        # Если есть еще фото, то порядковый номер увеличивается
        if len(profile.photos) == photo_num + 1:
            next_photo_num = 0
        else:
            next_photo_num = photo_num + 1

        # Выбор клавиатуре в зависимости от проверки
        if verification == 'wait':
            keyboard = await keyboards.check_waited_profiles(profile_id, profile.username, more_photo= True, next_photo_num= next_photo_num)
        elif verification == 'blocked':
            keyboard = await keyboards.check_blocked_profiles(profile_id, more_photo= True, next_photo_num= next_photo_num)

        await callback.message.edit_media(
            media= InputMediaPhoto(
                media= FSInputFile(f'photos/{profile.photos[photo_num]}'),
                caption= await messages.PROFILE_TEXT(profile.name, profile.age, profile.city, profile.about, profile.target),
                parse_mode='HTML'
            ), 
            reply_markup= keyboard
        )
    except Exception as error:
        print(f'photo_verification_handler() error: {error}')


# Подтверждение созданной анкеты 
@router_admin.callback_query(F.data.contains('accept_profile'))
async def accept_profile_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его наличии
    await state.clear()

    # Получение id анкеты
    profile_id = callback.data.split()[1]

    try:
        # Создание сессии
        async for session in database.get_session():
            # Изменение статуса анкеты
            await database.update_status_profile(session, profile_id, 'open')


        # Подписание анкеты 
        await callback.message.edit_caption(
            caption= f'Анкета подтверждена ✅\n\n{callback.message.caption}',
            parse_mode= 'HTML',
            reply_markup= None
        )

        try:
            # Отправка человеку сообщения о подтвержденной анкете
            await bot.send_photo(
                chat_id= profile_id,
                photo= FSInputFile('bot/design/accepted_profile.jpeg'),
                caption= 'Ваша анкета подтверждена!\n\nНачинайте знакомиться 😍',
                reply_markup= keyboards.start_keyboard
            )
        except:
            pass

    except Exception as error:
        print(f'accept_profile_handler error: {error}')


# Отклонение созданной анкеты 
@router_admin.callback_query(F.data.contains('cancel_profile'))
async def cancel_profile_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его наличии
    await state.clear()

    # Получение id и username анкеты
    profile_id = callback.data.split()[1]
    username = callback.data.split()[2]

    try:
        # Создание сессии
        async for session in database.get_session():
            # Изменение статуса анкеты
            await database.update_status_profile(session, profile_id, 'canceled')


        # Подписание анкеты 
        await callback.message.edit_caption(
            caption= f'Анкета не подтверждена ❌\n\n{callback.message.caption}',
            parse_mode= 'HTML',
            reply_markup= None
        )

        try:
            # Отправка человеку сообщения о неподтвержденной анкете
            await bot.send_photo(
                chat_id= profile_id,
                photo= FSInputFile('bot/design/canceled_profile.jpeg'),
                caption= messages.CANCELED,
                reply_markup= await keyboards.recreate_keyboard_by_admins(profile_id, username)
            )
        except:
            pass

    except Exception as error:
        print(f'cancel_profile_handler error: {error}')


# Разблокировка анкеты 
@router_admin.callback_query(F.data.contains('unblock'))
async def unblock_profile_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его наличии
    await state.clear()

    # Получение id анкеты
    profile_id = callback.data.split()[1]

    try:
        # Создание сессии
        async for session in database.get_session():
            # Изменение статуса анкеты
            await database.update_status_profile(session, profile_id, 'open')


        # Подписание анкеты 
        await callback.message.edit_caption(
            caption= f'Анкета разблокирована ✅\n\n{callback.message.caption}',
            parse_mode= 'HTML',
            reply_markup= None
        )

        try:
            # Отправка человеку сообщения о разблокированной анкете
            await bot.send_photo(
                chat_id= profile_id,
                photo= FSInputFile('bot/design/unblocked.jpeg'),
                caption= 'Ваша анкета разблокирована!\n\nПродолжайте занкомиться 😍',
                reply_markup= keyboards.start_keyboard
            )
        except:
            pass

    except Exception as error:
        print(f'unblock_profile_handler error: {error}')


# Разблокировка анкеты 
@router_admin.callback_query(F.data.contains('ban'))
async def ban_profile_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его наличии
    await state.clear()

    # Получение id анкеты
    profile_id = callback.data.split()[1]

    try:
        # Создание сессии
        async for session in database.get_session():
            # Изменение статуса анкеты
            await database.update_status_profile(session, profile_id, 'banned')


        # Подписание анкеты 
        await callback.message.edit_caption(
            caption= f'Анкета заблокирована 🔐\n\n{callback.message.caption}',
            parse_mode= 'HTML',
            reply_markup= None
        )

        try:
            # Отправка человеку сообщения о забаненной анкете
            await bot.send_photo(
                chat_id= profile_id,
                photo= FSInputFile('bot/design/banned.jpeg'),
                caption= '❌ Твой аккаунт заблокирован без возможности разблокировки.'
            )
        except:
            pass

    except Exception as error:
        print(f'ban_profile_handler error: {error}')