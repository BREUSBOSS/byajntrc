import slixmpp

import logging

import ssl



# Отключаем проверку сертификатов

slixmpp.xmlstream.XMLStream.ssl_context = ssl.create_default_context()

# slixmpp.xmlstream.XMLStream.ssl_context.check_hostname = False

slixmpp.xmlstream.XMLStream.ssl_context.verify_mode = ssl.CERT_NONE



# Настройка логирования

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger("slixmpp")

logger.setLevel(logging.DEBUG)



class SimpleBot(slixmpp.ClientXMPP):

    def __init__(self, jid, password, server):

        super().__init__(jid, password)

        self.server = server

        self.add_event_handler("session_start", self.session_start)

        self.add_event_handler("message", self.message)

        self.add_event_handler("error", self.handle_error)



    def session_start(self, event):

        logger.info("Сессия началась.")

        self.send_presence()

        self.get_roster()



        # Отправка сообщения сам себе

        self.send_message(mto=self.boundjid.bare, mbody="Привет, это твой бот!", mtype='chat')

        logger.info("Сообщение отправлено самому себе.")



    def message(self, msg):

        if msg['type'] in ('chat', 'normal'):

            logger.info(f"Получено сообщение: {msg['body']}")



    def handle_error(self, error):

        logger.error(f"Ошибка: {error}")



# Логин, пароль пользователя и адрес сервера

jid = "user1@contoso.com"

password = "123"

server = "192.168.88.234"



# Создание и запуск бота

bot = SimpleBot(jid, password, server)



# Установка соединения с сервером XMPP

ssl_context = ssl.create_default_context()

ssl_context.check_hostname = False

ssl_context.verify_mode = ssl.CERT_NONE



bot.ssl_context = ssl_context  # Устанавливаем ssl контекст



# Установка соединения с сервером XMPP

bot.connect((server, 5222))  # Обычно порт XMPP - 5222

bot.process(forever=True)

