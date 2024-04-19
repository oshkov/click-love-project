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