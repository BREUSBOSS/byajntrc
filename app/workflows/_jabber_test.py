import asyncio
import logging
import ssl
import random
from slixmpp import ClientXMPP


class UserSimBot(ClientXMPP):

    def __init__(self, jid, password):
        super().__init__(jid, password)

        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)
        self.add_event_handler("disconnected", self.on_disconnected)  # <- новый хендлер

    async def session_start(self, event):
        self.send_presence()
        await self.get_roster()

        all_contacts = list(self.client_roster.keys())
        if not all_contacts:
            logging.info("Контактов нет, отправляю сообщение самому себе.")
            recipients = [self.boundjid.full]
        else:
            recipients = random.sample(all_contacts, k=min(3, len(all_contacts)))

        for recipient in recipients:
            body = "Привет! Это бот-симулятор пользователя :)"
            self.send_message(mto=recipient, mbody=body, mtype='chat')
            logging.info(f"Отправлено сообщение: '{body}' пользователю {recipient}")

        await asyncio.sleep(5)
        self.disconnect()

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            response = f"Бот получил ваше сообщение: {msg['body']}"
            msg.reply(response).send()
            logging.info(f"Ответ отправлен: {response}")
            self.disconnect()

    def on_disconnected(self, event):
        """Завершаем event loop после отключения."""
        logging.info("Бот отключился. Завершаем event loop.")
        asyncio.get_event_loop().stop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

    xmpp = UserSimBot('user1@contoso.com', '123')
    xmpp.connect()
    asyncio.get_event_loop().run_forever()
