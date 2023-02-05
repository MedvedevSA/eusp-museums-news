import logging

from aiohttp import web
from celery import chain

import tasks
from db import async_session

logging.basicConfig(level=logging.DEBUG)
app = web.Application()
routes = web.RouteTableDef()


@routes.get('/')
async def hello(request):
    param = dict(request.rel_url.query)

    q = 'select * from news\n'
    if search := param.get('search'):
        q += 'where title ilike :search or news_content ilike :search\n'
    q += 'limit 10\n'
    async with async_session() as session:
        rows = (
            await session.execute(q, dict(search=f'%{search}%'))
        ).mappings().fetchall()
        
    return web.json_response([dict(row) for row in rows])


@routes.get('/lp')
async def launch_parser(request):
    chain(tasks.wp_parser_task.si()).apply_async()
    return web.json_response(data=None, status=200)

@routes.get('/stop_parse')
async def launch_parser(request):
    tasks.bin.purge() 
    # chain(tasks.wp_parser_task.si()).apply_async()
    return web.json_response(data=None, status=200)

def init_app(app):
    chain(tasks.wp_parser_task.si()).apply_async()
    app = web.Application()
    app.add_routes(routes)
    return app


def main():
    web.run_app(init_app(app))

async def serve():
    return init_app(app)

if __name__ == '__main__':
    main()