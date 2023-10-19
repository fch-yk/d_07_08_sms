import datetime
import logging
import os
from unittest.mock import patch

import aioredis
import trio
import trio_asyncio
from dotenv import load_dotenv
from hypercorn.config import Config as HyperConfig
from hypercorn.trio import serve
from pydantic import BaseModel, ValidationError, constr
from quart import render_template, request, websocket
from quart_trio import QuartTrio
from trio_asyncio import aio_as_trio

from db import Database
from smsc_api import RequestSMSC

app = QuartTrio(__name__)
app.config.from_prefixed_env(prefix='SMSC')
smsc_connection = RequestSMSC(
    login=os.getenv('SMSC_LOGIN', ''),
    password=os.getenv('SMSC_PSW', '')
)

logger = logging.getLogger(__file__)


class InputForm(BaseModel):
    text: constr(min_length=1, max_length=70)


class SMSCSettings(BaseModel):
    login: str
    password: str
    phones: str
    valid: int


@app.before_serving
async def create_db_connection():
    app.redis = aioredis.from_url(
        os.getenv('SMSC_REDIS_URL'), decode_responses=True
    )
    app.db = Database(app.redis)


@app.after_serving
async def close_db_connection():
    await app.redis.close()


@app.route("/")
async def hello():
    return await render_template("index.html")


@app.route("/send/", methods=["POST"])
async def send_sms():

    form = await request.form
    try:
        input_form = InputForm(**{'text': form['text']})
    except ValidationError as e:
        return {"errorMessage": str(e.errors())}, 400

    phones = os.getenv('SMSC_PHONES', '')
    # with patch.object(
    #     RequestSMSC,
    #     'send',
    #     return_value={
    #         'id': 104062998,
    #         'cnt': 1,
    #         'cost': '4.18',
    #         'balance': '770.59'
    #     }
    # ):
    #     request_smsc = RequestSMSC(
    #         login=os.getenv('SMSC_LOGIN', ''),
    #         password=os.getenv('SMSC_PSW', '')
    #     )
    #     sending_response = await request_smsc.send(
    #         input_form.text,
    #         phones,
    #         os.getenv('SMSC_VALID', '')
    #     )

    request_smsc = RequestSMSC(
        login=os.getenv('SMSC_LOGIN', ''),
        password=os.getenv('SMSC_PSW', '')
    )
    sending_response = await request_smsc.send(
        input_form.text,
        phones,
        os.getenv('SMSC_VALID', '')
    )
    logger.info('sending_response: %s', sending_response)

    await aio_as_trio(
        app.db.add_sms_mailing(
            sending_response['id'], phones.split(','), input_form.text
        )
    )

    return sending_response


@app.route("/api")
async def json():
    return {"hello": "world"}


@app.websocket("/ws")
async def ws():
    while True:
        await trio.sleep(1)
        sms_ids = await aio_as_trio(app.db.list_sms_mailings())
        db_sms_mailings = await aio_as_trio(app.db.get_sms_mailings(*sms_ids))
        site_sms_mailings = []
        for db_sms_mailing in db_sms_mailings:
            site_sms_mailings.append(
                {
                    "timestamp": db_sms_mailing['created_at'],
                    "SMSText": db_sms_mailing['text'],
                    "mailingId": str(db_sms_mailing['sms_id']),
                    "totalSMSAmount": len(db_sms_mailing['phones']),
                    "deliveredSMSAmount": len(db_sms_mailing['phones']),
                    "failedSMSAmount": 0,
                }
            )

        await websocket.send_json(
            {
                "msgType": "SMSMailingStatus",
                "SMSMailings": site_sms_mailings
            }
        )


async def run_server():
    async with trio_asyncio.open_loop():
        config = HyperConfig()
        config.bind = ["127.0.0.1:5000"]
        config.use_reloader = True
        await serve(app, config)

if __name__ == "__main__":
    logging.basicConfig()
    logger.setLevel(logging.INFO)
    load_dotenv()
    trio.run(run_server)
