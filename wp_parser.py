import asyncio
import json

from aiohttp import ClientSession
from sqlalchemy import select

import model
from db import async_session, set_context_session, session


WP_JSON = '/wp-json/wp/v2/posts'


async def run_parse():
    
    async def task(client: ClientSession, row: dict, sem):
        res = None
        try:
            res = await client.get(row['url'] + WP_JSON)
            if res.status == 200:
                data_text = await res.text()
                data = json.loads(data_text)
                q = f"""
                    UPDATE sites
                    SET posts=:post
                    WHERE id=:id"""
                args = dict(
                    post=json.dumps(data, ensure_ascii=False),
                    id=row['id']
                )
                await session().execute(q, args)
            
        except Exception as e:
            print(e)
        await session().commit()

    sem = asyncio.Semaphore(100)

    async def sem_task(client, row):
        async with sem:  
            return await task(client, row, sem)

    async with async_session() as s:
        set_context_session(s)
        sites = (await session().execute(
                str(select(model.Sites)),
            )
        ).mappings().fetchall()

        async with ClientSession() as client:
            await asyncio.gather(
                *[
                    asyncio.ensure_future(sem_task(client, dict(site)))
                    for site in sites
                ],
            )


def main():
    asyncio.run(run_parse())


if __name__ == '__main__':
    main()
