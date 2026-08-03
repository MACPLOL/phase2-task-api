import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, delete
from sqlalchemy.orm import sessionmaker
from models import Task, User
from fastapi.testclient import TestClient
from database import Base, get_db
from main import app
import pytest


load_dotenv()

test_database_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_TEST_NAME"),
)

test_engine = create_engine(test_database_url)

TestSessionLocal = sessionmaker(bind=test_engine)
Base.metadata.create_all(bind=test_engine)

def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    client.post(
        "/users",
        json={
            "email": "taskowner@example.com",
            "password": "Mauro123!",
        },
    )

    login_response = client.post(
        "/login",
        json={
            "email": "taskowner@example.com",
            "password": "Mauro123!",
        },
    )

    access_token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {access_token}",
    }

@pytest.fixture(autouse=True)
def clean_test_database():
    db = TestSessionLocal()

    try:
        db.execute(delete(Task))
        db.execute(delete(User))
        db.commit()

        yield

    finally:
        db.execute(delete(Task))
        db.execute(delete(User))
        db.commit()
        db.close()
