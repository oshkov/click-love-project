from fastapi import FastAPI, UploadFile, Request, Depends, Form, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import config

from web_registration.database import DataBase
import web_registration.app_texts as app_texts


database = DataBase(config.DATABASE_URL)

app = FastAPI(title='Registration')

UPLOAD_FOLDER = 'photos/'

app.mount('/web_registration/static', StaticFiles(directory='web_registration/static'), name='static')
templates = Jinja2Templates(directory="web_registration/templates")


# Вход на регистрацию
@app.get('/registration/{user_id}/{username}')
async def main(
    user_id,
    username,
    request: Request,
    session = Depends(database.get_session)
):

    # Получение данных о пользователе
    user_info = await database.get_profile_information(session, user_id)

    # Если есть анкета, то проверяется ее статус
    if user_info:
        # Если анкета забанена, то выводит ошибку
        if user_info.status == 'banned':
            error_message = app_texts.BANNED

            # Создаем объект переадресации
            response = RedirectResponse(url=f'/error/{user_id}/{username}/{error_message}', status_code=301)
            return response

        # Если анкета заморожена, то выводит ошибку
        elif user_info.status == 'blocked':
            error_message = 'Вы сможете изменить анкету только после разморозки вашего профиля админами'

            # Создаем объект переадресации
            response = RedirectResponse(url=f'/error/{user_id}/{username}/{error_message}', status_code=301)
            return response

    return templates.TemplateResponse(
        request=request, name="index.html"
    )


# Отправка данных для регистрации в бд
@app.post('/registration/{user_id}/{username}')
async def aaaaaaaaa(
    user_id,
    username,
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    city: str = Form(...),
    preferences: str = Form(...),
    target: list = Form(None),
    photos: list[UploadFile] = File(...),
    about = Form(None),
    session = Depends(database.get_session)
):

    try:
        # Скачивание фото и получения массива с именами фото
        photo_list = await database.download_photos(user_id, photos, UPLOAD_FOLDER)

        # Если произошла ошибка в скачивании фото
        if photo_list['response'] is False:

            # Обработка сообщения об ошибке
            error = str(photo_list['error'])
            error_message = error.replace('/', '-')

            # Создаем объект переадресации
            response = RedirectResponse(url=f'/error/{user_id}/{username}/{error_message}', status_code=301)
            return response


        # Добавление данных о пользователе в словарь
        profile_info = {
            'user_id': user_id,
            'username': username,
            'name': name,
            'gender': gender,
            'preferences': preferences,
            'city': city,
            'age': age,
            'target': target,
            'about': about,
            'photo_list': photo_list['photo_list']
        }

        # Создание или обновление анкеты
        create_profile = await database.create_profile(session, profile_info)

        status = create_profile['profile_status']

        # Если произошла ошибка в создании анкеты
        if create_profile['response'] is False:

            # Обработка сообщения об ошибке
            error = str(photo_list['error'])
            error_message = error.replace('/', '-')

            # Если ошибка в обновлении анкеты
            if status == 'not_updated':
                # Создаем объект переадресации
                response = RedirectResponse(url=f'/error-update/{user_id}/{username}/{error_message}', status_code=301)
                return response

            # Если ошибка в создании анкеты
            elif status == 'not_created':
                response = RedirectResponse(url=f'/error-creation/{user_id}/{username}/{error_message}', status_code=301)
                return response


        # Уведомление админам об анкете
        await database.notify_admins(session)

        # Сообщению пользователю
        await database.success_message(user_id, status)

        # Переадресация
        response = RedirectResponse(url=f'/success-{status}', status_code=301)
        return response

    # Обработка прочих ошибок
    except Exception as error:
        # Обработка сообщения об ошибке
        error = str(photo_list['error'])
        error_message = error.replace('/', '-')

        # Создаем объект переадресации
        response = RedirectResponse(url=f'/error/{user_id}/{username}/{error_message}', status_code=301)
        return response


# Страница при успешной регистрации
@app.get('/success-{status}')
async def main(
    status,
    request: Request
):

    if status == 'created':
        return templates.TemplateResponse(
            request=request, name='success_creation.html'
        )

    elif status == 'updated':
        return templates.TemplateResponse(
            request=request, name="success_update.html"
        )


# Страница при ошибки регистрации
@app.get('/error-{status}/{user_id}/{username}/{error_message}')
async def main(
    status,
    user_id,
    error_message,
    request: Request
):

    if status == 'creation':
        return templates.TemplateResponse(
            request=request,
            name="error_creation.html",
            context={'error_message': error_message, 'user_id': user_id}
        )

    elif status == 'update':
        return templates.TemplateResponse(
            request=request,
            name="error_update.html",
            context={'error_message': error_message, 'user_id': user_id}
        )
    

# Страница при любой ошибке
@app.get('/error/{user_id}/{username}/{error_message}')
async def main(
    user_id,
    error_message,
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={'error_message': error_message, 'user_id': user_id}
    )