import logging
from unittest.mock import patch

from quart import render_template, request, websocket
from quart_trio import QuartTrio

from smsc_api import RequestSMSC
from pydantic import BaseModel, ValidationError, constr


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
    # while True:
    #     await websocket.send("hello")
    #     await websocket.send_json({"hello": "world"})
    pass


if __name__ == "__main__":
    logging.basicConfig()
    logger.setLevel(logging.INFO)
    app.run()
