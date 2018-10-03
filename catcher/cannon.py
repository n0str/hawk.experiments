import aiohttp
import asyncio
from aiohttp import ClientSession
from local import TOKEN


URL = 'https://hawk.so/catcher/python'
data = {
    "token": TOKEN,
    "message": "Cannon shot",
    "errorLocation": {
        "file": "test.py",
        "line": 10,
        "full": "test.py -> 10"
    },
    "stack": [

    ],
    "time": 1538601176.5771341
}


async def fetch(url, session):
    async with session.post(url, json=data) as response:
        delay = response.headers.get("DELAY")
        date = response.headers.get("DATE")
        print("{}:{} with delay {}".format(date, response.url, delay))
        return await response.read()


async def bound_fetch(sem, url, session):
    # Getter function with semaphore.
    async with sem:
        await fetch(url, session)


async def run(r):
    # url = URL
    url = 'http://localhost:8081/catcher/python'
    tasks = []
    # create instance of Semaphore
    sem = asyncio.Semaphore(500)

    # Create client session that will ensure we dont open new connection
    # per each request.
    async with ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        for i in range(r):
            # pass Semaphore and session to every GET request
            task = asyncio.ensure_future(bound_fetch(sem, url.format(i), session))
            tasks.append(task)

        responses = asyncio.gather(*tasks)
        await responses


# Count of cannon shots
number = 5
loop = asyncio.get_event_loop()

future = asyncio.ensure_future(run(number))
loop.run_until_complete(future)
