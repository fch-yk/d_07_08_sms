import asks
from trio import TrioDeprecationWarning
import asyncclick as click
import warnings
from dotenv import load_dotenv


async def send_sms(login, password, message, phones, valid):
    payload = {
        'login': login,
        'psw': password,
        'mes': message,
        'phones': phones,
        'valid': valid,
        'cost': '3',
        'fmt': '3',
    }
    url = 'https://smsc.ru/sys/send.php'
    response = await asks.get(url, params=payload)
    response.raise_for_status()
    return response.json()


async def get_sms_status(login, password, phones, sms_id, fmt=3, all=2):
    payload = {
        'login': login,
        'psw': password,
        'phone': phones,
        'id': sms_id,
        'fmt': fmt,
        'all': all,
    }
    url = 'https://smsc.ru/sys/status.php'
    response = await asks.get(url, params=payload)
    response.raise_for_status()
    return response.json()


@click.command()
@click.option(
    '--login',
    envvar='SMSC_LOGIN',
    help='login'
)
@click.option(
    '--password',
    envvar='SMSC_PSW',
    help='password'
)
@click.option(
    '-m',
    '--message',
    envvar='SMSC_MES',
    default='Test message',
    help='message'
)
@click.option(
    '-p',
    '--phones',
    envvar='SMSC_PHONES',
    help='One or more phone numbers separated by commas'
)
@click.option(
    '-v',
    '--valid',
    envvar='SMSC_VALID',
    default='1',
    help='message time to live (in hours)',
)
async def main(login, password, message, phones, valid):
    send_response = await send_sms(login, password, message, phones, valid)
    # send_response = {'id': 411}
    status_response = await get_sms_status(
        login,
        password,
        phones,
        sms_id=send_response['id']
    )
    print(status_response)

if __name__ == '__main__':
    load_dotenv()
    warnings.filterwarnings(action='ignore', category=TrioDeprecationWarning)
    main(_anyio_backend="trio")
