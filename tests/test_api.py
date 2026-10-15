import os
import tempfile
import unittest

import database


class UserApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        handle, cls.test_db = tempfile.mkstemp(suffix=".db")
        os.close(handle)
        database.DATABASE = cls.test_db

        from app import app

        app.config["TESTING"] = True
        cls.client = app.test_client()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)

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
