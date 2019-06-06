from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


class Database(object):

    def __init__(self):
        self.engine = create_engine('postgresql://')
        self.session_cls = sessionmaker(
            bind=self.engine,
            autoflush=False
        )

    def get_session(self):
        return self.session_cls()
