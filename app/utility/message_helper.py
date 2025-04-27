import random
import string
import os

from .base_driver import BaseDriverHelper

class RandomMessageGenerator(BaseDriverHelper):
    """Генератор случайных сообщений с вложениями"""

    DEFAULT_SUBJECTS = [
        "Important Update", "Meeting Reminder", "Your Invoice", "Special Offer Inside!",
        "Project Status", "Urgent: Please Review", "Weekend Plans?", "Just Saying Hi!"
    ]

    DEFAULT_BODY_TEMPLATES = [
        "Hello,\n\nHope you're doing well! Here’s a quick update: {content}.\n\nBest regards,\nTeam",
        "Dear colleague,\n\nThis is to inform you about {content}.\n\nSincerely,\nHR",
        "Hey there!\n\nJust wanted to share some news: {content}.\n\nCheers!"
    ]

    def __init__(self, name: str = "RandomMessageGenerator", attachment_dir="attachments",
                 subjects=None, body_templates=None):
        super().__init__(name)
        self.attachment_dir = attachment_dir
        os.makedirs(self.attachment_dir, exist_ok=True)

        self.subjects = subjects if subjects else self.DEFAULT_SUBJECTS
        self.body_templates = body_templates if body_templates else self.DEFAULT_BODY_TEMPLATES

    def generate_subject(self):
        """Генерирует случайную тему сообщения"""
        return random.choice(self.subjects)

    def generate_body(self):
        """Генерирует случайное тело сообщения"""
        random_content = self._random_text(50, 150)
        template = random.choice(self.body_templates)
        return template.format(content=random_content)

    def generate_attachment(self, file_type="txt"):
        """
        Создаёт случайный файл как вложение.
        Поддерживаются типы: txt, csv, log.
        """
        file_extensions = {"txt": "txt", "csv": "csv", "log": "log"}
        extension = file_extensions.get(file_type, "txt")  # По умолчанию txt
        filename = f"{self.attachment_dir}/attachment_{random.randint(1000, 9999)}.{extension}"

        with open(filename, "w") as file:
            file.write(self._random_text(200, 500))  # Генерируем случайный текст

        return filename

    def cleanup(self):
        """Удаляет все созданные вложения"""
        for file in os.listdir(self.attachment_dir):
            file_path = os.path.join(self.attachment_dir, file)
            os.remove(file_path)
        print("Очистка вложений завершена!")

    def _random_text(self, min_len=50, max_len=200):
        """Генерирует случайный текст заданной длины"""
        length = random.randint(min_len, max_len)
        return ''.join(random.choices(string.ascii_letters + " ", k=length))

    
