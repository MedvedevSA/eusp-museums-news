import asyncio
import json
import logging
from typing import List

from aiohttp import ClientConnectionError, ClientSession
from funcy import get_in
from sqlalchemy import insert, select

import model
from db import async_session, session, set_context_session

logger = logging.getLogger()
WP_JSON = '/wp-json/wp/v2/posts'
CHUNK_SIZE = 500

status_str = '{title} ({signs})'


def row_signs_str(row, _list):
    return', '.join([
        ':'.join([str(k), str(v)])
        for k, v in row.items() if k in _list
    ])


class WPParser:
    def __init__(self, log=None) -> None:
        self.log = None
        if log:
            self.log = log
        if not self.log:
            self.log = logger

        self.sem = asyncio.Semaphore(500)

    async def add_to_news(self, row: dict, wp_resp: List[dict]):
        url = row['url']
        for post in wp_resp:
            item = dict(
                site_url=url,
                ext_id=post.get('id'),
                title=get_in(post, ['title', 'rendered']),
                news_content=get_in(post, ['content', 'rendered']),
                link=post.get('link'),
            )
            q = (
                select(model.News).where(
                    model.News.ext_id == item['ext_id']).where(
                        model.News.site_url == item['site_url']
                    )
            )
            if not (await session().execute(q)).scalar_one_or_none():
                q = insert(model.News).values(**item)
                await session().execute(q)
                await session().commit()
                self.log.info(status_str.format(
                    title="Success parsed", 
                    signs=row_signs_str(row, ['id', 'url'])
                    )
                )

    async def task(self, client: ClientSession, row: dict):
        res = None
        raw_wp_posts = None

        try:
            res = await client.get(row['url'] + WP_JSON)
            raw_wp_posts = json.loads(
                await res.text()
            )
        except json.JSONDecodeError:
            self.log.info(status_str.format(
                title="Error parse JSON", 
                signs=row_signs_str(row, ['id', 'url'])
                )
            )
        except ClientConnectionError:
            self.log.info(status_str.format(
                title="Connection error", 
                signs=row_signs_str(row, ['id', 'url'])
                )
            )
        except UnicodeDecodeError:
            self.log.info(status_str.format(
                title="UnicodeDecodeError", 
                signs=row_signs_str(row, ['id', 'url'])
                )
            )
        except Exception as e:
            self.log.info(status_str.format(
                title=type(e).__name__, 
                signs=row_signs_str(row, ['id', 'url'])
                ), e
            )

        if raw_wp_posts and res.status == 200:
            await self.add_to_news(row, raw_wp_posts)
            
    async def sem_task(self, client, row):
        async with self.sem:  
            return await self.task(client, row)

    async def raise_new_client(self, sites):
        async with ClientSession(raise_for_status=False) as client:
            await asyncio.gather(
                *[
                    asyncio.ensure_future(self.sem_task(client, dict(site)))
                    for site in sites
                ],
            )

    async def run(self):
        async with async_session() as s:
            set_context_session(s)
            sites = (await session().execute(
                    str(select(model.Sites)),
                )
            ).mappings().fetchall()

            chunk = []
            for site in sites:
                chunk.append(site)
                if len(chunk) > CHUNK_SIZE:
                    await self.raise_new_client(chunk)
                    chunk = []
            if chunk:
                await self.raise_new_client(chunk)
                chunk = []


async def main():
    await (WPParser()).run()


if __name__ == '__main__':
    asyncio.run(main())
    
