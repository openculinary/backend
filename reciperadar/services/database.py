from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

DB_URI = 'postgresql+pg8000://api@postgresql/api'


class Database(object):

    def __init__(self):
        self.engine = create_engine(DB_URI)
        self.session_cls = sessionmaker(
            bind=self.engine,
            autoflush=False
        )

    def get_session(self):
        return self.session_cls()


def create_schema():
    import reciperadar  # noqa
    from reciperadar.models.base import Storable

    db = Database()
    Storable.metadata.create_all(bind=db.engine)


if __name__ == '__main__':
    create_schema()
