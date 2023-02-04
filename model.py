from sqlalchemy import (JSON, Column, ForeignKey, Index, Integer, String,
                        UniqueConstraint)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Sites(Base):
    __tablename__ = "sites"
    id = Column(Integer(), primary_key=True, comment='Уникальный ID')
    url = Column(String(), comment='url ссылка')
    ref_count = Column((Integer()), comment='url ссылка')
    posts = Column(JSON(), comment='')


UniqueConstraint(Sites.url, name='uix-1')
Index('index_url', Sites.url)


class News(Base):
    __tablename__ = "news"
    id = Column(Integer(), primary_key=True, comment='Уникальный ID')
    ext_id = Column(Integer(), comment='id записи на реcурсе')
    site_url = Column(String(), ForeignKey(Sites.url, ondelete='CASCADE'), comment='Реурс')
    title = Column(String(), comment='url ссылка')
    news_content = Column(String(), comment='Содержимое новости')
    link = Column(String(), comment='Ссылка на новость')

