from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo


# Клавиатура регистрации
async def registrate(user_id, username):
    markup = [
        # [
        #     InlineKeyboardButton(text='❤️ Создать анкету', web_app=WebAppInfo(url=f'https://click-love.ru/registration/{user_id}/{username}'))
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
            InlineKeyboardButton(text= '😊 Как выглядит моя анкета', callback_data= 'my_profile')
        ],
        [
            InlineKeyboardButton(text= '🎃РЕПКА', callback_data= 'referral_program')
        ],
        # [
        #     InlineKeyboardButton(text= '✍️ Редактировать анкету', callback_data= 'recreate_profile')
        # ],
        # [
        #     InlineKeyboardButton(text= '🎁 Бонусы', callback_data= 'bonuses')
        # ],
        [
            InlineKeyboardButton(text= '❤️ Смотреть анкеты', callback_data= 'check_profiles from_menu')
        ]
    ]

    if status == 'open':
        markup.insert(0,[InlineKeyboardButton(text= '🙈 Скрыть анкету', callback_data= 'update_profile_status')])
    elif status == 'closed':
        markup.insert(0,[InlineKeyboardButton(text= '🤗 Открыть анкету', callback_data= 'update_profile_status')])

    keyboard = InlineKeyboardMarkup(inline_keyboard= markup)
    return keyboard


# Клавиатура для просмотра анкет
async def profile_keyboard(id, more_photo= False, next_photo_num= 1):
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
            InlineKeyboardButton(text='❤️ Изменить анкету', url=f'https://click-love.ru/edit_profile/{user_id}/{username}')
        ],
        [
            InlineKeyboardButton(text= '🏠 Меню', callback_data= 'menu')
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard= markup)
    return keyboard


# Клавиатура для ответа на лайк
async def profile_after_like_keyboard(id, more_photo= False, next_photo_num= 1):
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
async def check_waited_profiles(id, username, more_photo= False, next_photo_num= 1):
    markup = [
        [
            InlineKeyboardButton(text= '✅ Одобрить', callback_data= f'accept_profile {id}'),
        ],
        [
            InlineKeyboardButton(text= '❌ Отклонить', callback_data= f'cancel_profile {id} {username}'),
        ]
    ]
    if more_photo:
        markup.insert(0,[InlineKeyboardButton(text= '📸 Смотреть еще фото', callback_data= f'photo_verification {id} {next_photo_num} wait')])

    keyboard = InlineKeyboardMarkup(inline_keyboard= markup)
    return keyboard


# Клавиатура для проверки анкет на которые жаловались
async def check_blocked_profiles(id, more_photo= False, next_photo_num= 1):
    markup = [
        [
            InlineKeyboardButton(text= '🔓 Разблокировать', callback_data= f'unblock {id}'),
        ],
        [
            InlineKeyboardButton(text= '🔐 Забанить', callback_data= f'ban {id}'),
        ]
    ]
    if more_photo:
        markup.insert(0,[InlineKeyboardButton(text= '📸 Смотреть еще фото', callback_data= f'photo_verification {id} {next_photo_num} blocked')])

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


# Клавиатура для проверки анкет на которые жаловались
async def my_profile_keyboard(user_id, username, more_photo= False, next_photo_num= 1):
    markup = [
        [
            InlineKeyboardButton(text= '🏠 Меню', callback_data= 'menu'),
        ],
        [
            InlineKeyboardButton(text= '✍️ Редактировать анкету', url=f'https://click-love.ru/edit_profile/{user_id}/{username}')
        ],
        [
            InlineKeyboardButton(text= '❤️ Смотреть анкеты', callback_data= 'check_profiles'),
        ]
    ]
    if more_photo:
        markup.insert(0,[InlineKeyboardButton(text= '📸 Смотреть еще фото', callback_data= f'my_photo_check {user_id} {next_photo_num}')])

    keyboard = InlineKeyboardMarkup(inline_keyboard= markup)
    return keyboard


# Клавиатура при уведомлении о лайке
async def show_profile_keyboard(profile_id, mutual= None):
    if mutual is not None:
        mutual = 'mutual'
    keyboard = [
        [
            InlineKeyboardButton(text='Посмотреть', callback_data= f'check_profile_who_liked_me {profile_id} {mutual}')
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard= keyboard)
    return keyboard



# Клавиатура после подтверждения анкеты
start_keyboard = [
    [
        InlineKeyboardButton(text= '🏠 Меню', callback_data= 'menu'),
    ],
    [
        InlineKeyboardButton(text= '❤️ Смотреть анкеты', callback_data= 'check_profiles')
    ]
]
start_keyboard = InlineKeyboardMarkup(inline_keyboard= start_keyboard)


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
        InlineKeyboardButton(text= 'Смотреть анкеты ➡️', callback_data= 'check_bot')
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
        KeyboardButton(text='📩 Рассылка всем')
    ],
    [
        KeyboardButton(text='📩 Рассылка всем без анкет')
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


# ТехПоддержка
corbots_keyboard = [
    [
        InlineKeyboardButton(text='👀 ПОСМОТРЕТЬ 👀', url='https://t.me/corbots')
    ]
]
corbots_keyboard = InlineKeyboardMarkup(inline_keyboard=corbots_keyboard)


# Демо-выбор
gender_keyboard = [
    [
        InlineKeyboardButton(text='С мужчинами', callback_data='demo no-mark man 1')
    ],
    [
        InlineKeyboardButton(text='С женщинами', callback_data='demo no-mark woman 1')
    ]
]
gender_keyboard = InlineKeyboardMarkup(inline_keyboard=gender_keyboard)


# Демо-клавиатура для анкет
async def demo_profile_keyboard(gender, number):
    markup = [
        [
            InlineKeyboardButton(text= '❤️ Нравится', callback_data= f'demo like {gender} {number}'),
            InlineKeyboardButton(text= '❌ Не нравится', callback_data= f'demo dislike {gender} {number}')
        ]
    ]
    demo_profile_keyboard = InlineKeyboardMarkup(inline_keyboard= markup)
    return demo_profile_keyboard


# Клавиатура реферальной системы
referrals_keyboard = [
    [
        InlineKeyboardButton(text= '👨‍👧‍👦 Пригласить друзей', callback_data= 'invite'),
    ],
    [
        InlineKeyboardButton(text= '🏠 Меню', callback_data= 'menu'),
    ],
    [
        InlineKeyboardButton(text= '❤️ Смотреть анкеты', callback_data= 'check_profiles')
    ]
]
referrals_keyboard = InlineKeyboardMarkup(inline_keyboard= referrals_keyboard)