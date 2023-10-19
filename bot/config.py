import os

API_URL = os.getenv('API_URL')
CRYPTO_KEY = os.getenv('CRYPTO_KEY', '')

DEFAULT_RATE_LIMIT = 0.3

CHANGE_BOX_STATUS_THROTTLE_KEY = '{box_id}_change_status'

EXIST_ENDPOINT = 'user/{telegram_id}/exist'
ACTIVE_ENDPOINT = 'user/{telegram_id}/active'
NEW_USER_ENDPOINT = 'user'
ALL_DOMAINS_ENDPOINT = 'email-domain'
NEW_BOX_ENDPOINT = 'user/{telegram_id}/boxes'
MY_BOX_ENDPOINT = 'user/{telegram_id}/boxes'
CHANGE_BOX_STATUS_ENDPOINT = 'user/{telegram_id}/boxes/{box_id}/change-status'

INSTRUCTIONS_MESSAGE = """
Чтобы успешно добавить почтовый ящик необходимо:\n
1️⃣ В настройках вашего почтового ящика нужно разрешить
    доступ по протоколу IMAP.\n
2️⃣ При включенной двухфакторной аутентификации
    необходимо создать в почтовом ящике специалный
    пароль для приложений.\n
3️⃣ Добавить почтовый ящик с помощью команды
    'Добавить ящик' в меню бота.\n
В случае проблем с функционалом бота попробуйте
выполнить команду /start для возврата в главное меню.
"""
UNKNOWN_MESSAGE = (
    'Неизвестная команда.\n\nВоспользуйтесь кнопками'
    ' меню или выполните команду /start'
)
START_MESSAGE = 'Привет! 👋\nС возвращением!'
START_UNREG_MESSAGE = (
    'Привет! 👋\nДля того, чтобы воспользоваться '
    'полным функционалом, зарегистрируйтесь.'
)
SUCCESS_REG_MESSAGE = 'Вы успешно зарегистрировались! 🥳'
CANCEL_MESSAGE = 'Действие отменено.'
API_ERROR_MESSAGE = (
    'Бот недоступен. 🤷\nОбратитесь к администратору или попробуйте позже.'
)
CHOOSE_DOMAIN_MESSAGE = '1️⃣ Выберите почтовый сервис нового ящика'
ERROR_DOMAIN_MESSAGE = (
    'Неизвестный сервис. 🤷\nВыберите корректный почтовый сервис нового ящика'
)
ENTER_USERNAME_MESSAGE = '2️⃣ Введите адрес электронной почты'
ERROR_EMAIL_ENTER_MESSAGE = (
    'Введенный текст не является адресом электронной почты.\nПовторите ввод.'
)
ENTER_PASSWORD_MESSAGE = '3️⃣ Введите пароль'
PASSWORD_ACCEPTED_MESSAGE = 'Пароль принят. 🆗\n\n'
NEED_ONE = 'К почтовому ящику нужно добавить минимум один фильтр.\n\n'
ENTER_FILTERS_MESSAGE = (
    '4️⃣ Введите адрес почты отправителя, от которого вы хотите получать почту'
    ' в бота, и через пробел псевдоним для него.\n\nПример ввода:\n'
    'example@example.com Гвидо Ван Россум\n\n Псевдонима фильтра может быть '
    'пустым.\n\nПример ввода:\nexample@example.com'
)
ERROR_ALIAS_MESSAGE = 'Псевдоним фильтра не должен быть длинее 128 символов.'
ANOTHER_FILTER_MESSAGE = (
    'Фильтр успешно добавлен. 🆗\nДобавить еще один фильтр или завершить ввод?'
)
APPROVE_MESSAGE = (
    'Подтвердите добавление нового ящика:\n\n'
    'Адрес почты: {email}\n'
    '\nФильтры:\n{filters}'
)
SUCCESS_NEW_BOX_MESSAGE = 'Почтовый ящик успешно добавлен!'
EMPTY_BOX_LIST_MESSAGE = 'У вас пока нет отслеживаемых почтовых ящиков.'
ERROR_BOX_CHOOSE_MESSAGE = (
    'Выбран некорректный ящик. 🤷\nВыберите ящик из предложенных.'
)
MY_BOXES_MESSAGE = 'Выберите почтовый ящик:'
ONE_BOX_MESSAGE = 'Адрес: {email}\n\nСтатус: {status}'
ERROR_CHANGE_BOX_STATUS_MESSAGE = 'Почтовый ящик уже находится в этом статусе.'
SUCCESS_CHANGE_BOX_STATUS_MESSAGE = 'Статус почтового ящика успешно изменен!'
BAN_MESSAGE = 'Ваш аккаунт заблокирован. ❌\nОбратитесь к администратору.'

DOMAINS_CHUNK_SIZE = 3
