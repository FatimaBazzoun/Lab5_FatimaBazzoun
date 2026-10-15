import os
import sqlite3


DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")


def connect_to_db():
    """Open a connection to the SQLite database."""
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_db_table():
    """Create the users table if it does not already exist."""
    connection = connect_to_db()
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            country TEXT
        )
        """
    )
    connection.commit()
    connection.close()


def insert_user(user):
    """Insert one user and return the new user id."""
    connection = connect_to_db()
    cursor = connection.execute(
        """
        INSERT INTO users (name, email, phone, address, country)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user["name"], user["email"], user["phone"], user["address"], user["country"]),
    )
    connection.commit()
    user_id = cursor.lastrowid
    connection.close()
    return user_id


def get_users():
    """Return all users as a list of dictionaries."""
    connection = connect_to_db()
    rows = connection.execute("SELECT * FROM users").fetchall()
    connection.close()
    return [dict(row) for row in rows]


def get_user_by_id(user_id):
    """Return one user, or None when the id does not exist."""
    connection = connect_to_db()
    row = connection.execute(
        "SELECT * FROM users WHERE user_id = ?", (user_id,)
    ).fetchone()
    connection.close()
    return dict(row) if row else None


def update_user(user):
    """Update one user and return True when a row was changed."""
    connection = connect_to_db()
    cursor = connection.execute(
        """
        UPDATE users
        SET name = ?, email = ?, phone = ?, address = ?, country = ?
        WHERE user_id = ?
        """,
        (
            user["name"],
            user["email"],
            user["phone"],
            user["address"],
            user["country"],
            user["user_id"],
        ),
    )
    connection.commit()
    was_updated = cursor.rowcount > 0
    connection.close()
    return was_updated


def delete_user(user_id):
    """Delete one user and return True when a row was deleted."""
    connection = connect_to_db()
    cursor = connection.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    connection.commit()
    was_deleted = cursor.rowcount > 0
    connection.close()
    return was_deleted
