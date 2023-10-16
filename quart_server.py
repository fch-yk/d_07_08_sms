import datetime
import logging
from unittest.mock import patch

import trio
from pydantic import BaseModel, ValidationError, constr
from quart import render_template, request, websocket
from quart_trio import QuartTrio

from smsc_api import RequestSMSC

app = QuartTrio(__name__)
app.config.from_prefixed_env(prefix='SMSC')
smsc_connection = RequestSMSC(
    login=app.config['LOGIN'],
    password=app.config['PSW']
)
logger = logging.getLogger(__file__)


class InputForm(BaseModel):
    text: constr(min_length=1, max_length=70)


class SMSCSettings(BaseModel):
    login: str
    password: str
    phones: str
    valid: int


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

    with patch.object(
        RequestSMSC,
        'send',
        return_value={'id': 104062995, 'cnt': 1}
    ):
        request_smsc = RequestSMSC(
            login=app.config['LOGIN'],
            password=app.config['PSW']
        )
        sending_response = await request_smsc.send(
            input_form.text, app.config['PHONES'], app.config['VALID']
        )

    # request_smsc = RequestSMSC(
    #     login=app.config['LOGIN'],
    #     password=app.config['PSW']
    # )
    # sending_response = await request_smsc.send(
    #     input_form.text, app.config['PHONES'], app.config['VALID']
    # )
    logger.info('sending_response: %s', sending_response)
    return sending_response


@app.route("/api")
async def json():
    return {"hello": "world"}


@app.websocket("/ws")
async def ws():
    delivered_01 = 0
    delivered_02 = 0
    total_01 = 345
    total_02 = 3993

    while True:
        await trio.sleep(1)
        timestamp = datetime.datetime.now().timestamp()
        await websocket.send_json(
            {
                "msgType": "SMSMailingStatus",
                "SMSMailings": [
                    {
                        "timestamp": timestamp,
                        "SMSText": "Сегодня гроза! Будьте осторожны!",
                        "mailingId": "1",
                        "totalSMSAmount": total_01,
                        "deliveredSMSAmount": delivered_01,
                        "failedSMSAmount": 5,
                    },
                    {
                        "timestamp": timestamp,
                        "SMSText": "Новогодняя акция!!! Получи скидку!!!",
                        "mailingId": "new-year",
                        "totalSMSAmount": total_02,
                        "deliveredSMSAmount": delivered_02,
                        "failedSMSAmount": 0,
                    },
                ]
            }
        )
        delivered_01 += total_01 // 100
        if delivered_01 > total_01:
            delivered_01 = 0
        delivered_02 += total_02 // 100
        if delivered_02 > total_02:
            delivered_02 = 0


if __name__ == "__main__":
    logging.basicConfig()
    logger.setLevel(logging.INFO)
    app.run()
