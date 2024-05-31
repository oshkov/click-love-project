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
app.mount('/photos', StaticFiles(directory='photos'), name='photos')
templates = Jinja2Templates(directory="web_registration/templates")


# Вход на регистрацию
@app.get('/registration/{user_id}/{username}')
async def start_registration(
    user_id,
    username,
    request: Request,
    session = Depends(database.get_session)
):

    # Получение данных об анкете пользователя
    profile_info = await database.get_profile_information(session, user_id)

    # Если есть анкета, то проверяется ее статус
    if profile_info:

        # Если анкета была отменена, то отправляет на регистрацию 
        if profile_info.status == 'canceled':
            return templates.TemplateResponse(
                request=request,
                name="registration.html"
            )

        # Словарь с ошибками
        error_messages = {
            'banned': app_texts.BANNED,
            'blocked': app_texts.BLOCKED,
            'open': app_texts.WITH_PROFILE,
            'closed': app_texts.WITH_PROFILE,
            'wait': app_texts.WAIT_PROFILE
        }

        # Проверка статуса анкеты и установка сообщения об ошибке
        error_message = error_messages.get(profile_info.status)

        # В случае иной ошибки
        if error_message == None:
            error_message = app_texts.SUPPORT_TEXT

        # Данные для шаблона
        context = {
            'request': request,
            'error_title': None,
            'error_message': error_message
        }

        return templates.TemplateResponse(
            "error.html",
            context
        )

    return templates.TemplateResponse(
        request=request,
        name="registration.html"
    )


# Отправка данных для регистрации в бд
@app.post('/registration/{user_id}/{username}')
async def registration(
    user_id,
    username,
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    city: str = Form(...),
    preferences: str = Form(...),
    target: list = Form(None),
    main_photo: list[UploadFile] = File(...),
    more_photos: list[UploadFile] = File(None),
    about = Form(None),
    session = Depends(database.get_session)
):

    try:
        # Создаем новый массив, начиная с элементов main_photo
        photos = main_photo.copy()

        # Добавляем элементы из more_photos, если они есть
        if more_photos[0].filename != '':
            photos.extend(more_photos)

        # Скачивание фото и получения массива с именами фото
        photo_list = await database.download_photos(user_id, photos, UPLOAD_FOLDER)

        # Если произошла ошибка в скачивании фото
        if photo_list['response'] is False:

            # Обработка сообщения об ошибке
            error = str(photo_list['error'])
            error_message = error.replace('/', '-')

            # Переадресация
            response = RedirectResponse(url=f'/error/{user_id}/{username}/{error_message}', status_code=301)
            return response


        # Получение данных об анкете пользователя
        profile_info = await database.get_profile_information(session, user_id)

        # Если анкеты не было, то она создается
        if profile_info is None:
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

            # Создание анкеты
            create_profile = await database.create_profile(session, profile_info)

        # Если анкета была отменена, то ее данные обновляются
        elif profile_info.status == 'canceled':
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

            # Обновление анкеты
            create_profile = await database.update_profile(session, profile_info)


        # Если произошла ошибка в создании анкеты
        if create_profile['response'] is False:

            # Обработка сообщения об ошибке
            error = str(create_profile['error'])
            error_message = error.replace('/', '-')

            # Переадресация
            response = RedirectResponse(url=f'/error-creation/{user_id}/{username}/{error_message}', status_code=301)
            return response


        # Уведомление админам об анкете
        await database.notify_admins(session)

        # Сообщению пользователю
        status = create_profile['profile_status']
        await database.success_message(user_id, status)

        # Переадресация
        response = RedirectResponse(url=f'/success-created', status_code=301)
        return response

    # Обработка прочих ошибок
    except Exception as error:
        # Обработка сообщения об ошибке
        error_message = str(error).replace('/', '-')

        # Переадресация
        response = RedirectResponse(url=f'/error/{user_id}/{username}/{error_message}', status_code=301)
        return response


# Страница при успешной регистрации
@app.get('/success-{status}')
async def success(
    status,
    request: Request
):
    
    if status == 'created':
        title = 'Ваша анкета успешно создана!'
    elif status == 'updated':
        title = 'Ваша анкета успешно обновлена!'
    
    # Данные для шаблона
    context = {
        'request': request,
        'title': title,
        'message': None
    }

    return templates.TemplateResponse(
        'success_page.html',
        context
    )


# Страница при ошибки регистрации или редактировании анкеты
@app.get('/error-{status}/{user_id}/{username}/{error_message}')
async def error(
    status,
    user_id,
    username,
    error_message,
    request: Request
):
    
    if status == 'creation':
        error_title = 'Не удалось создать анкету'
    elif status == 'update':
        error_title = 'Не удалось обновить анкету'
    
    # Данные для шаблона
    context = {
        'request': request,
        'error_title': error_title,
        'error_message': error_message
    }

    return templates.TemplateResponse(
        'error.html',
        context
    )


# Страница при любой ошибке
@app.get('/error/{user_id}/{username}/{error_message}')
async def another_errors(
    user_id,
    username,
    error_message,
    request: Request
):

    # Данные для шаблона
    context = {
        'request': request,
        'error_title': None,
        'error_message': error_message
    }

    return templates.TemplateResponse(
        'error.html',
        context
    )


# Страница при любой ошибке
@app.get('/license')
async def another_errors(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="license.html",
    )


# Вход на изменение анкеты
@app.get('/edit_profile/{user_id}/{username}')
async def start_edit_profile(
    user_id,
    username,
    request: Request,
    session = Depends(database.get_session)
):

    # Получение данных о пользователе
    profile_info = await database.get_profile_information(session, user_id)

    if profile_info is None:
        error_message = 'Такой анкеты не существует'

        # Данные для шаблона
        context = {
            'request': request,
            'error_title': None,
            'error_message': error_message
        }

        return templates.TemplateResponse(
            "error.html",
            context
        )
    
    elif profile_info.status == 'banned' or profile_info.status == 'blocked':
        # Словарь с ошибками
        error_messages = {
            'banned': app_texts.BANNED,
            'blocked': app_texts.BLOCKED,
        }

        # Проверка статуса анкеты и установка сообщения об ошибке
        error_message = error_messages.get(profile_info.status)

        # Данные для шаблона
        context = {
            'request': request,
            'error_title': None,
            'error_message': error_message
        }

        return templates.TemplateResponse(
            "error.html",
            context
        )
    
    elif profile_info.status not in ['open', 'closed', 'canceled', 'wait']:

        error_message = app_texts.SUPPORT_TEXT

        # Данные для шаблона
        context = {
            'request': request,
            'error_title': None,
            'error_message': error_message
        }

        return templates.TemplateResponse(
            "error.html",
            context
        )


    context = {
        "request": request,
        "profile_info": profile_info
    }

    return templates.TemplateResponse(
        "edit_profile.html",
        context
    )


# Отправка данных для изменения анкеты
@app.post('/edit_profile/{user_id}/{username}')
async def edit_profile(
    user_id,
    username,
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    city: str = Form(...),
    preferences: str = Form(...),
    target: list = Form(None),
    main_photo: list[UploadFile] = File(...),
    more_photos: list[UploadFile] = File(...),
    about = Form(None),
    session = Depends(database.get_session)
):

    try:
        # Получение данных о пользователе
        profile_info = await database.get_profile_information(session, user_id)

        # Если были загружены фото
        new_photos = None
        if main_photo[0].filename != '' or more_photos[0].filename != '':

            # Если есть имя первого файла в загрузке главного фото, то фотографии были обновлены
            if main_photo[0].filename != '':
                # Скачивание фото
                main_photo_info = await database.download_photo_by_one(user_id, main_photo[0], 0, UPLOAD_FOLDER)

                # Если произошла ошибка в скачивании фото
                if main_photo_info['response'] is False:

                    # Обработка сообщения об ошибке
                    error = str(main_photo_info['error'])
                    error_message = error.replace('/', '-')

                    # Создаем объект переадресации
                    response = RedirectResponse(url=f'/error/{user_id}/{username}/{error_message}', status_code=301)
                    return response

            else:
                main_photo_info = None

            # Если есть имя первого файла в загрузке остальных фото, то фотографии были обновлены
            if more_photos[0].filename != '':
                num = 1
                more_photo_names = []
                for photo in more_photos:
                    more_photo_info = await database.download_photo_by_one(user_id, photo, num, UPLOAD_FOLDER)
                    more_photo_names.append(more_photo_info['photo_name'])
                    num += 1

                    # Если произошла ошибка при скачивании фото
                    if more_photo_info['response'] is False:

                        # Обработка сообщения об ошибке
                        error = str(main_photo_info['error'])
                        error_message = error.replace('/', '-')

                        # Создаем объект переадресации
                        response = RedirectResponse(url=f'/error/{user_id}/{username}/{error_message}', status_code=301)
                        return response

            else:
                more_photo_names = None

            # Если обновлены главное и прочие фото
            if main_photo_info and more_photo_names:
                new_photos = [main_photo_info['photo_name']] + more_photo_names

            # Если обновлено только главное фото
            elif main_photo_info:
                # Добавление фото в массив в качестве первого элемента
                new_photos = [main_photo_info['photo_name']] + profile_info.photos[1:]

            # Если обновлены только прочие фото
            elif more_photo_names:
                # Добавление в массив фото после первого фото
                new_photos = [profile_info.photos[0]] + more_photo_names


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
            'photo_list': new_photos
        }

        # Создание или обновление анкеты
        update_profile = await database.update_profile(session, profile_info)

        # Если произошла ошибка в создании анкеты
        if update_profile['response'] is False:

            # Обработка сообщения об ошибке
            error = str(update_profile['error'])
            error_message = error.replace('/', '-')

            # Создаем объект переадресации
            response = RedirectResponse(url=f'/error-update/{user_id}/{username}/{error_message}', status_code=301)
            return response
        
        # Уведомление админам об анкете
        await database.notify_admins(session)

        # Сообщению пользователю
        status = update_profile['profile_status']
        await database.success_message(user_id, status)

        # Переадресация
        response = RedirectResponse(url=f'/success-updated', status_code=301)
        return response

    # Обработка прочих ошибок
    except Exception as error:
        # Обработка сообщения об ошибке
        error_message = str(error).replace('/', '-')

        # Создаем объект переадресации
        response = RedirectResponse(url=f'/error/{user_id}/{username}/{error_message}', status_code=301)
        return response