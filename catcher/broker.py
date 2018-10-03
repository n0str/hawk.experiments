import base64

from celery import Celery

app = Celery('amqp', broker='amqp://guest:guest@localhost:5672/')


@app.task(serializer='json')
def catch(*args, **kwargs):
    try:
        print(base64.b64decode(args[0]))
    except Exception as e:
        print(f"Exception: {e}")
