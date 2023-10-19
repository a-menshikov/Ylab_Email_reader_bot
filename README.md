# Чат-бот для чтения электронной почты

Выполнен в рамках стажировки в компании Y_lab, которая проходила с августа по октябрь 2023 года.

Позволяет получать новые письма электронной почты в чат-боте для Telegram. Поддерживает возможность отслеживания нескольких ящиков и фильтрации писем по их отправителям.

## Основные технологии разработки продукта

- Python 3.10
- Django 4.1 (async)
- Aiogram
- Celery
- Flower
- PostgreSQL 15
- Redis
- Docker

## Развертывание проекта

### Требования

- Установленный Docker и Docker Compose
- GNU Make

### Инструкция

1. Склонируйте репозиторий

   ```bash
   git clone <ссылка на репозиторий>
   ```

2. Создайте файл .env и заполните его по примеру .env_example своими данными
3. Поднимите контейнеры

   ```bash
   make up-d
   ```

4. Примените миграции

   ```bash
   make migrate
   ```

5. Соберите статику

   ```bash
   make collectstatic
   ```

6. Чтобы остановить контейнеры, выполните команду

   ```bash
   make down
   ```

## High-level design

![HLD](./readme_images/HLD.png)

## Схема БД проекта

![DB](./readme_images/database.png)

## Use cases

1. Регистрация пользователя в боте

    ![UC_registration](./readme_images/uc_registration.png)

2. Добавление пользователем нового почтового ящика для отслеживания

    ![UC_add_email_box](./readme_images/uc_add_email_box.png)

3. Получение пользователем нового email-сообщения от бота

    ![UC_new_email_message](./readme_images/uc_new_email_message.png)

## Примеры использования специфических методов

- После успешного запуска проекта, откройте <http://localhost:8000/api/v1/docs> для доступа к документации по api проекта

## Контакты

**telegram** [@Menshikov_AS](https://t.me/Menshikov_AS)  
**e-mail** <a.menshikov1989@gmail.com>
