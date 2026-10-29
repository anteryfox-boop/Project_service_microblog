# Project_service_microblog (Корпоративный сервис микроблогов)

Бэкэнд-часть корпоративного сервиса микроблогов (аналог Twitter). Проект реализован
на FastApi, работает в связке с PostgreSQL, Nginx, упаковано в Docker.

## Стек технологий:
*   **Язык:** Python 3.13
*   **Фреймворк:** FastAPI + Uvicorn
*   **База данных:** PostgreSQL 15
*   **ORM:** SQLAlchemy 2.0 (асинхронный)
*   **Веб-сервер / Прокси:** Nginx
*   **Контейнеризация:** Docker, Docker Compose

## Как запустить проект

1. Для запуска нужно клонировать репозиторий и перейти  в папку с проектом:
-bash:
git clone https://github.com/anteryfox-boop/Project_service_microblog.git
cd Project_service_microblog
2. Создать файл .env в корне проекта и указать настройки подключения к БД:
   DATABASE_URL=postgresql+asyncpg://olga:secret@postgres_db:5432/microblog
3. Запустить сборку и поднятие контейнеров:
    docker compose up -d --build
   После запуска автоматически выполнится скрипт entrypoint.sh( заполнит базу данных тестовыми данными, создаст таблицы)
4. Приложение будет доступно по адресу: http://localhost:8001


## Аутентификация

Для тестирование на фронтеде можно использовать следующие ключи из базы данных:
- test (пользователь Test User)

- cooldev (пользователь Cool Dev)

- olga (пользователь Olga)

## Документация API(Swagger):
После запуска проекта документация будет доступна по адресу:
 http://localhost:8001/docs

## Структура проекта:
- app/ - основной код бэкэнда(роутеры, модели, схемы)
- dist/ - статический фронтед
- media/ - папка для загружаемых пользователями картинок
- nginx/ - конфигурация веб-сервера Nginx
- tests/ - папка с тестами
- docker-compose.yml - описание (Nginx, FastApi, PostgreSQL)
- seed_db.py - скрипт заполнеия базы тестовыми данными
- init_db.py -скрипт создания таблиц
