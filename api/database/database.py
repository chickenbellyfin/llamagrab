from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from loguru import logger
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


# https://stackoverflow.com/questions/24622170
def run_migrations(base_path: str, db_file_name: str ='data.db') -> None:
    script_location = 'alembic'
    db_file_path = os.path.join(base_path, db_file_name)
    db_url = f'sqlite:///{db_file_path}'
    logger.info(f'Running DB migrations in {script_location} on {db_url}')
    alembic_cfg = Config()
    alembic_cfg.set_main_option('script_location', script_location)
    alembic_cfg.set_main_option('sqlalchemy.url', db_url)
    command.upgrade(alembic_cfg, 'head')
    