import base64
import ssl
import socket
from builder import build_message

TIME_OUT = 1  # Время ожидания (в секундах) для получения данных по сокету.


class SMTPException(Exception):
    """
    Исключение, возникающее при ошибках в SMTP-клиенте или SMTP-сервере.
    """
    pass


class SMTPClient:
    def __init__(self):
        self._host = None
        self._login = None
        self._socket = None

    def connect(self, host: str, port: int):
        """
        Устанавливает соединение с SMTP-сервером.

        Args:
            host (str): Хост SMTP-сервера.
            port (int): Порт SMTP-сервера.

        """
        self._host = host
        self._socket = self._create_ssl_socket(host, port)
        self._receive_data()  # Прочитать приветственное сообщение сервера

    def authorization(self, login: str, password: str):
        """
        Авторизует клиента на SMTP-сервере.

        Args:
            login (str): Логин пользователя.
            password (str): Пароль пользователя.

        """
        self._login = login
        try:
            self._request(f'EHLO {self._host}')
            self._request('AUTH LOGIN')
            self._request(self._encode_base64(login))
            self._request(self._encode_base64(password))
        except SMTPException as e:
            print(e)

    def send_data(self, to_addrs: list, message: dict):
        """
        Отправляет данные (письмо) на SMTP-сервер.

        Args:
            to_addrs (list): Список адресов получателей.
            message (dict): Данные для построения сообщения. Включает ключи 'subject', 'message_file_path' и 'attachment_folder_path'.

        """
        try:
            self._send_mail_commands(to_addrs)
            self._request('DATA')
            self._request(build_message(self._login, to_addrs, message))
        except SMTPException as e:
            print(e)
        else:
            print("Message sent successfully")

    def close(self):
        """
        Закрывает соединение с SMTP-сервером.

        """
        if self._socket:
            self._socket.close()
        self._socket = None

    def _encode_base64(self, data: str) -> str:
        """
        Кодирует строку в формате Base64.

        Args:
            data (str): Исходная строка.

        Returns:
            str: Закодированная строка в формате Base64.

        """
        encoded_data = base64.b64encode(data.encode()).decode()
        return encoded_data

    def _send_mail_commands(self, to_addrs: list):
        """
        Отправляет команды MAIL FROM и RCPT TO для адресов получателей.

        Args:
            to_addrs (list): Список адресов получателей.

        """
        self._request(f'MAIL FROM:{self._login}')
        for to_addr in to_addrs:
            self._request(f'RCPT TO:{to_addr}')

    def _request(self, msg_request: str) -> str:
        """
        Отправляет запрос на SMTP-сервер и получает ответ.

        Args:
            msg_request (str): Запрос.

        Returns:
            str: Ответ от SMTP-сервера.

        """
        self._socket.send((msg_request + '\r\n').encode())
        response = self._receive_data()
        self._check_response(response)
        return response

    def _receive_data(self) -> str:
        """
        Получает данные (ответ) от SMTP-сервера.

        Returns:
            str: Данные (ответ) от SMTP-сервера.

        """
        recv_data = b""
        try:
            while chunk := self._socket.recv(4096):
                recv_data += chunk
        finally:
            return recv_data.decode()

    def _create_ssl_socket(self, host: str, port: int) -> ssl.SSLSocket:
        """
        Создает SSL-сокет и устанавливает соединение с SMTP-сервером.

        Args:
            host (str): Хост SMTP-сервера.
            port (int): Порт SMTP-сервера.

        Returns:
            ssl.SSLSocket: SSL-сокет.

        """
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        return ssl_context.wrap_socket(socket.create_connection(
            (host, port), timeout=TIME_OUT), server_hostname=host)

    def _check_response(self, response: str):
        """
        Проверяет ответ от SMTP-сервера на наличие ошибок.

        Args:
            response (str): Ответ от SMTP-сервера.

        Raises:
            SMTPException: Если SMTP-сервер возвращает ошибку.

        """
        code = response[:3]
        if code not in ['250', '235', '334', '354']:
            raise SMTPException(f"SMTP server returned an error: {response}")