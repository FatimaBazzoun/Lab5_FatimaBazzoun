from flask import Flask
from flask_cors import CORS

from database import create_db_table


app = Flask(__name__)
CORS(app)

# The table is created automatically every time the application starts.
create_db_table()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
