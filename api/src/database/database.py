from alembic.config import Config
from alembic.migration import MigrationContext
from alembic import command
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from loguru import logger
import os

ALEMBIC_SCRIPT_LOCATION = 'src/alembic'

Base = declarative_base()

class Database:
  def __init__(self, base_path, db_file_name='data.db', poolclass=None):
    db_file_path = os.path.join(base_path, db_file_name)
    db_is_new = not os.path.exists(db_file_path)
    db_url = f'sqlite:///{db_file_path}'
    # poolclass=StaticPool for inmemory sqlite (unit tests)
    #  https://stackoverflow.com/a/61085725
    self.engine = create_engine(
        db_url, connect_args={"check_same_thread": False}, poolclass=poolclass
    )
    self.SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    Base.metadata.create_all(bind=self.engine)

    # skip migrations if DB is newly created
    if db_is_new:
        logger.info(f'DB is newly created, setting alembic version to \'head\'')
        alembic_cfg = Config()
        alembic_cfg.set_main_option('script_location', ALEMBIC_SCRIPT_LOCATION)
        alembic_cfg.set_main_option('sqlalchemy.url', db_url)
        command.stamp(alembic_cfg, 'head')


# https://stackoverflow.com/questions/24622170
def run_migrations(base_path: str, db_file_name: str ='data.db') -> None:
    db_file_path = os.path.join(base_path, db_file_name)
    db_url = f'sqlite:///{db_file_path}'
    logger.info(f'Running DB migrations in {ALEMBIC_SCRIPT_LOCATION} on {db_url}')
    alembic_cfg = Config()
    alembic_cfg.set_main_option('script_location', ALEMBIC_SCRIPT_LOCATION)
    alembic_cfg.set_main_option('sqlalchemy.url', db_url)
    command.upgrade(alembic_cfg, 'head')
    