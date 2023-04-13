# Foodgram - Продуктовый помощник

## Описание

«Продуктовый помощник» — это сайт, на котором можно публиковать собственные рецепты, добавлять чужие рецепты в избранное, подписываться на других авторов и создавать список покупок для заданных блюд.
Вот, что было сделано в ходе работы над проектом:
настроено взаимодействие Python-приложения с внешними API-сервисами;
создан собственный API-сервис на базе проекта Django;
создан Telegram-бот;
подключено SPA к бэкенду на Django через API;
созданы образы и запущены контейнеры Docker;
созданы, развёрнуты и запущены на сервере мультиконтейнерные приложения;
закреплены на практике основы DevOps, включая CI&CD.
Инструменты и стек: #python #JSON #YAML #Django #React #Telegram #API #Docker #Nginx #PostgreSQL #Gunicorn #JWT #Postman

## Стек технологий

- Python 3.7
- Django 3.2
- Django REST Framework
- PostgreSQL
- Nginx
- Gunicorn
- Docker, Docker Hub
- GitHubActions(CI/CD)
- JS

## Установка проекта из репозитория (Linux и macOS)

- Клонировать репозиторий к себе на компьютер:

```bash
https://github.com/PavelPrist/foodgram-project-react.git
cd foodgram-project-react
cd Foodgramm
```

- Cоздать и активировать виртуальное окружение:

```bash
python -m venv venv
```

```bash
. venv/bin/activate
```

- Cоздайте файл `.env` в директории `/infra/` с содержанием:

```bash
cd infra/
touch .env
```

```
echo SECRET_KEY=<тут ваш секртеный ключ от Django> >> .env  можно взять пример из example.env

echo DB_ENGINE=django.db.backends.postgresql >> .env

echo DB_NAME=postgres >> .env

echo POSTGRES_PASSWORD=postgres >> .env

echo POSTGRES_USER=postgres >> .env

echo DB_HOST=db >> .env

echo DB_PORT=5432 >> .env
```

- Установите зависимости из файла requirements.txt:

```bash
cd backend/
pip install -r requirements.txt
```

- Выполните миграции:

```bash
python manage.py migrate
```

- Запустите сервер:

```bash
python manage.py runserver
```

## Запуск проекта в Docker контейнере

- Установите Docker.

Параметры запуска описаны в файлах `docker-compose.yml` и `nginx.conf` которые находятся в директории `infra/`

- Запустите docker compose:

```bash
docker-compose up -d --build
```  

  > После сборки появляются 3 контейнера:
  >
  > 1. контейнер базы данных **db**
  > 2. контейнер приложения **backend**
  > 3. контейнер web-сервера **nginx**
  >
- Выполните миграции:

```bash
docker-compose exec backend python manage.py migrate
```

- Запустите процесс загрузки ингредиентов:

```bash
docker-compose exec backend python manage.py load_ingrs
```

- Запустите процесс загрузки тегов:

```bash
docker-compose exec backend python manage.py load_tags
```

- Создайте суперпользователя:

```bash
docker-compose exec backend python manage.py createsuperuser
```

- Запустите процесс сбора статики:

```bash
docker-compose exec backend python manage.py collectstatic --no-input
```
