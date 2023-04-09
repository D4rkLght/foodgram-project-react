![foodgram_workflow](https://github.com/D4rkLght/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
### Стек технологий
[![Python](https://img.shields.io/badge/-Python-464641?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-464646?style=flat-square&logo=django)](https://www.djangoproject.com/)
[![Pytest](https://img.shields.io/badge/Pytest-464646?style=flat-square&logo=pytest)](https://docs.pytest.org/en/6.2.x/)
[![Docker](https://img.shields.io/badge/Docker-464646?style=flat-square&logo=docker)](https://hub.docker.com/)
[![Postgresql](https://img.shields.io/badge/Postgres-464646?style=flat-square&logo=POSTGRESQL)](https://www.postgresql.org/)

# Проект Foodgram
Foodgram, «Продуктовый помощник». Онлайн сервис для публикации рецептов. Имеется возможность подписки на автора рецепта и добавление 
рецептов в избранное. Также можно скачать список продуктов на выбранные рецепты. 

### Установка:
Создайте директорию infra/:
~~~
mkdir infra
~~~
В директории создать файл infra/.env и наполнить: 
- DB_ENGINE=django.db.backends.postgresql
- DB_NAME= # название дб
- POSTGRES_USER= # имя пользователя
- POSTGRES_PASSWORD= # пароль
- DB_HOST=db
- DB_PORT=5432

Из папки infra/ соберите образ:
```
docker-compose up -d
```
Миграции:
```
docker-compose exec web python manage.py migrate
```
Сбор статики:
```
docker-compose exec web python manage.py collectstatic --no-input
```
Создание суперюзера:
```
docker-compose exec web python manage.py createsuperuser
```
Резервная копия:
```
docker-compose exec web python manage.py dumpdata > fixtures.json 
```
# Примеры запросов:
http://localhost/redoc/ http://localhost/admin/
## Над проектом работал:
Разработчик [Ярослав Андреев ](https://github.com/D4rkLght).