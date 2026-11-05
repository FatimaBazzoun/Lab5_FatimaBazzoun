"""EECE 435L Lab 7: real SQLite CRUD and Flask API tests.

Startup creates an EMPTY users table. The Lab 5 app does not seed users;
no specified seed list was supplied. Test data below is fixture data only.
"""

from contextlib import closing
import importlib.util
from pathlib import Path

import pytest

import database


@pytest.fixture
def isolated_database(tmp_path, monkeypatch):
    """Redirect real SQLite connections before importing app (which creates tables)."""
    db_path = tmp_path / "lab7.sqlite3"
    monkeypatch.setattr(database, "DATABASE", str(db_path))
    return db_path


@pytest.fixture
def db(isolated_database):
    database.create_db_table()
    return database


@pytest.fixture
def client(db, monkeypatch):
    # Never import app during collection: its startup writes to DATABASE.
    from app import app

    monkeypatch.setitem(app.config, "TESTING", True)
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def user():
    return {
        "name": "Fatima Bazzoun",
        "email": "fatima@example.com",
        "phone": "03123456",
        "address": "Beirut",
        "country": "Lebanon",
    }


@pytest.fixture
def other_user():
    return {
        "name": "Sara Ali",
        "email": "sara@example.com",
        "phone": "03000000",
        "address": "Tripoli",
        "country": "Lebanon",
    }


def test_database_creation_on_app_start_has_no_seed_users(isolated_database):
    """Requirement 1: verify real startup; specified initial users are absent."""
    assert not isolated_database.exists()
    # Execute startup afresh even if another test already imported app.
    spec = importlib.util.spec_from_file_location(
        "lab7_startup_app", Path(__file__).with_name("app.py")
    )
    startup_app = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(startup_app)

    assert isolated_database.is_file()
    with closing(database.connect_to_db()) as connection:
        columns = connection.execute("PRAGMA table_info(users)").fetchall()
        assert [(row["name"], row["type"], row["pk"]) for row in columns] == [
            ("user_id", "INTEGER", 1),
            ("name", "TEXT", 0),
            ("email", "TEXT", 0),
            ("phone", "TEXT", 0),
            ("address", "TEXT", 0),
            ("country", "TEXT", 0),
        ]
    assert database.get_users() == []
    with startup_app.app.test_client() as startup_client:
        response = startup_client.get("/api/users")
        assert response.status_code == 200
        assert response.get_json() == []


def test_insert_user(db, user):
    """Requirement 2: insert and persist every field under a generated ID."""
    user_id = db.insert_user(user)
    assert isinstance(user_id, int) and user_id > 0
    assert db.get_user_by_id(user_id) == {"user_id": user_id, **user}


def test_get_all_users(db, user, other_user):
    """Requirement 3: empty results, then complete records for multiple users."""
    assert db.get_users() == []
    first_id = db.insert_user(user)
    second_id = db.insert_user(other_user)
    assert first_id != second_id
    assert sorted(db.get_users(), key=lambda row: row["user_id"]) == [
        {"user_id": first_id, **user},
        {"user_id": second_id, **other_user},
    ]


def test_get_user_by_id(db, user, other_user):
    """Requirement 4: select the requested user among multiple records."""
    db.insert_user(other_user)
    user_id = db.insert_user(user)
    assert db.get_user_by_id(user_id) == {"user_id": user_id, **user}


def test_update_user(db, user, other_user):
    """Requirement 5: change all fields, preserve the ID and unrelated user."""
    user_id = db.insert_user(user)
    untouched_id = db.insert_user(user)
    updated = {"user_id": user_id, **other_user}
    assert db.update_user(updated) is True
    assert db.get_user_by_id(user_id) == updated
    assert db.get_user_by_id(untouched_id) == {"user_id": untouched_id, **user}
    assert len(db.get_users()) == 2


def test_delete_user(db, user, other_user):
    """Requirement 6: remove only the requested user and persist the deletion."""
    user_id = db.insert_user(user)
    remaining_id = db.insert_user(other_user)
    assert db.delete_user(user_id) is True
    assert db.get_user_by_id(user_id) is None
    assert db.get_users() == [{"user_id": remaining_id, **other_user}]
    assert db.delete_user(user_id) is False


def test_api_get_user(client, db, user, other_user):
    """Requirement 7: GET returns 200 and the complete requested record."""
    db.insert_user(other_user)
    user_id = db.insert_user(user)
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    assert response.get_json() == {"user_id": user_id, **user}


def test_api_add_user(client, db, user):
    """Requirement 8: POST returns 201, message, generated ID and persists data."""
    response = client.post("/api/users/add", json=user)
    assert response.status_code == 201
    data = response.get_json()
    user_id = data["user_id"]
    assert isinstance(user_id, int) and user_id > 0
    assert data == {"message": "User added successfully.", "user_id": user_id}
    assert db.get_users() == [{"user_id": user_id, **user}]
    retrieved = client.get(f"/api/users/{user_id}")
    assert retrieved.status_code == 200
    assert retrieved.get_json() == {"user_id": user_id, **user}


def test_api_update_user(client, db, user, other_user):
    """Requirement 9: PUT returns 200 and the exact message; fields persist."""
    user_id = db.insert_user(user)
    untouched_id = db.insert_user(user)
    updated = {"user_id": user_id, **other_user}
    response = client.put("/api/users/update", json=updated)
    assert response.status_code == 200
    assert response.get_json() == {"message": "User updated successfully."}
    assert db.get_user_by_id(user_id) == updated
    assert db.get_user_by_id(untouched_id) == {"user_id": untouched_id, **user}
    retrieved = client.get(f"/api/users/{user_id}")
    assert retrieved.status_code == 200
    assert retrieved.get_json() == updated


def test_api_delete_user(client, db, user, other_user):
    """Requirement 10: DELETE returns 200, exact message and removes the row."""
    user_id = db.insert_user(user)
    remaining_id = db.insert_user(other_user)
    response = client.delete(f"/api/users/delete/{user_id}")
    assert response.status_code == 200
    assert response.get_json() == {"message": "User deleted successfully."}
    assert db.get_users() == [{"user_id": remaining_id, **other_user}]
    retrieved = client.get(f"/api/users/{user_id}")
    assert retrieved.status_code == 404
    assert retrieved.get_json() == {"error": "User not found."}


def test_create_db_table_preserves_existing_users(db, user):
    user_id = db.insert_user(user)
    db.create_db_table()
    db.create_db_table()
    assert db.get_users() == [{"user_id": user_id, **user}]


@pytest.mark.parametrize("operation", ["get", "update", "delete"])
def test_database_missing_user(db, user, operation):
    if operation == "get":
        assert db.get_user_by_id(999) is None
    elif operation == "update":
        assert db.update_user({"user_id": 999, **user}) is False
    else:
        assert db.delete_user(999) is False
    assert db.get_users() == []


@pytest.mark.parametrize("populated", [False, True], ids=["empty", "populated"])
def test_api_get_all_users(client, db, user, other_user, populated):
    expected = []
    if populated:
        for record in (user, other_user):
            user_id = db.insert_user(record)
            expected.append({"user_id": user_id, **record})
    response = client.get("/api/users")
    assert response.status_code == 200
    assert sorted(response.get_json(), key=lambda row: row["user_id"]) == expected


@pytest.mark.parametrize(
    "method, endpoint",
    [("GET", "/api/users/999"), ("PUT", "/api/users/update"),
     ("DELETE", "/api/users/delete/999")],
)
def test_api_missing_user(client, db, user, method, endpoint):
    kwargs = {"json": {"user_id": 999, **user}} if method == "PUT" else {}
    response = client.open(endpoint, method=method, **kwargs)
    assert response.status_code == 404
    assert response.get_json() == {"error": "User not found."}
    assert db.get_users() == []


@pytest.mark.parametrize(
    "method, endpoint", [("POST", "/api/users/add"), ("PUT", "/api/users/update")]
)
@pytest.mark.parametrize("payload", [None, {}], ids=["no-json", "empty-object"])
def test_api_rejects_empty_data(client, db, method, endpoint, payload):
    kwargs = {} if payload is None else {"json": payload}
    response = client.open(endpoint, method=method, **kwargs)
    assert response.status_code == 400
    assert response.get_json() == {"error": "Send user data as JSON."}
    assert db.get_users() == []


@pytest.mark.parametrize(
    "method, endpoint", [("POST", "/api/users/add"), ("PUT", "/api/users/update")]
)
def test_api_rejects_missing_fields(client, db, user, method, endpoint):
    user_id = db.insert_user(user)
    payload = {"user_id": user_id, **user}
    del payload["email"]
    response = client.open(endpoint, method=method, json=payload)
    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing fields: email"}
    assert db.get_users() == [{"user_id": user_id, **user}]


def test_api_update_requires_user_id(client, db, user):
    user_id = db.insert_user(user)
    response = client.put("/api/users/update", json=user)
    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing fields: user_id"}
    assert db.get_users() == [{"user_id": user_id, **user}]
