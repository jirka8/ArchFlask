import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

#basedir = os.path.abspath(os.path.dirname(__file__))

#engine = create_engine('sqlite:///' + os.path.join(basedir, 'app.db'))
engine = create_engine('postgresql://postgres:aspop@localhost/archeodb', echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)