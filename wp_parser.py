import logging 
import asyncio
import json
from funcy import get_in

from aiohttp import ClientSession, ClientConnectionError
from sqlalchemy import select, insert

import model
from db import async_session, set_context_session, session

logger = logging.getLogger()
WP_JSON = '/wp-json/wp/v2/posts'


class WPParser:
    def __init__(self, log=None) -> None:
        self.log = None
        if log:
            self.log = log
        if not self.log:
            self.log = logger

        self.sem = asyncio.Semaphore(100)

    async def _add_to_news(self, row, wp_resp):
        url = row['url']
        for post in wp_resp:
            if isinstance(post, dict):
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
                    self.log(f'Success parsed ({row["url"]})')

    async def _task(self, client: ClientSession, row: dict):
        def row_signs_str(_list):
            return', '.join([
                ':'.join([k, v])
                for k, v in row.items() if k in _list
            ])
        res = None
        raw_wp_posts = None
        exept_str = '{title} ({signs})'

        try:
            res = await client.get(row['url'] + WP_JSON)
            raw_wp_posts = json.loads(
                await res.text()
            )
        except json.JSONDecodeError:
            self.log.info(exept_str.format(
                title="Error parse JSON", 
                signs=row_signs_str(['id', 'url'])
                )
            )
        except ClientConnectionError:
            self.log.info(exept_str.format(
                title="Connection error", 
                signs=row_signs_str(['id', 'url'])
                )
            )
        except UnicodeDecodeError:
            self.log.info(exept_str.format(
                title="UnicodeDecodeError", 
                signs=row_signs_str(['id', 'url'])
                )
            )
        except Exception:
            self.log.info(exept_str.format(
                title="Exception", 
                signs=row_signs_str(['id', 'url'])
                )
            )

        if raw_wp_posts and res.status == 200:
            await self._add_to_news(row, raw_wp_posts)
            
    async def _sem_task(self, client, row):
        async with self.sem:  
            return await self._task(client, row)

    async def run(self):
        async with async_session() as s:
            set_context_session(s)
            sites = (await session().execute(
                    str(select(model.Sites)),
                )
            ).mappings().fetchall()

            async with ClientSession() as client:
                await asyncio.gather(
                    *[
                        asyncio.ensure_future(self._sem_task(client, dict(site)))
                        for site in sites
                    ],
                )


async def main():
    await (WPParser()).run()


if __name__ == '__main__':
    asyncio.run(main())
    
