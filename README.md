# Проект: Foodgram
Проект Foodgram дает возможность пользователям создавать и хранить рецепты на онлайн-платформе. Кроме того, можно скачать список продуктов, необходимых для приготовления блюда, просмотреть рецепты друзей и добавить любимые рецепты в список избранных.


## Технологии
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Django REST Framework](https://img.shields.io/badge/Django%20REST%20Framework-092E20?style=for-the-badge&logo=django&logoColor=white)
![Djoser](https://img.shields.io/badge/Djoser-092E20?style=for-the-badge&logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)

## Запуск проекта локально
Клонировать репозиторий:
```bash
git clone <https or SSH URL>
```
Перейти в директорию проекта
```bash
cd foodgram
```
или
```bash
cd foodgram-main
```
Создать .env:
```bash
touch .env
```
```bash
# Django
DEBUG=True
SECRET_KEY=django-insecure--(htnx8z%fz_s2!!x-jse*gfjl^j46&t#1my96mbxg#0a947s%
ALLOWED_HOSTS=127.0.0.1;localhost;<your_ip>;<your_domen_name>

# DB
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432

# SuperUser for admin zone
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@admin.admin
ADMIN_PASSWORD=admin
```
Собрать контейнера:
```bash
docker compose -f docker-compose.yml up
```
Выполнить заполнение базы ингредиентами:
```bash
docker compose exec backend python manage.py load_csv
```
После успешного запуска, проект доступен по http://127.0.0.1:8000.
