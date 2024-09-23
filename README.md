# Проект Foodgram

Гастрономическая социальная сеть. Создавайте рецепты, обменивайтесь избранными, получайте точную информацию о необходимых покупках для приготовления всего, что выберете

## Развертывание проекта

Установите и разверните виртуальное окружение:

```
python3 -m venv env
source venv/bin/activate
```

Установите зависимости:
```
pip install -r requirements.txt
```

Выполнить миграции и запустить сервер для локального использования:
```
python3 manage.py migrate
```

Локальный запуск:
```
python3 manage.py runserver
```

## Запуск на удаленном сервере:
Скачайте/скопируйте файл dcoker-compose.production.yml
Заполните файл .env (требуются переменные: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, DB_HOST, DB_PORT, SECRET_KEY, HOST_IP, HOST_DOMAIN)
Настройте внешний nginx на проксирование запросов к домену foodgram на порт 80 контейнера.
Создайте Docker compose.

## Технологии

Использованные технологии:

- Django 3.2.16
- djangorestframework 3.12.4
- djoser

Для более подробного обзора использованных технологий посетите файл requirements.txt.

При промышленном развертывании проекта использован Docker, gunicorn 20.1.0, nginx.

## Автор

Исхаков Руслан, студент Яндекс Практикума.
ruslan_iskhak@mail.ru
