import asyncio
import json
import aio_pika
import logging
from aiohttp import web


def error(message):
    return web.Response(text=json.dumps({
            'status': 'error',
            'message': message
        }))

async def catcher(request):
    channel = await request.app['connection'].channel()
    raw_data = await request.text()

    try:
        data = json.loads(raw_data)
    except Exception as e:
        return error("JSON data invalid")

    for tp in ['lang', 'token', 'message', 'errorLocation', 'stack', 'time']:
        if tp not in data:
            return error(f"Param {tp} not presented")

    await channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps(data).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        ),
        routing_key="hawk"
    )

    return web.Response(text=json.dumps({
            'status': 'success'
        }))


async def init(app, loop):
    connection = await aio_pika.connect("amqp://guest:guest@127.0.0.1/", loop=loop)
    app['connection'] = connection


async def close_connection(app):
    await app['connection'].close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    app.router.add_post('/', catcher)

    loop.run_until_complete(init(app, loop))
    web.run_app(app)
    loop.run_until_complete(close_connection(app))
