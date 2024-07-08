from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Session
from sqlmodel import Field, SQLModel
from fastapi.testclient import TestClient  
from sqlalchemy import create_engine
from unittest.mock import MagicMock

import pytest,uuid
import bookmgmt ,database
from main import app
from database import get_db

# DATABASE_URL = "sqlite:///./test1.db"  # Example using SQLite
# Base = declarative_base()

# engine = create_engine(DATABASE_URL)
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLModel.metadata.create_all(engine)

TestingSessionLocal = MagicMock()


@pytest.fixture(scope="function")
def override_get_db():
    try:
        ''' Create a session, close after that session'''
        # session = TestingSessionLocal()
        yield TestingSessionLocal
    finally:
        TestingSessionLocal.close()


app.dependency_overrides[get_db]=override_get_db

@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client

@pytest.fixture
def mock_db_session():
    return TestingSessionLocal

@pytest.fixture(scope='module')
def valid_user():
    valid_user=database.UserCredentials(email="testabc@gmail.com",pwd="")
    return valid_user

@pytest.fixture(scope='module')
def valid_book():
    valid_book=database.Book(name="",author="",published_year="",book_summary="")
    return valid_book

# # Fixture to generate a random book id
# @pytest.fixture()
# def book_id() ->uuid.UUID:
#     '''Generate a random book Id '''
#     return int(uuid.uuid1)

# Fixture to Generate a pay load
@pytest.fixture(scope='module')
def book_update_payload():
    '''Generate a book payload'''
    return {
        "book_id":2000,
        "name":"Python",
        "published_year":2021,
        "book_summary":"book summary"
    }

@pytest.fixture(scope='module')
def book_payload():
    '''Generate a book payload'''
    return {
        "name":"Python_world",
        "author":"joe",
        "published_year": 2009,
        "book_summary":"book summary"
    }
