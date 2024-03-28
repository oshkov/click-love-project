# ТЕКСТА
async def PREVIEW_FORM_TEXT(data_json):
    target_text = ", ".join(data_json['target'])
    return f'❕ Проверьте свою анкету и подтвердите ее создание\n\nВаше имя: {data_json["name"]}\nПол: {data_json["gender"]}\nХочешь знакомиться: {data_json["preferences"]}\nЦели знакомства: {target_text}'

async def FORM_TEXT(name, age, city, about, targets):
    target_text = "\n".join(targets)
    if about is None:
        about = ''
    else:
        about = f'\n\n{about}'
    return f'<b>{name}, {age}, г.{city}</b>{about}\n\n<b>Цели знакомств:</b>\n{target_text}'

async def MENU_TEXT(status):
    if status == 'open':
        status_text = '\n\n🤗 Ваша анкета открыта'
    elif status == 'closed':
        status_text = '\n\n🙈 Ваша анкета скрыта от других людей'
    elif status == 'wait':
        status_text = '\n\n❗️ Ваша анкета еще не подтверждена администраторами'
    elif status == 'blocked':
        status_text = '\n\n🥶 Ваша анкета заморожена'
    elif status == 'banned':
        status_text = '\n\n🔒Ваша анкета заблокирована'
    return f'🏠 Главное меню{status_text}'

async def MUTUAL_LIKE_PREVIEW(form):
    name = form.name
    age = form.age
    city = form.city
    about = form.about
    target = form.target
    username = form.username

    return f'Взаимный лайк ❤️\n\n{await FORM_TEXT(name, age, city, about, target)}\n\nНачинайте общение: @{username}'


START_TEXT_NEW_USER = 'Как это работает? 🥳\n\n✅ Регистрируйся\n👀 Смотри анкеты\n📍 Находи людей рядом\n❤️ Ставь лайки\n👩‍❤️‍💋‍👨 Получай взаимные лайки\n✍️ Общайся\n😘 Влюбляйся'
START_TEXT = 'У вас уже есть анкета, если хотите изменить ее, то воспользуйтесь клавиатурой 👇'
CREATE_USERNAME = 'Чтобы пользоваться ботом, вам нужен @юзернейм, по нему люди смогут связаться с тобой\n\nОн создается в настройках телеграма в пару кликов'
RECREATE_FORM_TEXT = 'Чтобы редактировать свою анкету нужно заново пройти регистрацию'
SUCCESS_FORM_CREATE_TEXT = 'Ваша анкета успешно создана'
CHECK_BOT = 'Подтвердите, что вы не робот'
MAKE_WARN = 'Жалоба отправлена, анкета будет проверена администраторами!'
NO_FORMS = 'Подходящих для вас анкет, к сожалению, нет'
WAITED_FORM = 'Ваша анкета еще не подтверждена'
MUTUAL_LIKE = 'У вас взаимный лайк 😍'
YOU_LIKED = 'Ваша анкета понравилась одному человеку 🤗'
BLOCKED = 'Твой аккаунт временно заморожен из-за жалоб других пользователей'