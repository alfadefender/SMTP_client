import base64
import os
import random
import re
from datetime import datetime


class MsgBuilder:
    def __init__(self, from_addr: str, to_addr: list, subject: str):
        self._boundary = f"boundary.{random.randint(10000, 99999)}"
        self._message = self._build_headers(from_addr, to_addr, subject)

    def get_message(self) -> str:
        """
        Возвращает сформированное сообщение электронной почты.

        Returns:
            str: Сообщение электронной почты.

        """
        self._message += (
            f"--{self._boundary}--\n"
            ".\n"
        )
        return self._message

    def add_text(self, text: str):
        """
        Добавляет текстовую часть сообщения.

        Args:
            text (str): Текст для добавления в сообщение.

        """
        self._message += (
            f"--{self._boundary}\n"
            "Content-Type: text/html; charset=utf-8;\n"
            "\n"
            f"{self._normalize_text(text)}\n"
            "\n"
        )

    def add_attachment(self, file_data: bytes, file_name: str):
        """
        Добавляет вложение в виде байтовых данных.

        Args:
            file_data (bytes): Байтовые данные вложения.
            file_name (str): Имя файла вложения.

        """
        self._message += (
            f"--{self._boundary}\n"
            f"Content-Type: application/octet-stream;\n"
            f'  name="{file_name}"\n'
            f"Content-Disposition: attachment;\n"
            f'  filename="{file_name}"\n'
            f"Content-Transfer-Encoding: base64\n"
            "\n"
            f"{base64.b64encode(file_data).decode()}\n"
        )

    def add_attachment_from(self, path: str):
        """
        Добавляет вложение из указанного файла или папки.

        Args:
            path (str): Путь к файлу или папке вложения.

        """
        if os.path.isfile(path):
            self._add_file_content(path)
        elif os.path.isdir(path):
            self._add_folder_content(path)
        else:
            print(f"Invalid path: {path}")

    def _add_file_content(self, file_path: str):
        """
        Вспомогательный метод для добавления содержимого файла в виде вложения.

        Args:
            file_path (str): Путь к файлу.

        """
        with open(file_path, "rb") as file:
            file_data = file.read()
        file_name = os.path.basename(file_path)
        self.add_attachment(file_data, file_name)

    def _add_folder_content(self, folder_path: str):
        """
        Вспомогательный метод для добавления содержимого папки в виде вложений.

        Args:
            folder_path (str): Путь к папке.

        """
        for root, _, files in os.walk(folder_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                self._add_file_content(file_path)

    def _build_headers(self, from_addr: str, to_addrs: list, subject: str) -> str:
        """
        Вспомогательный метод для построения заголовков сообщения.

        Args:
            from_addr (str): Адрес отправителя.
            to_addrs (list): Список адресов получателей.
            subject (str): Тема письма.

        Returns:
            str: Заголовки сообщения.

        """
        return (
            f"Date: {datetime.now().strftime('%d/%m/%y')}\n"
            f"From: {from_addr}\n"
            f"To: {', '.join(to_addrs)}\n"
            f"Subject: {subject}\n"
            "MIME-Version: 1.0\n"
            "Content-Type: multipart/mixed;\n"
            f"  boundary={self._boundary}\n"
            "\n"
        )

    def _normalize_text(self, text: str) -> str:
        """
        Вспомогательный метод для нормализации текста.

        Если строка текста начинается с точки, добавляет одну дополнительную точку в начало.
        Это позволяет обеспечить корректную интерпретацию строк, начинающихся с точки в контексте MIME.

        Args:
            text (str): Исходный текст.

        Returns:
            str: Нормализованный текст.

        """
        text = ("." + text) if text.startswith(".") else text
        return re.sub(r"\n\.", lambda match: match.group(0) + ".", text)


def build_message(from_addr: str, to_addrs: list, message: dict) -> str:
    """
    Строит сообщение электронной почты на основе заданных параметров.

    Args:
        from_addr (str): Адрес отправителя.
        to_addrs (list): Список адресов получателей.
        message (dict): Данные для построения сообщения. Включает ключи 'subject', 'message_file_path' и 'attachment_folder_path'.

    Returns:
        str: Сообщение электронной почты.

    """
    builder = MsgBuilder(from_addr, to_addrs, message.get("subject"))
    with open(message.get('message_file_path'), 'r', encoding="utf-8") as file:
        builder.add_text(file.read())
    builder.add_attachment_from(message.get("attachment_folder_path"))
    return builder.get_message()