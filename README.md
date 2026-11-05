# Lab 5 API / Lab 7 - Python Testing

This project is a simple Flask REST API that stores users in SQLite.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run the API

```powershell
python app.py
```

The app runs at `http://127.0.0.1:5000` and creates `database.db` automatically.

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/users` | Get all users |
| GET | `/api/users/<user_id>` | Get one user |
| POST | `/api/users/add` | Add a user |
| PUT | `/api/users/update` | Update a user |
| DELETE | `/api/users/delete/<user_id>` | Delete a user |

For POST and PUT, send JSON with `name`, `email`, `phone`, `address`, and
`country`. PUT also needs `user_id`.

## Postman

In the original Lab 5 project, import these files into Postman (optional;
the collection and environment are not included in the Lab 7 submission):

- `postman/Flask user app.postman_collection.json`
- `postman/Flask user app.postman_environment.json`

Select the imported environment before sending requests. The Add User request
stores the new `user_id` automatically for the GET, PUT, and DELETE requests.

## Test

Run the complete pytest suite from the project directory using the virtual
environment configured above:

```powershell
python -m pytest -v
```

Without activating the existing environment, use:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

The Lab 7 tests are in `test_user_Fatima_Bazzoun.py`. Each test uses a new
temporary SQLite database through pytest's `tmp_path` and `monkeypatch` fixtures.
Only the database path is redirected; SQLite functions and Flask handlers run
normally. The database path is changed before importing `app.py`, because app
import initializes the table. The original `database.db` is never used by tests.

**Initialization mismatch:** Lab 7 asks for specified initial users. This Lab 5
implementation only creates an empty `users` table, and no initial-user list was
provided. The startup test verifies the real schema and empty initial state.
It does not claim seeded-user compliance or add seed data to the application.
The sample users in fixtures and Postman requests are test inputs, not seeds.

| Lab 7 requirement | Primary test in `test_user_Fatima_Bazzoun.py` |
| --- | --- |
| 1. Database creation / initial users | `test_database_creation_on_app_start_has_no_seed_users` (creation verified; seed requirement mismatch above) |
| 2. Insert user | `test_insert_user` |
| 3. Get all users | `test_get_all_users` |
| 4. Get user by ID | `test_get_user_by_id` |
| 5. Update user | `test_update_user` |
| 6. Delete user | `test_delete_user` |
| 7. API get user | `test_api_get_user` |
| 8. API add user | `test_api_add_user` |
| 9. API update user | `test_api_update_user` |
| 10. API delete user | `test_api_delete_user` |

Additional tests verify repeated initialization preserves data, missing IDs,
empty and populated API lists, and validation failures without data changes.
API assertions check status codes and complete JSON responses, plus persisted
database state for writes. POST success returns 201; GET, PUT and DELETE success
return 200. Missing users return 404 and invalid required data returns 400.

The existing unittest test remains available and is also collected by pytest.
Its setup now creates a fresh database per test and restores the database path
and Flask testing configuration during cleanup. To run it separately:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

Verified on November 5, 2026 with Python 3.12.1 and pytest 9.2.0:
`python -m pytest -v` collected 27 tests and reported **27 passed in 0.88s**,
with no failures, skips or expected failures. This includes 26 Lab 7 cases
(parameterized cases counted separately) and the original Lab 5 API test.
The original unittest also passed separately. No production source was changed.
The original database's SHA-256, size and modification timestamp were unchanged.

## Moodle submission and screenshot

The separate `Lab7-Fatima-Bazzoun` folder and `Lab7-Fatima-Bazzoun.zip` contain
application source, both test files, `requirements.txt`, `pytest.ini`, and this
README. No existing database, environment, credentials, caches, Git history or
generated test output is included. The pytest configuration excludes the copied
submission folder when running tests in the original project.

For the successful-test screenshot, open `test_user_Fatima_Bazzoun.py` in VS Code.
In the integrated PowerShell terminal, activate the existing environment and run:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest -v
```

Expand the terminal so the command, collected test count, test names with PASSED,
and final passing summary are visible. Capture the project Explorer and test-file
tab as well. If activation is blocked by PowerShell policy, use the direct
`.\.venv\Scripts\python.exe -m pytest -v` command instead.
