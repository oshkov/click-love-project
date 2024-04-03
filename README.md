# Второй проект для компании "Корпорация ботов"

## Телеграм бот знакомств с регистрацией через веб-приложение

### О боте

Бот написан на aiogram

### О сайте

Сайт создан для использования внутри телеграма в качестве веб-приложения. Он использует TelegramAPI для получения id пользователя, передачи данных и закрытия сайта после завершения регистрации.

#### В сайте были использованы
- Python/FastAPI
- JavaScript
- SQLalchemy
- PostgreSQL (async)
- Dadata API (Для поиска всех городов мира)

#### Возможности сайта
- Регистрация выполнена в виде квиза, поэтапно запрашиватся данные о пользователе
- Выбор города представлен в виде поисковой строки и использует Dadata API для поиска всех городов мира
- Загрузка до пяти фотографий размером до 5мб с предпросмотром (JavaScript, размер и количество фото можно редактировать)
- Фото скачиваются после завершения регистрации и сохраняются в папку /photos
- После регистрации в базе данных создается запись со всеми данными пользователя, сайт закрывается и пользователь получает возможность пользоваться ботом

## Запуск

Запуск осуществлять из папки с проектом: click_love_project/

   Для запуска сайта:
   ```python
   uvicorn web_registration.app:app --host 0.0.0.0
   ```

   Для запуска бота:
   ```python
   python bot_start.py
   ```

## Статусы

Каждая анкета имеет свой статус:
- **wait** - Статус после регистрации или изменения анкеты (Ожидание подтверждения админами)
- **open** - Открытая анкета
- **closed** - Закрытая анкета (Для скрытия анкеты от других людей)
- **blocked** - Временно заблокированная анкета (Ожидание подтверждения админами после 3 жалоб)
- **banned** - Заблокированная анкета