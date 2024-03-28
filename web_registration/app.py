import shutil
from fastapi import FastAPI, UploadFile, Request, Depends, Form, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import time
from web_registration.database import get_session, notify_admins, success_message
from models import FormModel


app = FastAPI(
    title='Registration'
)

UPLOAD_FOLDER = 'photos/'


app.mount('/web_registration/static', StaticFiles(directory='web_registration/static'), name='static')
templates = Jinja2Templates(directory="web_registration/templates")


# Вход на регистрацию
@app.get('/registration/{user_id}/{username}')
async def main(user_id, username, request: Request, session = Depends(get_session)):

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
    session = Depends(get_session)
):

    try:
        # Поиск анкеты по user_id
        user_in_db = await session.get(FormModel, user_id)

        # Создание массива с фотками и их скачивание
        photo_list = []
        num = 0
        timenow = time.strftime('%d%m%Y%H%M%S')
        for photo in photos:
            # Имя для фото: дата + номер фото
            photo.filename = f'{user_id}_{timenow}_{num}.jpeg'

            # Добавление фото в список фотографий
            photo_list.append(photo.filename)

            # Скачивание фото
            with open(f'{UPLOAD_FOLDER}/{photo.filename}', 'wb') as buffer:
                shutil.copyfileobj(photo.file, buffer)
            num += 1

        # Если анкета уже была, то ее данные обновляются
        if user_in_db:
            # Обновление данных в бд
            user_in_db.status = 'open'
            user_in_db.name = name
            user_in_db.gender = gender
            user_in_db.preferences = preferences
            user_in_db.city = city
            user_in_db.age = age
            user_in_db.target = target
            user_in_db.about = about
            user_in_db.photos = photo_list
            user_in_db.warns = 0

            try:
                # Добавление данных в бд и сохранение
                await session.commit()

                # Сообщение пользователю в телеграм о создании анкеты
                await success_message(user_id, 'update')

                # Уведомление админам о новой анкете
                await notify_admins()

                # Создаем объект переадресации
                response = RedirectResponse(url='/success-update', status_code=301)

                return response

            except Exception as error:
                error_message = str(error)

                # Создаем объект переадресации
                response = RedirectResponse(url=f'/error-update/{user_id}/{username}/{error_message}', status_code=301)

                return response

        # В случае если анкеты не было - она создается
        else:
            user_info = FormModel(
                creation_date = None,
                id = user_id,
                username = username,
                status = 'open',
                name = name,
                gender = gender,
                preferences = preferences,
                city = city,
                age = age,
                vk_url = None,
                target = target,
                about = about,
                photos = photo_list,
                warns = 0
            )

            try:
                # Добавление данных в сессию
                session.add(user_info)

                # Добавление данных в бд и сохранение
                await session.commit()

                # Сообщение пользователю в телеграм о создании анкеты
                await success_message(user_id, 'creation')

                # Уведомление админам о новой анкете
                await notify_admins()

                # Создаем объект переадресации
                response = RedirectResponse(url='/success-creation', status_code=301)

                return response

            except Exception as error:
                error_message = str(error)
                
                # Создаем объект переадресации
                response = RedirectResponse(url=f'/error-creation/{user_id}/{username}/{error_message}', status_code=301)

                return response
            
    except Exception as error:
        error_message = str(error)
        
        # Создаем объект переадресации
        response = RedirectResponse(url=f'/error/{user_id}/{username}/{error_message}', status_code=301)

        return response


# Страница при успешной регистрации
@app.get('/success-{status}')
async def main(status, request: Request):

    if status == 'creation':
        return templates.TemplateResponse(
            request=request, name='success_creation.html'
        )

    elif status == 'update':
        return templates.TemplateResponse(
            request=request, name="success_update.html"
        )


# Страница при ошибки регистрации
@app.get('/error-{status}/{user_id}/{username}/{error_message}')
async def main(status, user_id, error_message, request: Request):

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
async def main(user_id, error_message, request: Request):

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={'error_message': error_message, 'user_id': user_id}
    )