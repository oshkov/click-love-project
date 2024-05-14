# ТЕКСТА

async def PROFILE_TEXT(name, age, city, about, targets):
    trgt = ''
    if targets is not None:
        target_text = "\n".join(targets)
        trgt = f'<b>Цели знакомств:</b>\n{target_text}'
    if about is None:
        about = ''
    else:
        about = f'\n\n{about}'

    return f'<b>{name}, {age}, г.{city}</b>{about}\n\n{trgt}'


async def MENU_TEXT(status, premium, premium_end):
    if status == 'open':
        status_text = '🤗 Ваша анкета открыта'
    elif status == 'closed':
        status_text = '🙈 Ваша анкета скрыта от других людей'
    elif status == 'wait':
        status_text = '❗️ Ваша анкета еще не подтверждена администраторами'
    elif status == 'blocked':
        status_text = '🥶 Ваша анкета заморожена'
    elif status == 'banned':
        status_text = '🔒Ваша анкета заблокирована'
    elif status == 'canceled':
        status_text = '❗️ Вам нужно пересоздать анкету'

    if premium == None:
        premium_text = '<b>❌ Подписка неактивна</b>'
    else:
        premium_text = f'<b>💎 Подписка активна до {premium_end.strftime("%d.%m.%Y")}</b>'

    return f'<b>🏠 Главное меню</b>\n\n{status_text}\n\n{premium_text}'


async def MUTUAL_LIKE_PREVIEW(profile):
    name = profile.name
    age = profile.age
    city = profile.city
    about = profile.about
    target = profile.target
    username = profile.username

    return f'Взаимный лайк ❤️\n\n{await PROFILE_TEXT(name, age, city, about, target)}\n\nНачинайте общение: @{username}'


async def REFERRAL_PROGRAM(user_id, referral_data):
    referrals_first_line = referral_data['firstLine']
    if referrals_first_line == 0:
        firstLine = 'Пользователи пока отсутствуют...'
    else:
        firstLine = f'{referrals_first_line} Пользователей / Начислено {referrals_first_line * 160}₽'

    referrals_second_line = referral_data['secondLine']
    if referrals_second_line == 0:
        secondLine = 'Пользователи пока отсутствуют...'
    else:
        secondLine = f'{referrals_second_line} Пользователей / Начислено {referrals_second_line * 80}₽'

    referrals_third_line = referral_data['thirdLine']
    if referrals_third_line == 0:
        thirdLine = 'Пользователи пока отсутствуют...'
    else:
        thirdLine = f'{referrals_third_line} Пользователей / Начислено {referrals_third_line * 40}₽'

    referrals_fourth_line = referral_data['fourthLine']
    if referrals_fourth_line == 0:
        fourthLine = 'Пользователи пока отсутствуют...'
    else:
        fourthLine = f'{referrals_fourth_line} Пользователей / Начислено {referrals_fourth_line * 20}₽'

    referrals_five_line = referral_data['fiveLine']
    if referrals_five_line == 0:
        fiveLine = 'Пользователи пока отсутствуют...'
    else:
        fiveLine = f'{referrals_five_line} Пользователей / Начислено {referrals_five_line * 10}₽'

    referrals_six_line = referral_data['sixLine']
    if referrals_six_line == 0:
        sixLine = 'Пользователи пока отсутствуют...'
    else:
        sixLine = f'{referrals_six_line} Пользователей / Начислено {referrals_six_line * 5}₽'

    invited_users = referral_data['allInvitedUsersCount']
    balance = referral_data['points']

    return f'💵Баланс Реферальной Программы:\n{balance}₽\n\n📲 Пригласить друга: <code>https://t.me/clicklove_bot?start={user_id}</code>\n\nПриглашено всего:\n{invited_users} Пользователей\n\n<u>1 уровень:</u> 160₽ за пользователя.\n<b>{firstLine}</b>\n\n<u>2 уровень:</u> 80₽ за пользователя.\n<b>{secondLine}</b>\n\n<u>3 уровень:</u> 40₽ за пользователя.\n<b>{thirdLine}</b>\n\n<u>4 уровень:</u> 20₽ за пользователя.\n<b>{fourthLine}</b>\n\n<u>5 уровень:</u> 10₽ за пользователя.\n<b>{fiveLine}</b>\n\n<u>6 уровень:</u> 5₽ за пользователя.\n<b>{sixLine}</b>'


async def REFERRAL_INVITE(user_id):
    return f'🥳 Вы приглашены в 🎃РЕПКУ!\n\n🤖 Единственная реферальная программа, для большой системы ботов.\n💵 Заработав в этом боте - тратишь во всех.\n👑 Приглашай пока тебя не пригласили. Первым быть выгодно!\n\nСсылка: <code>https://t.me/clicklove_bot?start={user_id}</code>\n\n<b><a href="https://t.me/clicklove_bot?start={user_id}">▶️ ПОДКЛЮЧИТЬСЯ К РЕПКЕ! ◀️</a></b>'


START_TEXT_NEW_USER = '<b>Как это работает? 🥳</b>\n\n✅ Регистрируйся\n👀 Смотри анкеты\n📍 Находи людей рядом\n❤️ Ставь лайки\n👩‍❤️‍💋‍👨 Получай взаимные лайки\n✍️ Общайся\n😘 Влюбляйся'
START_TEXT_NEW_USER_2 = 'С кем ты хочешь знакомиться?'
START_TEXT_NEW_USER_3 = '<b>Первым 1000 людей мы дарим Premium доступ на целый год!</b> 🎁\n\nЧтобы знакомиться дальше нужно зарегистрироваться!'
CREATE_USERNAME = 'Чтобы пользоваться ботом, вам нужен @юзернейм, по нему люди смогут связаться с тобой\n\nОн создается в настройках телеграма в пару кликов: настройки -> имя пользователя'
RECREATE_PROFILE_TEXT = 'Чтобы редактировать свою анкету нужно заново пройти регистрацию'
SUCCESS_PROFILE_CREATE_TEXT = 'Ваша анкета успешно создана'
CHECK_BOT = 'Подтвердите, что вы не робот'
MAKE_WARN = 'Жалоба отправлена, анкета будет проверена администраторами!'
NO_PROFILES = 'Подходящих для вас анкет, к сожалению, пока что нет'
MUTUAL_LIKE = 'У вас взаимный лайк 😍'
YOU_LIKED = 'Ваша анкета понравилась одному человеку 🤗'
BLOCKED = '🥶 Твой аккаунт временно заморожен из-за жалоб других пользователей'
BANNED = '🔒 Ваш аккаунт заблокирован навсегда'
WAITED = '❕ Ваша анкета не подтверждена\n\nОжидайте подтверждения админами'
CLOSED = '🙈 У вас закрытая анкета\n\nЧтобы просматривать анкеты, для начала откройте свою'
NO_PROFILE = 'У вас пока нет анкеты! 🤷🏻‍♀️\n\nЧтобы пользоваться ботом, необходимо создать анкету! 📝'
SUPPORT_TEXT = 'Техническая поддержка проекта - @managerbotstg'
CORBOTS_TEXT = 'Десятки <a href="https://t.me/corbots">ПОЛЕЗНЫХ БОТОВ</a>, которые пригодятся всем! 👍'
CANCELED = 'Ваша анкета не подтверждена!\n\nВам необходимо заново пройти регистрацию'

DEMO_PROFILES_MAN = [
    '<b>Тимур, 29</b>\n\n<b>Цель знакомств:</b>\nОбщение',
    '<b>Дмитрий, 21</b>\n\n<b>Цель знакомств:</b>\nОбщение\nСерьезные отношения',
    '<b>Олег, 24</b>\n\n<b>Цель знакомств:</b>\nОбщение'
]
DEMO_PROFILES_WOMAN = [
    '<b>Милана, 27</b>\n\n<b>Цель знакомств:</b>\nОбщение',
    '<b>Юля, 23</b>\n\n<b>Цель знакомств:</b>\nОбщение',
    '<b>Алина, 27</b>\n\n<b>Цель знакомств:</b>\nОбщение\nСерьезные отношения'
]