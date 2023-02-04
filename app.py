from aiohttp import web
from celery import chain

import tasks
from db import async_session

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
        row = (
            await session.execute(q, dict(search=f'%{search}%'))
        ).mappings().fetchall()
        
    return web.Response(text=str(row))


@routes.get('/lp')
async def launch_parser(request):
    chain(tasks.wp_parser_task.si()).apply_async()
    return web.Response(text="Started")


def main():
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app)


if __name__ == '__main__':
    main()
