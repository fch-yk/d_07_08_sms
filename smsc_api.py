import asks
from trio import TrioDeprecationWarning
import asyncclick as click
import warnings
from dotenv import load_dotenv


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
    payload = {
        'login': login,
        'psw': password,
        'mes': message,
        'phones': phones,
        'valid': valid,
    }
    url = 'https://smsc.ru/sys/send.php'
    response = await asks.get(url, params=payload)
    response.raise_for_status()

if __name__ == '__main__':
    load_dotenv()
    warnings.filterwarnings(action='ignore', category=TrioDeprecationWarning)
    main(_anyio_backend="trio")
