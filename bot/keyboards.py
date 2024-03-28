from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo


# Клавиатура после стартового сообщения
start_keyboard = [
    [
    KeyboardButton(text= 'Зарегистрироваться', web_app= WebAppInfo(url='https://click-love.ru/registration/123'))
    ]
]
start_keyboard = ReplyKeyboardMarkup(keyboard= start_keyboard, resize_keyboard= True, is_persistent= True)

# Клавиатура подтверждения анкеты после регистрации
preview_form_keyboard =[
    [
        InlineKeyboardButton(text= '✅ Создать анкету', callback_data= 'create_form')
    ],
    [
        InlineKeyboardButton(text= '🔄 Пересоздать', callback_data= 'recreate_form')
    ]
]
preview_form_keyboard = InlineKeyboardMarkup(inline_keyboard= preview_form_keyboard)

# Клавиатура для разделов меню
under_menu_keyboard = [
    [
    InlineKeyboardButton(text= '🏠 Меню', callback_data= 'menu')
    ],
    [
    InlineKeyboardButton(text= '❤️ Смотреть анкеты', callback_data= 'check_forms')
    ]
]
under_menu_keyboard = InlineKeyboardMarkup(inline_keyboard= under_menu_keyboard)


# Клавиатура меню
async def menu_keyboard(status):
    menu_keyboard =[
        [
            InlineKeyboardButton(text= '😊 Как выглядит моя анкета', callback_data= 'my_form')
        ],
        [
            InlineKeyboardButton(text= '✍️ Редактировать анкету', callback_data= 'recreate_form')
        ],
        [
            InlineKeyboardButton(text= '🎁 Бонусы', callback_data= 'bonuses')
        ],
        [
            InlineKeyboardButton(text= '❤️ Смотреть анкеты', callback_data= 'check_forms')
        ]
    ]

    if status == 'open':
        menu_keyboard.insert(0,[InlineKeyboardButton(text= '🙈 Скрыть анкету', callback_data= 'update_form_status')])
    elif status == 'closed':
        menu_keyboard.insert(0,[InlineKeyboardButton(text= '🤗 Открыть анкету', callback_data= 'update_form_status')])
    elif status == 'wait':
        menu_keyboard.insert(0,[InlineKeyboardButton(text= '❗️ Анкета еще не подтверждена', callback_data= 'update_form_status')])

    menu_keyboard = InlineKeyboardMarkup(inline_keyboard= menu_keyboard)
    return menu_keyboard

# Клавиатура при уведомлении о лайке
async def show_form_keyboard(form_id, mutual= None):
    if mutual is not None:
        mutual = 'mutual'
    show_form_keyboard = [
        [
            InlineKeyboardButton(text='Посмотреть', callback_data= f'check_form_who_liked_me {form_id} {mutual}')
        ]
    ]
    show_form_keyboard = InlineKeyboardMarkup(inline_keyboard= show_form_keyboard)
    return show_form_keyboard









# НОВЫЕ КЛАВИАТУРЫ




# Клавиатура регистрации
async def registrate(user_id, username):
    markup = [
        # [
        #     InlineKeyboardButton(text='❤️ Создать анкету', web_app=WebAppInfo(url=f'https://click-love.ru/registration/{user_id}'))
        # ],
        [
            InlineKeyboardButton(text='❤️ Создать анкету', url=f'https://click-love.ru/registration/{user_id}/{username}')
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard= markup)
    return keyboard


# Клавиатура меню
async def menu_keyboard(status):
    markup =[
        [
            InlineKeyboardButton(text= '😊 Как выглядит моя анкета', callback_data= 'my_form')
        ],
        [
            InlineKeyboardButton(text= '✍️ Редактировать анкету', callback_data= 'recreate_form')
        ],
        # [
        #     InlineKeyboardButton(text= '🎁 Бонусы', callback_data= 'bonuses')
        # ],
        [
            InlineKeyboardButton(text= '❤️ Смотреть анкеты', callback_data= 'check_forms')
        ]
    ]

    if status == 'open':
        markup.insert(0,[InlineKeyboardButton(text= '🙈 Скрыть анкету', callback_data= 'update_form_status')])
    elif status == 'closed':
        markup.insert(0,[InlineKeyboardButton(text= '🤗 Открыть анкету', callback_data= 'update_form_status')])

    keyboard = InlineKeyboardMarkup(inline_keyboard= markup)
    return keyboard


# Клавиатура для просмотра анкет
async def form_keyboard(id, more_photo= False, next_photo_num= 1):
    markup = [
        [
            InlineKeyboardButton(text= '❤️ Нравится', callback_data= f'rate like {id}'),
            InlineKeyboardButton(text= '❌ Не нравится', callback_data= f'rate dislike {id}')
        ],
        [
            InlineKeyboardButton(text= '❕ Жалоба', callback_data= f'warn {id}'),
            InlineKeyboardButton(text= '🏠 Меню', callback_data= 'menu')
        ]
    ]
    if more_photo:
        markup.insert(0,[InlineKeyboardButton(text= '📸 Смотреть еще фото', callback_data= f'check_photo {id} {next_photo_num}')])

    keyboard = InlineKeyboardMarkup(inline_keyboard= markup)
    return keyboard


# Клавиатура для пересоздания анкет
async def recreate_keyboard(user_id, username):
    markup = [
        [
            InlineKeyboardButton(text='❤️ Изменить анкету', url=f'https://click-love.ru/registration/{user_id}/{username}')
        ],
        [
            InlineKeyboardButton(text= '🏠 Меню', callback_data= 'menu')
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard= markup)
    return keyboard


# Клавиатура для ответа на лайк
async def form_after_like_keyboard(id, more_photo= False, next_photo_num= 1):
    markup = [
        [
            InlineKeyboardButton(text= '❤️ Нравится', callback_data= f'who_liked_me like {id}'),
            InlineKeyboardButton(text= '❌ Не нравится', callback_data= f'who_liked_me dislike {id}')
        ],
        [
            InlineKeyboardButton(text= '❕ Жалоба', callback_data= f'warn {id}'),
            InlineKeyboardButton(text= '🏠 Меню', callback_data= 'menu')
        ]
    ]
    if more_photo:
        markup.insert(0,[InlineKeyboardButton(text= '📸 Смотреть еще фото', callback_data= f'check_photo {id} {next_photo_num}')])

    keyboard = InlineKeyboardMarkup(inline_keyboard= markup)
    return keyboard


# Клавиатура для проверки созданных анкет
async def check_waited_forms(id, username):
    markup = [
        [
            InlineKeyboardButton(text= '✅ Одобрить', callback_data= f'accept_form {id}'),
        ],
        [
            InlineKeyboardButton(text= '❌ Отклонить', callback_data= f'cancel_form {id} {username}'),
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard= markup)
    return keyboard


# Клавиатура для проверки анкет на которые жаловались
async def check_blocked_forms(id):
    markup = [
        [
            InlineKeyboardButton(text= '🔓 Разблокировать', callback_data= f'unblock {id}'),
        ],
        [
            InlineKeyboardButton(text= '🔐 Забанить', callback_data= f'ban {id}'),
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard= markup)
    return keyboard


# Клавиатура для пересоздания анкет после отклонения админами
async def recreate_keyboard_by_admins(user_id, username):
    markup = [
        [
            InlineKeyboardButton(text='❤️ Изменить анкету', url=f'https://click-love.ru/registration/{user_id}/{username}')
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard= markup)
    return keyboard


# Клавиатура проверки юзернейма
check_username = [
    [
    InlineKeyboardButton(text= 'Проверить @юзернейм', callback_data= 'check_username')
    ]
]
check_username = InlineKeyboardMarkup(inline_keyboard= check_username)


# Клавиатура проверки юзернейма
check_bot = [
    [
    InlineKeyboardButton(text= 'Я не робот', callback_data= 'check_bot')
    ]
]
check_bot = InlineKeyboardMarkup(inline_keyboard= check_bot)


# Меню админа в боте заработка
admin_keyboard = [
[
    KeyboardButton(text='🔍 Начать проверку')
],
[
    KeyboardButton(text='📋 Статистика')
],
[
    KeyboardButton(text='📩 Рассылка')
]
]
admin_keyboard = ReplyKeyboardMarkup(keyboard=admin_keyboard, resize_keyboard=True, input_field_placeholder='Меню админа')


# Для рассылки
without_photo_keyboard = [
    [
        InlineKeyboardButton(text='Без фото', callback_data='WithoutPhoto')
    ]
]
without_photo_keyboard = InlineKeyboardMarkup(inline_keyboard=without_photo_keyboard)

question_to_send = [
[
    InlineKeyboardButton(text='Отправить всем пользователям', callback_data='SendToAll')
],
[
    InlineKeyboardButton(text='Не отправлять', callback_data='DontSendToAll')
]
]
question_to_send = InlineKeyboardMarkup(inline_keyboard=question_to_send)

dont_send = [
[
    InlineKeyboardButton(text='Не отправлять', callback_data='DontSendToAll')
]
]
dont_send = InlineKeyboardMarkup(inline_keyboard=dont_send)