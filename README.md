# Lab 5 - Postman and APIs

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

Import these files into Postman:

- `postman/Flask user app.postman_collection.json`
- `postman/Flask user app.postman_environment.json`

Select the imported environment before sending requests. The Add User request
stores the new `user_id` automatically for the GET, PUT, and DELETE requests.

## Test

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```
