from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select
import config
import web_registration.app_texts as app_texts
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from models import UserModel


bot = Bot(token=config.BOT_TOKEN)

engine = create_async_engine(config.DATABASE_URL)

Base = declarative_base()

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Создание сессии
async def get_session():
    async with async_session() as session:
        yield session


# Создание всех таблиц
async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Сообщение админам в телеграм о создании новой анкеты
async def notify_admins():
    try:
        # Поиск id админов
        async with async_session() as session:

            # Выполняем запрос для получения id пользователей, у которых admin равно 1
            result = await session.execute(select(UserModel.id).where(UserModel.admin == 1))
            admin_ids = [row for row in result.scalars()]

        for id in admin_ids:
            await bot.send_message(
                id,
                app_texts.new_form
            )
    except Exception as error:
        print(f'notify_admins() error: {error}')
    pass


# Сообщение пользователю в телеграм о создании или обновлении анкеты
async def success_message(user_id, action):
    try:
        # Если нужна проверка новой анкеты админами
 
        # if action == 'update':
        #     await bot.send_message(
        #         user_id,
        #         app_texts.success_update
        #     )

        # elif action == 'creation':
        #     await bot.send_message(
        #         user_id,
        #         app_texts.success_create
        #     )

        await bot.send_photo(
            user_id,
            photo= FSInputFile('web_registration/static/already.jpeg'),
            caption= app_texts.success_create_without_wait,
            reply_markup= InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text= '❤️ Смотреть анкеты', callback_data= 'check_forms')]])
        )

    except Exception as error:
        print(f'success_message({user_id}) error: {error}')