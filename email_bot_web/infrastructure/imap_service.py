import asyncio
import email
import logging
import re
from asyncio import wait_for
from email.header import decode_header
from email.message import Message
from email.parser import BytesHeaderParser
from email.utils import parseaddr
from typing import Collection

import aioimaplib
from django.conf import settings

from infrastructure.error_messages import (
    IMAP_AUTHENTICATION_FAILED,
    IMAP_CONNECTION_ERROR,
    SERVER_UNAVAILABLE,
)
from infrastructure.exceptions import (
    ImapAuthenticationFailed,
    ImapConnectionError,
    ServerUnavailable,
)
from infrastructure.redis_service import redis_client
from infrastructure.repository import Repository
from infrastructure.tasks import (
    email_html_to_image,
    send_image_to_telegram_task,
)
from infrastructure.template import HTML_FORMAT

ID_HEADER_SET = {'Content-Type', 'From', 'To', 'Cc', 'Bcc', 'Date', 'Subject',
                 'Message-ID', 'In-Reply-To', 'References'}

FETCH_MESSAGE_DATA_UID = re.compile(rb'.*UID (?P<uid>\d+).*')

logger = logging.getLogger('imap')
repo = Repository()


class EmailMessageService:
    """Сервис для работы с новыми письмами."""

    async def extract_text_parts(self, message: Message) -> list[str]:
        """Извлечь текстовые части из письма."""
        text_parts = []
        if message.is_multipart():
            for part in message.get_payload():
                if part.get_content_type() in ('text/plain', 'text/html'):
                    text_parts.append(part.get_payload(decode=True).decode())
                elif part.is_multipart():
                    text_parts.extend(await self.extract_text_parts(part))
        else:
            text_parts.append(message.get_payload(decode=True).decode())
        return text_parts

    async def extract_attach_names(self, message: Message) -> list[str]:
        """Извлечь названия приложенных файлов."""
        attach_names = []
        for part in message.walk():
            if part.get_content_type() not in ('text/plain', 'text/html'):
                attachment_filename = part.get_filename()
                if attachment_filename:
                    decoded_parts = decode_header(attachment_filename)
                    decoded_filename = ''
                    for part, encoding in decoded_parts:
                        if isinstance(part, bytes):
                            decoded_filename += str(part.decode(
                                encoding or 'utf-8',
                            ))
                        else:
                            decoded_filename += str(part)
                    attach_names.append(decoded_filename)
        return attach_names

    async def process_new_message(
        self,
        message: Message,
        box_id: int,
        telegram_id: int,
        username: str,
    ) -> None:
        """Обработать новое письмо."""
        logger.info(f'BOX {box_id}. Processing new message.')
        sender = message['From']
        sender_email = parseaddr(sender)[1]

        filters = await repo.filter.get_box_filters_value_list(
            box_id=box_id,
            telegram_id=telegram_id,
        )
        for filter in filters:
            if sender_email == filter[0]:
                sender_email = f'{filter[0]} {filter[1]}'
                break
        else:
            logger.info(f'BOX {box_id}. New message sender not in filters.')
            return None

        subject = message['Subject']
        if subject:
            decoded_subject = decode_header(subject)[0][0]
            if isinstance(decoded_subject, bytes):
                decoded_subject = decoded_subject.decode()
        else:
            decoded_subject = ''

        logger.info(f'BOX {box_id}. Extracting text.')
        raw_text = await self.extract_text_parts(message)
        logger.info(f'BOX {box_id}. Extracting attachments.')
        attaches = await self.extract_attach_names(message)

        message_data = {
            'From': sender_email,
            'To': username,
            'Subject': decoded_subject,
            'Text': raw_text,
            'Attachments': attaches,
        }
        logger.info(f'BOX {box_id}. Message prepare.')

        html_mail = await self.email_to_html(message_data)
        email_html_to_image.apply_async(
            args=(html_mail,),
            link=send_image_to_telegram_task.s(telegram_id=telegram_id),
        )

    async def email_to_html(
        self,
        email_data: dict[str, str | list[str]],
    ) -> str:
        """Получения HTML для генерации изображения."""
        html = HTML_FORMAT.format(
            sender=email_data['From'],
            recipient=email_data['To'],
            subject=email_data['Subject'],
            text=''.join(email_data['Text']),
            attachments=' | '.join(email_data['Attachments']),
        )
        return html


class IMAPClient:
    """Клиент для работы с почтовыми ящиками."""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        telegram_id: int,
        box_id: int,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.telegram_id = telegram_id
        self.box_id = box_id
        self.current_max_uid = 1
        self.redis = redis_client
        self.restart_loop = False
        self.mail_processor = EmailMessageService()

    @classmethod
    async def check_connection(
        cls,
        host: str,
        port: int,
        username: str,
        password: str,
    ) -> None:
        """Проверка соединения с почтовыми ящиками."""
        try:
            check_client = aioimaplib.IMAP4_SSL(
                host=host,
                port=port,
                timeout=20,
            )
            await check_client.wait_hello_from_server()
        except (ConnectionRefusedError, asyncio.exceptions.TimeoutError):
            logger.error(f'USERNAME {username} HOST {host} connection error.')
            raise ServerUnavailable(SERVER_UNAVAILABLE)
        response = await check_client.login(
            user=username,
            password=password,
        )
        if response.result != 'OK':
            for line in response.lines:
                if b'ALERT' in line:
                    logger.error(f'USERNAME {username} alert login response.')
                    raise ImapConnectionError(IMAP_CONNECTION_ERROR)
                if b'AUTHENTICATIONFAILED' in line or response.result == 'NO':
                    logger.error(f'USERNAME {username} authentication failed.')
                    raise ImapAuthenticationFailed(IMAP_AUTHENTICATION_FAILED)

    async def fetch_messages_headers(
        self,
        imap_client: aioimaplib.IMAP4_SSL,
        max_uid: int,
        username: str,
        return_message: bool,
    ) -> int:
        """Получить заголовки писем,
        при новом письме - отправить на обработку."""
        logger.info(f'BOX {self.box_id}. Fetching start.')
        response = await imap_client.uid(
            'fetch', '%d:*' % (max_uid),
            '(UID FLAGS BODY.PEEK[HEADER.FIELDS (%s)])' % ' '.join(
                ID_HEADER_SET,
            ),
        )
        new_max_uid = max_uid
        last_message_headers = None
        if response.result == 'OK':
            logger.info(f'BOX {self.box_id}. Fetching OK response.')
            fetch_command_without_literal = b'%s %s' % (
                response.lines[-4],
                response.lines[-2],
            )
            match_result = FETCH_MESSAGE_DATA_UID.match(
                fetch_command_without_literal,
            )
            if match_result:
                uid = int(match_result.group('uid'))
                last_message_headers = BytesHeaderParser().parsebytes(
                    response.lines[-3],
                )
                new_max_uid = uid
            if last_message_headers and return_message:
                logger.info(f'BOX {self.box_id}. Handling new mail.')
                dwnld_resp = await imap_client.uid(
                    'fetch',
                    str(uid),
                    'BODY.PEEK[]',
                )
                raw_email = dwnld_resp.lines[1]
                decode_message = email.message_from_bytes(raw_email)
                await self.mail_processor.process_new_message(
                    message=decode_message,
                    box_id=self.box_id,
                    telegram_id=self.telegram_id,
                    username=username,
                )
        return new_max_uid

    async def handle_server_push(
        self,
        push_messages: Collection[bytes],
    ) -> bool:
        """Обработка ответа imap сервера."""
        for msg in push_messages:
            if msg.endswith(b'EXISTS'):
                logger.info(f'BOX {self.box_id}. New message exists.')
                return True
            elif msg.endswith(b'EXPUNGE'):
                logger.info(f'BOX {self.box_id}. Message removed: %r' % msg)
            elif b'FETCH' in msg and br'\Seen' in msg:
                logger.info(f'BOX {self.box_id}. Message seen %r' % msg)
            else:
                logger.info(f'BOX {self.box_id}. Another push : %r' % msg)
        return False

    async def imap_loop(self) -> None:
        """Loop для работы с почтовыми ящиками."""
        try:
            logger.info(f'BOX {self.box_id}. Connecting IMAP.')
            imap_client = aioimaplib.IMAP4_SSL(
                host=self.host,
                port=self.port,
                timeout=60,
            )
            await imap_client.wait_hello_from_server()

            logger.info(f'BOX {self.box_id}. Logining in IMAP.')
            await imap_client.login(self.username, self.password)

            select_response = await imap_client.select('INBOX')

            for i in select_response[1]:
                if b'UIDNEXT' in i:
                    match = re.search(r'UIDNEXT (\d+)', i.decode())
                    if match:
                        uidnext = int(match.group(1))
                        self.current_max_uid = uidnext - 1
                        break

            redis_key = await self.redis.gen_key(
                telegram_id=self.telegram_id,
                box_id=self.box_id,
            )

            return_message = False

            while await self.redis.get(redis_key) == settings.ACTIVE_VALUE:
                logger.info(f'BOX {self.box_id}. New while loop.')
                logger.info(f'BOX {self.box_id}. Starting idle.')
                idle_task = await imap_client.idle_start(timeout=59)

                logger.info(f'BOX {self.box_id}. Waiting server push.')
                if await self.handle_server_push(
                    await imap_client.wait_server_push()
                ):
                    return_message = True

                logger.info(f'BOX {self.box_id}. Ending idle.')
                imap_client.idle_done()
                logger.info(f'BOX {self.box_id}. Waiting idle timeout.')
                await wait_for(idle_task, timeout=60)

                if return_message:
                    self.current_max_uid = await self.fetch_messages_headers(
                        imap_client=imap_client,
                        max_uid=self.current_max_uid,
                        username=self.username,
                        return_message=return_message,
                    )
                    return_message = False
            logger.info(f'BOX {self.box_id}. Logining out IMAP.')
            await imap_client.logout()
        except asyncio.TimeoutError:
            logger.error(f'BOX {self.box_id}. Loop timeout.')
            self.restart_loop = True

        if self.restart_loop:
            logger.info(f'BOX {self.box_id}. Restarting imap_loop.')
            self.restart_loop = False
            await self.imap_loop()


class IMAPListener:
    """Слушатель почтовых ящиков."""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        telegram_id: int,
        box_id: int,
    ):
        self.imap_client: IMAPClient = IMAPClient(
            host=host,
            port=port,
            username=username,
            password=password,
            telegram_id=telegram_id,
            box_id=box_id,
        )
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        """Запустить слушатель."""
        if self._task is None:
            self._task = asyncio.create_task(self.imap_client.imap_loop())
        logger.info(
            f'BOX {self.imap_client.box_id}. Started IMAP Listener.',
        )
