import logging
import warnings
from typing import Dict
from unittest.mock import patch

import asks
import asyncclick as click
from dotenv import load_dotenv
from trio import TrioDeprecationWarning

logger = logging.getLogger(__file__)


class SmscApiError(Exception):
    def __init__(self, error, error_code, sending_id):
        self.error = error
        self.error_code = error_code
        self.sending_id = sending_id

    def __str__(self):
        return (
            f'sms was not sent (error_code: {self.error_code}, '
            f'error: {self.error}, '
            f'sending id: {self.sending_id})'
        )


class RequestSMSC():
    def __init__(self, login: str, password: str, format_code: int = 3):
        self.login = login
        self.password = password
        self.format_code = format_code

    async def send(self, message: str, phone: str, valid: int = 1) -> Dict:
        payload = {
            'login': self.login,
            'psw': self.password,
            'fmt': self.format_code,
            'mes': message,
            'phones': phone,
            'valid': valid,
            'charset': 'utf-8',
            'cost': 3,
        }
        url = 'https://smsc.ru/sys/send.php'
        response = await asks.post(url, params=payload)
        response.raise_for_status()
        sending_response = response.json()
        if 'error' in sending_response:
            raise SmscApiError(
                sending_response['error'],
                sending_response['error_code'],
                sending_response['id'],
            )

        return sending_response

    async def get_status(self, phones, sending_id, all=2) -> Dict:
        payload = {
            'login': self.login,
            'psw': self.password,
            'fmt': self.format_code,
            'phone': phones,
            'id': sending_id,
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
    default=1,
    help='message time to live (in hours)',
)
@click.option(
    '--debug_mode',
    envvar='SMSC_DEBUG_MODE',
    is_flag=True,
    default=False,
    help='Turn the debug mode on/off'
)
async def main(login, password, message, phones, valid, debug_mode):
    logging.basicConfig()
    logger.setLevel(logging.INFO)

    if debug_mode:
        with patch.object(
            RequestSMSC,
            'send',
            return_value={'id': 104062993, 'cnt': 1}
        ):
            request_smsc = RequestSMSC(login, password)
            sending_response = await request_smsc.send(message, phones, valid)
    else:
        request_smsc = RequestSMSC(login, password)
        sending_response = await request_smsc.send(message, phones, valid)

    logger.debug('send responsce: %s', sending_response)
    for phone in phones.split(','):
        status_response = await request_smsc.get_status(
            phone,
            sending_id=sending_response['id']
        )
        logger.info('status response: %s', status_response)

if __name__ == '__main__':
    load_dotenv()
    warnings.filterwarnings(action='ignore', category=TrioDeprecationWarning)
    main(_anyio_backend="trio")
