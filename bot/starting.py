from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from bot.database import DataBase
import bot.keyboards as keyboards
import bot.messages as messages
import config


bot = Bot(token=config.BOT_TOKEN)
router_starting = Router()

database = DataBase(config.DATABASE_URL)


# Команда /start
@router_starting.message(F.text.contains("/start"))
async def accept_agreement_handler(message: Message, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    global start_message
    start_message = await message.answer_video(
        video= FSInputFile('bot/design/start.mp4'),
        caption= messages.START_TEXT_NEW_USER,
        reply_markup= keyboards.check_bot,
        parse_mode= 'HTML'  
    )

# Проверка юзернейма
@router_starting.callback_query(F.data.contains('check_bot'))
async def check_bot_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Проверка на наличие юзернейма
    if callback.from_user.username is None:
        await callback.message.answer(
            messages.CREATE_USERNAME,
            reply_markup= keyboards.check_bot
        )
        return

    # Создание сессии
    try:
        async for session in database.get_session():

            # Получение данных об анкете
            profile = await database.get_profile_information(session, callback.from_user.id)

            # Получение данных о пользователе
            user = await database.get_user_information(session, callback.from_user.id)

            # Проверка на бан
            if profile:
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

    except Exception as error:
        print(f'check_bot_handler() Session error: {error}')

    try:
        # Проверка на наличие анкеты
        if profile is None:
            # await callback.message.answer_video(
            #     video= FSInputFile('bot/design/start.mp4'),
            #     caption= messages.START_TEXT_NEW_USER,
            #     reply_markup= await keyboards.registrate(callback.from_user.id, callback.from_user.username)
            # )

            # await callback.message.edit_media(
            #     media= InputMediaPhoto(
            #         media= FSInputFile('bot/design/gift.jpeg'),
            #         caption= messages.START_TEXT_NEW_USER_3,
            #         parse_mode= 'HTML'
            #     ),
            #     reply_markup= await keyboards.registrate(callback.from_user.id, callback.from_user.username)
            # )

            await callback.message.edit_media(
                media= InputMediaPhoto(
                    media= FSInputFile('bot/design/gender.jpeg'),
                    caption= messages.START_TEXT_NEW_USER_2,
                    parse_mode= 'HTML'
                ),
                reply_markup= keyboards.gender_keyboard
            )

        # В случае наличии анкеты вход в меню
        else:
            global main_menu
            main_menu = await callback.message.answer_photo(
                photo= FSInputFile('bot/design/menu.jpeg'),
                caption= await messages.MENU_TEXT(profile.status, user.sub_status, user.sub_end_date),
                reply_markup= await keyboards.menu_keyboard(profile.status),
                parse_mode= 'html'
            )

            try:
                await bot.delete_message(callback.message.chat.id, start_message.message_id)
            except: pass

    except Exception as error:
        print(f'check_bot_handler() error: {error}')
    

# Выбор пола
@router_starting.callback_query(F.data.contains('demo'))
async def demo_profiles_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    try:
        mark = callback.data.split()[1]
        gender = callback.data.split()[2]
        number = int(callback.data.split()[3])
        next_demo_profile = number + 1

        try:
            if gender == 'man':
                caption = messages.DEMO_PROFILES_MAN[number-1]
            elif gender == 'woman':
                caption = messages.DEMO_PROFILES_WOMAN[number-1]
        except: pass


        # К тексту анкеты добавляется оценка и убирается клавиатура
        if mark == 'like':
            await callback.message.edit_caption(
                caption= f'Вы лайкнули эту анкету ❤️\n\n{callback.message.caption}',
                reply_markup= None
            )
        elif mark == 'dislike':
            await callback.message.edit_caption(
                caption= f'Вам не понравилась эта анкета 💔\n\n{callback.message.caption}',
                reply_markup= None
            )


        # Если первая анкета, то сообщение редактируется
        if number == 1:
            await callback.message.edit_media(
                media= InputMediaPhoto(
                    media= FSInputFile(f'photos/demo-{gender}-{number}.jpeg'),
                    caption= caption,
                    parse_mode= 'HTML'
                ),
                reply_markup= await keyboards.demo_profile_keyboard(gender, next_demo_profile)
            )

        # Вывод анкет, до третей
        elif number <= 3:
            await callback.message.answer_photo(
                photo= FSInputFile(f'photos/demo-{gender}-{number}.jpeg'),
                caption= caption,
                parse_mode= 'HTML',
                reply_markup= await keyboards.demo_profile_keyboard(gender, next_demo_profile)
            )

        # Если пролистаны все демо анкеты, то сообщение зарегаться
        else:
            await callback.message.answer_photo(
                photo= FSInputFile('bot/design/gift.jpeg'),
                caption= messages.START_TEXT_NEW_USER_3,
                parse_mode= 'HTML',
                reply_markup= await keyboards.registrate(callback.from_user.id, callback.from_user.username)
            )

    except Exception as error:
        print(f'demo_profiles_handler() error: {error}')


# Обработка прочих сообщений
@router_starting.message()
async def echo(message: Message, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()
 
    await message.answer('Воспользуйтесь командами или клавиатурой, а если что-то пошло не так, воспользуйся командой /start, чтобы перезапустить бота')
