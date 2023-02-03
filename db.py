from sqlalchemy import create_engine, select, insert, text
from sqlalchemy.orm import Session

from model import Base
import model
engine = create_engine("sqlite:///sqlite.db")

def init():
    def init_models():
        with engine.connect() as conn:
            for meta_tbl in Base.metadata.tables.values():
                conn.execute(text(f'drop table if exists {meta_tbl}'))

            Base.metadata.create_all(conn)

    def seeds():
        with Session(engine) as session:
            q = f"""
count(*) as ref_count,
"_source/general/contacts/website" as url
from raw_data
group by "_source/general/contacts/website"
            """
            session.execute(insert(model.Sites)
                            .from_select(['ref_count', 'url'],select(text(q)))
            )
            session.commit()

    init_models()
    seeds()

    