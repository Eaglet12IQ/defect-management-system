import sys
from pathlib import Path

# Add the project root to the Python path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from sqlalchemy import create_engine
from app.main import app
from app.models.base import Base
from sqlalchemy.orm import sessionmaker
from app.core.database import get_db
from fastapi.testclient import TestClient

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db dependency for tests
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()  # Rollback to ensure clean state
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Helper functions
def register_user(email, username, password):
    response = client.post("/api/auth/register", json={
        "email": email,
        "username": username,
        "password": password,
        "re_password": password
    })
    return response

def login_user(username, password):
    response = client.post("/api/auth/login", json={
        "username": username,
        "password": password
    })
    if response.status_code != 200:
        pytest.fail(f"Login failed: {response.status_code}, {response.json()}")
    data = response.json()
    access_token = data.get("access_token")
    if not access_token:
        pytest.fail("Access token not found in login response")
    return access_token

# User Auth Tests
def test_register_user(test_db):
    response = register_user("testuser@example.com", "testuser", "testpassword")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["username"] == "testuser"

def test_register_user_existing_email(test_db):
    response = register_user("testuser@example.com", "testuser2", "testpassword")
    assert response.status_code == 400

def test_login_success(test_db):
    access_token = login_user("testuser", "testpassword")
    assert access_token is not None

def test_login_wrong_password(test_db):
    response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 400  # Adjust based on API

def test_logout(test_db):
    access_token = login_user("testuser", "testpassword")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/api/auth/logout", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Пользователь вышел из системы."

def test_delete_user(test_db):
    access_token = login_user("testuser", "testpassword")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.delete("/api/auth/delete", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Пользователь удален."

# Collection Tests
def test_create_collection(test_db):
    register_user("collector@example.com", "collector", "collectorpass")
    access_token = login_user("collector", "collectorpass")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/api/collections/create", data={
        "name": "Test Collection",
        "description": "Test Description"
    }, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Collection"

def test_get_collections(test_db):
    response = client.get("/api/collections")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_collections_grouped(test_db):
    response = client.get("/api/collections/grouped")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_collection_by_id(test_db):
    access_token = login_user("collector", "collectorpass")
    headers = {"Authorization": f"Bearer {access_token}"}
    create_response = client.post("/api/collections/create", data={
        "name": "Collection For Get",
        "description": "Description"
    }, headers=headers)
    assert create_response.status_code == 200
    collection_id = create_response.json().get("id")
    assert collection_id is not None
    response = client.get(f"/api/collections/{collection_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == collection_id

def test_get_collection_by_id_not_found(test_db):
    response = client.get("/api/collections/999999")
    assert response.status_code == 404

def test_update_collection_authorized(test_db):
    access_token = login_user("collector", "collectorpass")
    headers = {"Authorization": f"Bearer {access_token}"}
    create_response = client.post("/api/collections/create", data={
        "name": "Collection To Update",
        "description": "Description"
    }, headers=headers)
    assert create_response.status_code == 200
    collection_id = create_response.json().get("id")
    assert collection_id is not None
    response = client.patch(f"/api/collections/update/{collection_id}", data={
        "name": "Updated Name",
        "description": "Updated Description"
    }, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"

def test_update_collection_unauthorized(test_db):
    response = client.patch("/api/collections/update/999999", data={
        "name": "Name",
        "description": "Description"
    })
    assert response.status_code in (401, 403), f"Expected 401 or 403, got {response.status_code}: {response.json()}"

def test_delete_collection_authorized(test_db):
    access_token = login_user("collector", "collectorpass")
    headers = {"Authorization": f"Bearer {access_token}"}
    create_response = client.post("/api/collections/create", data={
        "name": "Collection To Delete",
        "description": "Description"
    }, headers=headers)
    assert create_response.status_code == 200
    collection_id = create_response.json().get("id")
    assert collection_id is not None
    response = client.delete(f"/api/collections/delete/{collection_id}", headers=headers)
    assert response.status_code == 204

def test_delete_collection_unauthorized(test_db):
    response = client.delete("/api/collections/delete/999999")
    assert response.status_code in (401, 403, 404), f"Expected 401, 403, or 404, got {response.status_code}: {response.json()}"

# Profile Tests
def test_get_collectors_list(test_db):
    response = client.get("/api/profiles/list")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_profile(test_db):
    response = register_user("profileuser@example.com", "profileuser", "profilepass")
    access_token = login_user("profileuser", "profilepass")
    data = response.json()
    id = data["id"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get(f"/api/profiles/{id}", headers=headers)
    assert response.status_code == 200

def test_update_user_info(test_db):
    response = register_user("updateuser@example.com", "updateuser", "updatepass")
    access_token = login_user("updateuser", "updatepass")
    data = response.json()
    id = data["id"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.patch(f"/api/profiles/users/{id}", json={
        "username": "updateduser",
        "email": "updateduser@example.com"
    }, headers=headers)
    assert response.status_code == 200

def test_update_collector_info(test_db):
    response = register_user("updatecollector@example.com", "updatecollector", "updatepass")
    access_token = login_user("updatecollector", "updatepass")
    data = response.json()
    id = data["id"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.patch(f"/api/profiles/collectors/{id}", json={
        "country": "New Country",
        "phone_number": "1234567890"
    }, headers=headers)
    assert response.status_code == 200

def test_create_stamp(test_db):
    # Register and login user
    register_user("stampcollector@example.com", "stampcollector", "stamppass")
    access_token = login_user("stampcollector", "stamppass")
    headers = {"Authorization": f"Bearer {access_token}"}

    # Create a collection first
    response = client.post("/api/collections/create", data={
        "name": "Stamp Collection",
        "description": "Collection for stamps"
    }, headers=headers)
    assert response.status_code == 200
    collection_id = response.json().get("id")
    assert collection_id is not None

    # Prepare a dummy image file for upload
    import io
    image_content = io.BytesIO(b"fake image data")
    image_content.name = "test_image.jpg"

    # Create a stamp
    response = client.post(
        "/api/stamps/create",
        data={
            "name": "Test Stamp",
            "serial_number": "SN123456",
            "country": "Testland",
            "year": 2020,
            "circulation": 1000,
            "cost": 1500.0,
            "perforation": "Type A",
            "topic": "Test Topic",
            "features": "Feature1, Feature2",
            "collection_id": collection_id
        },
        files={"image": ("test_image.jpg", image_content, "image/jpeg")},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Stamp"
    assert data["serial_number"] == "SN123456"
    assert data["rarity"] == "Редкая"
