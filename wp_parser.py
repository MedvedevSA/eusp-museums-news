import asyncio
import json

from aiohttp import ClientSession
from sqlalchemy import select, update
from sqlalchemy.orm import Session

import model
from db import engine


WP_JSON = '/wp-json/wp/v2/posts'


async def run_parse():
    
    async def task(conn, client: ClientSession, row: dict, sem):
        res = None
        try:
            res = await client.get(row['url'] + WP_JSON)
            if res.status == 200:
                data_text = await res.text()
                data = json.loads(data_text)
                print(f'WP FOUND: {row["id"]}', row, sem)
                upd = (
                    update(model.Sites)
                    .where(model.Sites.id == row['id'])
                    .values(posts=json.dumps(data))
                )
                # with engine.begin() as conn:
                conn.execute(upd)
                conn.commit()
            else:
                print(f'NO WP: {row["id"]}', row, sem)
        except Exception as e:
            print(e)

    sem = asyncio.Semaphore(100)

    async def sem_task(conn, client, row):
        async with sem:  
            return await task(conn, client, row, sem)

    with engine.begin() as conn:
        sites = conn.execute(select(model.Sites)).mappings().fetchall()
        async with ClientSession() as client:
            all_res = await asyncio.gather(
                *[
                    asyncio.ensure_future(sem_task(conn, client, dict(site)))
                    for site in sites
                ],
            )
            all_res = all_res


def main():
    asyncio.run(run_parse())


if __name__ == '__main__':
    main()
