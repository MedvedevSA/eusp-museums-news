from sqlalchemy.orm import declarative_base
from sqlalchemy import (Column, Integer, String)


Base = declarative_base()

class Sites(Base):
    __tablename__ = "sites"
    id = Column(Integer(), primary_key=True, comment='Уникальный ID')
    url = Column(String(), comment='url ссылка')
    ref_count = Column((Integer()), comment='url ссылка')

