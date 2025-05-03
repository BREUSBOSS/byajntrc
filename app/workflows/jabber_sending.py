import slixmpp
import logging
import ssl
import asyncio
import random
from time import sleep

from ..utility.base_workflow import BaseWorkflow  # Убедись, что путь корректный

WORKFLOW_NAME = 'jabber_activity_emulation'
WORKFLOW_DESCRIPTION = 'Эмуляция отправки и получения сообщений в Jabber (XMPP) для имитации действий пользователя.'

# Конфигурация пользователя
SENDER_JID = "user1@contoso.com"
PASSWORD = "123"
SERVER = "192.168.88.234"
PORT = 5222

DEFAULT_WAIT_TIME = 2


def load():
    return JabberBot()


class JabberBot(BaseWorkflow):
    def __init__(self, input_wait_time=DEFAULT_WAIT_TIME):
        super().__init__(name=WORKFLOW_NAME, description=WORKFLOW_DESCRIPTION)
        self.input_wait_time = input_wait_time
        self.logger = logging.getLogger(__name__)
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    def action(self, extra=None):
        """Асинхронный запуск эмуляции действий"""
        try:
            asyncio.run(self._run_bot())
        except Exception as e:
            self.logger.error(f"Ошибка в Jabber workflow: {str(e)}")
            raise

    async def _run_bot(self):
        xmpp = SimpleBot(SENDER_JID, PASSWORD, SERVER, self.logger)
        xmpp.ssl_context = self.ssl_context

        connected = await xmpp.connect((SERVER, PORT))
        if not connected:
            self.logger.error("Не удалось подключиться к серверу XMPP.")
            return
        await xmpp.process()

    def cleanup(self):
        """Очистка ресурсов"""
        super().cleanup()
        self.logger.info("Jabber workflow завершён.")


class SimpleBot(slixmpp.ClientXMPP):
    def __init__(self, jid, password, server, logger):
        super().__init__(jid, password)
        self.server = server
        self.logger = logger

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)
        self.add_event_handler("error", self.handle_error)

    async def session_start(self, event):
        self.logger.info("Сессия началась.")
        self.send_presence()
        await self.get_roster()

        sleep(random.uniform(1.0, 3.0))  # имитация паузы пользователя

        messages = [
            "Привет! Как дела?",
            "Напомни, когда встреча?",
            "Скинь, пожалуйста, презентацию.",
            "Да, всё получил, спасибо!",
            "Буду через 10 минут.",
        ]

        message = random.choice(messages)
        self.send_message(mto=self.boundjid.bare, mbody=message, mtype='chat')
        self.logger.info(f"Отправлено сообщение: {message}")

        await asyncio.sleep(2)  # небольшая задержка
        self.disconnect()

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            self.logger.info(f"Получено сообщение: {msg['body']}")

    def handle_error(self, error):
        self.logger.error(f"Ошибка: {error}")
