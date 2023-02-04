from sqlalchemy import create_engine, select, insert, text
from sqlalchemy.orm import Session

import model

engine = create_engine("sqlite:///sqlite.db")


def init_db():
    def init_models():
        with engine.connect() as conn:
            for meta_tbl in model.Base.metadata.tables.values():
                conn.execute(text(f'drop table if exists {meta_tbl}'))

            model.Base.metadata.create_all(conn)

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

    