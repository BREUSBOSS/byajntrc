import asyncio
import logging
import ssl
from slixmpp import ClientXMPP
from time import sleep
import random

from ..utility.base_workflow import BaseWorkflow
from ..utility.message_helper import RandomMessageGenerator

WORKFLOW_NAME = 'jabber_activity_emulation'
WORKFLOW_DESCRIPTION = 'Эмуляция отправки и получения сообщений в Jabber (XMPP) для имитации действий пользователя.'

SENDER_JID = "user1@contoso.com"
PASSWORD = "123"

DEFAULT_WAIT_TIME = 2.0


def load():
    return JabberSenderReceiver()

class JabberSenderReceiver(BaseWorkflow):
    def __init__(self, input_wait_time=DEFAULT_WAIT_TIME):
        super().__init__(name=WORKFLOW_NAME, description=WORKFLOW_DESCRIPTION)
        self.input_wait_time = input_wait_time
        self.loop = asyncio.get_event_loop()
        self.xmpp = None

    def action(self, extra=None):
        """
        Основной метод: эмуляция работы пользователя.
        Запускает XMPP-клиента, ждёт завершения его работы.
        """
        self.xmpp = UserSimBot(SENDER_JID, PASSWORD)
        if self.xmpp.connect():
            try:
                self.loop.run_forever()
            except KeyboardInterrupt:
                logging.info("Принудительное завершение")
                self.xmpp.disconnect()
        else:
            logging.error("Не удалось подключиться к серверу Jabber")

    def cleanup(self):
        """Очистка после завершения"""
        if self.xmpp:
            self.xmpp.disconnect()
        if self.loop.is_running():
            self.loop.stop()
        super().cleanup()
        

class UserSimBot(ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid, password)

        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)
        self.add_event_handler("disconnected", self.on_disconnected)

        self.msg_helper = RandomMessageGenerator()

    async def session_start(self, event):
        self.send_presence()
        await self.get_roster()

        all_contacts = list(self.client_roster.keys())
        if not all_contacts:
            logging.info("Контактов нет, пишу себе.")
            recipients = [self.boundjid.full]
        else:
            recipients = random.sample(all_contacts, k=min(3, len(all_contacts)))

        for recipient in recipients:
            await asyncio.sleep(DEFAULT_WAIT_TIME)

            body = self.msg_helper.generate_body()

            self.send_message(
                mto=recipient,
                mbody=body,
                mtype='chat'
            )

            logging.info(f"Сообщение отправлено пользователю {recipient}")

        await asyncio.sleep(5)
        self.disconnect()

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            logging.info(f"Получено сообщение от {msg['from']}")

            response = f"Бот получил ваше сообщение: {msg['body']}"
            msg.reply(response).send()

            logging.info(f"Ответ отправлен пользователю {msg['from']}")

            self.disconnect()

    def on_disconnected(self, event):
        logging.info("Бот отключился. Завершаем event loop.")
        asyncio.get_event_loop().stop()