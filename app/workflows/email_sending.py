import smtplib
import imaplib
import email
import random
import os
import logging
from time import sleep
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from ..utility.base_workflow import BaseWorkflow
from ..utility.message_helper import RandomMessageGenerator

# Константы
WORKFLOW_NAME = 'EmailSenderReceiver'
WORKFLOW_DESCRIPTION = 'Send and receive emails between two users'

SENDER_USERNAME = "user1"
SENDER_PASSWORD = "12345"
SENDER_EMAIL = "user1@contoso.com"
RECIPIENT_EMAIL = SENDER_EMAIL
DEFAULT_WAIT_TIME = 2
DOMAIN = "contoso.com"
SMTP_SERVER = 'mail.contoso.com'
SMTP_PORT = 587
IMAP_SERVER = 'mail.contoso.com'


def load():
    return EmailSenderReceiver()


class EmailSenderReceiver(BaseWorkflow):
    def __init__(self, input_wait_time=DEFAULT_WAIT_TIME):
        super().__init__(name=WORKFLOW_NAME, description=WORKFLOW_DESCRIPTION)
        self.input_wait_time = input_wait_time
        self.logger = logging.getLogger(__name__)
        self.msg_generator = RandomMessageGenerator()

    def action(self, extra=None):
        """Основной метод выполнения workflow"""
        try:
            self._send_email()
            sleep(random.uniform(2, 5))  # Имитация задержки между отправкой и получением
            self._receive_email()
        except Exception as e:
            self.logger.error(f"Error in email workflow: {str(e)}")
            raise

    def _send_email(self):
        """Отправка email через SMTP, с возможным вложением"""
        subject = self.msg_generator.generate_subject()
        body = self.msg_generator.generate_body()

        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Рандомное добавление вложения
        if random.choice([True, False]):
            attachment_path = self.msg_generator.generate_attachment("txt")
            self._attach_file_to_email(msg, attachment_path)

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SENDER_USERNAME, SENDER_PASSWORD)
                server.send_message(msg)
                self.logger.info(f"Email sent successfully. Subject: {subject}")
        except Exception as e:
            self.logger.error(f"Failed to send email: {str(e)}")
            raise
        finally:
            self.msg_generator.cleanup()

    def _attach_file_to_email(self, msg, file_path):
        """Добавляет вложение к письму"""
        try:
            with open(file_path, "rb") as file:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(file_path)}",
            )
            msg.attach(part)
            self.logger.debug(f"Attached file: {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to attach file: {str(e)}")
            raise

    def _receive_email(self):
        """Получение последнего непрочитанного письма через IMAP"""
        try:
            with imaplib.IMAP4_SSL(IMAP_SERVER) as mail:
                mail.login(SENDER_USERNAME, SENDER_PASSWORD)
                mail.select('inbox')

                status, messages = mail.search(None, 'UNSEEN')
                if status != 'OK' or not messages[0]:
                    self.logger.warning("No unseen emails found.")
                    return

                latest_email_id = messages[0].split()[-1]
                status, msg_data = mail.fetch(latest_email_id, '(RFC822)')
                
                if status != 'OK':
                    raise Exception("Failed to fetch the latest email")

                raw_email = msg_data[0][1]
                email_message = email.message_from_bytes(raw_email)
                subject = email_message['Subject']
                self.logger.info(f"Received email. Subject: {subject}")

        except Exception as e:
            self.logger.error(f"Failed to receive email: {str(e)}")
            raise

    def cleanup(self):
        """Очистка ресурсов"""
        super().cleanup()
        self.logger.info("Email workflow cleanup completed")