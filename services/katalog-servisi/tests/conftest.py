import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Taban
import app.models  # noqa: F401  (tabloları kaydeder)


@pytest.fixture
def oturum():
    motor = create_engine("sqlite://")
    Taban.metadata.create_all(motor)
    with sessionmaker(bind=motor)() as o:
        yield o
