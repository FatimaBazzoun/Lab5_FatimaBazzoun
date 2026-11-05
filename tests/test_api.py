import os
import tempfile
import unittest

import database


class UserApiTests(unittest.TestCase):
    def setUp(self):
        test_directory = tempfile.TemporaryDirectory()
        self.addCleanup(test_directory.cleanup)
        original_database = database.DATABASE
        self.addCleanup(setattr, database, "DATABASE", original_database)
        database.DATABASE = os.path.join(test_directory.name, "test.db")
        # app may already be imported by pytest; initialize each new DB explicitly.
        database.create_db_table()

        from app import app

        self.addCleanup(app.config.__setitem__, "TESTING", app.config["TESTING"])
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_all_api_operations(self):
        user = {
            "name": "Sara Ali",
            "email": "sara@example.com",
            "phone": "03000000",
            "address": "Beirut",
            "country": "Lebanon",
        }

        add_response = self.client.post("/api/users/add", json=user)
        self.assertEqual(add_response.status_code, 201)
        user_id = add_response.get_json()["user_id"]

        all_response = self.client.get("/api/users")
        self.assertEqual(all_response.status_code, 200)
        self.assertEqual(len(all_response.get_json()), 1)

        one_response = self.client.get(f"/api/users/{user_id}")
        self.assertEqual(one_response.status_code, 200)
        self.assertEqual(one_response.get_json()["name"], "Sara Ali")

        user["user_id"] = user_id
        user["country"] = "Lebanon (updated)"
        update_response = self.client.put("/api/users/update", json=user)
        self.assertEqual(update_response.status_code, 200)

        delete_response = self.client.delete(f"/api/users/delete/{user_id}")
        self.assertEqual(delete_response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
