import sqlite3

from flask import Flask, request

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('chatroom.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/', methods=['GET'])
def home():
    if request.method == 'GET':
        return "hello world"


@app.route('/add_user', methods=['POST'])
def add_user():
    conn = get_db_connection()
    if request.method == 'POST':
        data = request.get_json()
        for user in data['USERS']:
            try:
                conn.execute('INSERT INTO USERS '
                             '(NICKNAME, PUBLIC_KEY) '
                             'VALUES (?,?)',
                             (user['NICKNAME'], user['PUBLIC_KEY']))
                conn.commit()
            except sqlite3.IntegrityError:
                return "ERROR: User already exists"
        conn.close()
        return "INFO: Users added successfully"


if __name__ == '__main__':
    app.run(debug=True, port=5000)
