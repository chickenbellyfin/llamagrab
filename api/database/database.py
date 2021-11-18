from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()

class Database:
  def __init__(self, base_path, db_file_name='data.db', poolclass=None):
    db_file_path = os.path.join(base_path, db_file_name)
    db_url = f'sqlite:///{db_file_path}'
    # poolclass=StaticPool for inmemory sqlite (unit tests)
    #  https://stackoverflow.com/a/61085725
    self.engine = create_engine(
        db_url, connect_args={"check_same_thread": False}, poolclass=poolclass
    )
    self.SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    Base.metadata.create_all(bind=self.engine)
