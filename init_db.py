import pandas as pd
from sqlalchemy import insert, select, text
from sqlalchemy.orm import Session

import model
from db import engine


def init_db():
    def load_row(conn):
            tbl = 'raw_data'
            conn.execute(f'drop table if exists {tbl} ')
            df = pd.read_csv('./museums-urls.csv')
            df.to_sql(tbl, conn, index=False)

    def init_models(conn):
        for meta_tbl in model.Base.metadata.tables.values():
            conn.execute(text(f'drop table if exists {meta_tbl} cascade'))
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
                            .from_select(['ref_count', 'url'], select(text(q)))
            )
            session.commit()

    with engine.connect() as conn:
        load_row(conn)
        init_models(conn)
    seeds()

def main():
    init_db()


if __name__ == '__main__':
    main()