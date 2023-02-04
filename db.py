from contextvars import ContextVar

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config import ASYNC_DB_URL, SYNC_DB_URL

ctx_session = ContextVar('ctx_session', default=None)


def session() -> AsyncSession:
    s = ctx_session.get()
    if not s:
        raise Exception('Session is not set')
    return s


def set_context_session(session: AsyncSession):
    ctx_session.set(session)


engine = create_engine(SYNC_DB_URL)
async_engine = create_async_engine(ASYNC_DB_URL)
async_session = sessionmaker(async_engine,
                             expire_on_commit=False,
                             class_=AsyncSession)



    