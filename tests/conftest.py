import pytest
from fastapi.testclient import TestClient
from src.app import app, get_activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def fresh_activities():
    """Return a fresh copy of activities data for each test"""
    return get_activities()


@pytest.fixture(autouse=True, scope="function")
def reset_activities():
    """Reset the global activities data before each test for isolation"""
    import src.app
    src.app.activities = src.app.get_activities()