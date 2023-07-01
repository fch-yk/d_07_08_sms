import requests
from environs import Env


def main():
    env = Env()
    env.read_env()
    url = 'https://smsc.ru/sys/send.php'

    payload = {
        'login': env.str('SMSC_LOGIN'),
        'psw': env.str('SMSC_PSW'),
        'mes': env.str('SMSC_MES'),
        'phones': env.str('SMSC_PHONES')
    }
    response = requests.post(url, params=payload, timeout=100)
    print(response.text)
    response.raise_for_status()


if __name__ == '__main__':
    main()
