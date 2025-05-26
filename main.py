from dependencies import get_settings, get_data, get_credentials
from smtp_client import SMTPClient


def main():
    settings = get_settings()
    credentials = get_credentials()
    data = get_data()

    client = SMTPClient()
    client.connect(settings.get("smtp_host"), settings.get("smtp_port"))
    client.authorization(credentials.get("login"), credentials.get("password"))
    client.send_data(data.get("to_addrs"), data.get("message"))
    client.close()


if __name__ == "__main__":
    main()