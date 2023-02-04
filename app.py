from aiohttp import web
from celery import chain

import tasks
from db import init_db

app = web.Application()
routes = web.RouteTableDef()


@routes.get('/')
async def hello(request):
    params = dict(request.rel_url.query)
    return web.Response(text=str(params))


@routes.get('/lp')
async def launch_parser(request):
    chain(tasks.wp_parser_task.si()).apply_async()
    return web.Response(text="Started")


def main():
    init_db()
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app)


if __name__ == '__main__':
    main()
