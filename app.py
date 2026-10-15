from flask import Flask, jsonify, request
from flask_cors import CORS

from database import (
    create_db_table,
    delete_user,
    get_user_by_id,
    get_users,
    insert_user,
    update_user,
)


app = Flask(__name__)
CORS(app)

# The table is created automatically every time the application starts.
create_db_table()


USER_FIELDS = ["name", "email", "phone", "address", "country"]


def check_user_data(user, needs_id=False):
    """Return an error response when required fields are missing."""
    if not user:
        return jsonify({"error": "Send user data as JSON."}), 400

    fields = USER_FIELDS.copy()
    if needs_id:
        fields.append("user_id")

    missing_fields = [field for field in fields if field not in user]
    if missing_fields:
        return jsonify({"error": "Missing fields: " + ", ".join(missing_fields)}), 400

    return None


@app.route("/api/users", methods=["GET"])
def get_all_users():
    return jsonify(get_users()), 200


@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_one_user(user_id):
    user = get_user_by_id(user_id)
    if user is None:
        return jsonify({"error": "User not found."}), 404
    return jsonify(user), 200


@app.route("/api/users/add", methods=["POST"])
def add_user():
    user = request.get_json(silent=True)
    error = check_user_data(user)
    if error:
        return error

    user_id = insert_user(user)
    return jsonify({"message": "User added successfully.", "user_id": user_id}), 201


@app.route("/api/users/update", methods=["PUT"])
def edit_user():
    user = request.get_json(silent=True)
    error = check_user_data(user, needs_id=True)
    if error:
        return error

    if not update_user(user):
        return jsonify({"error": "User not found."}), 404
    return jsonify({"message": "User updated successfully."}), 200


@app.route("/api/users/delete/<int:user_id>", methods=["DELETE"])
def remove_user(user_id):
    if not delete_user(user_id):
        return jsonify({"error": "User not found."}), 404
    return jsonify({"message": "User deleted successfully."}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
