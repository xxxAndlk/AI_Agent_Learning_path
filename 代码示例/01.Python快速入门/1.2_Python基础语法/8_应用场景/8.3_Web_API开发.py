# 使用Flask快速搭建API
from flask import Flask, jsonify, request

app = Flask(__name__)

users = {}

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(list(users.values()))

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    if user_id in users:
        return jsonify(users[user_id])
    return jsonify({"error": "User not found"}), 404

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    user_id = str(len(users) + 1)
    users[user_id] = {"id": user_id, **data}
    return jsonify(users[user_id]), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)
