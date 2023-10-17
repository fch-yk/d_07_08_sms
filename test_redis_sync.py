import os

from dotenv import load_dotenv
from redis import Redis

load_dotenv()


redis_connection = Redis(
    host=os.getenv('SMSC_REDIS_HOST'),
    port=os.getenv('SMSC_REDIS_PORT'),
    password=os.getenv('SMSC_REDIS_PASSWORD'),
    decode_responses=True
)


redis_connection.set('my_phone', 223322)
my_value = redis_connection.get('my_phone')  # если ключа нет, вернет None
print(my_value)
