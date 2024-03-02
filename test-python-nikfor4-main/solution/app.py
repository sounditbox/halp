import os
import jwt
from flask import Flask, jsonify, request, current_app
import psycopg2
from flask_paginate import Pagination, get_page_args
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models import Post, Like, db




app = Flask(__name__)


def connect_to_db():
    conn = psycopg2.connect(
        dbname=os.environ.get('POSTGRES_DATABASE'),
        user=os.environ.get('POSTGRES_USERNAME'),
        password=os.environ.get('POSTGRES_PASSWORD'),
        host=os.environ.get('POSTGRES_HOST'),
        port=os.environ.get('POSTGRES_PORT')
    )
    return conn

@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'ok'})

@app.route('/api/countries', methods=['GET'])
def get_countries():
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM countries")
        countries = cur.fetchall()

        region = request.args.get('region')
        if region:
            filtered_countries = [country for country in countries if country[3] == region]
            return jsonify(filtered_countries)
        else:
            return jsonify(countries)

    except psycopg2.Error as e:
        return jsonify({'error': str(e)})

    finally:
        if conn:
            conn.close()
@app.route('/api/countries/<alpha2>', methods=['GET'])
def get_country_by_alpha2(alpha2):
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM countries WHERE alpha2 = %s", (alpha2,))
        country = cur.fetchone()

        if country:
            return jsonify(country)
        else:
            return jsonify({'error': 'Country not found'}), 404

    except psycopg2.Error as e:
        return jsonify({'error': str(e)})

    finally:
        if conn:
            conn.close()
@app.route('/api/countries', methods=['GET'])
def get_countries():
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        region = request.args.get('region')

        if region:
            cur.execute("SELECT * FROM countries WHERE region = %s", (region,))
        else:
            cur.execute("SELECT * FROM countries")

        countries = cur.fetchall()

        return jsonify(countries)

    except psycopg2.Error as e:
        return jsonify({'error': str(e)})

    finally:
        if conn:
            conn.close()
@app.route('/api/countries/<alpha2>', methods=['GET'])
def get_country_by_alpha2(alpha2):
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM countries WHERE alpha2 = %s", (alpha2,))
        country = cur.fetchone()

        if country:
            return jsonify(country)
        else:
            return jsonify({'error': 'Country not found'}), 404

    except psycopg2.Error as e:
        return jsonify({'error': str(e)})

    finally:
        if conn:
            conn.close()
@app.route('/api/countries', methods=['GET'])
def get_countries():
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        region = request.args.get('region')

        if region:
            cur.execute("SELECT * FROM countries WHERE region = %s", (region,))
        else:
            cur.execute("SELECT * FROM countries")

        countries = cur.fetchall()

        return jsonify(countries)

    except psycopg2.Error as e:
        return jsonify({'error': str(e)})

    finally:
        if conn:
            conn.close()
@app.route('/api/profiles/<string:login>', methods=['GET'])
def get_profile_by_login(login):
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE login = %s", (login,))
        user = cur.fetchone()

        if user:
            profile = {
                'login': user[0],
                'email': user[1],
                'country_code': user[2],
                'is_public': user[3],
                'phone': user[4],
                'image': user[5]
            }
            return jsonify(profile)
        else:
            return jsonify({'error': 'User not found'}), 404

    except psycopg2.Error as e:
        return jsonify({'error': str(e)})

    finally:
        if conn:
            conn.close()
users = {
    "user1": {
        "password": "password123",
        "tokens": []
    }
}

@app.route("/me/updatePassword", methods=["POST"])
def update_password():
    data = request.json
    new_password = data.get("new_password")
    current_password = data.get("current_password")
    token = request.headers.get("Authorization")

    user_login = get_user_login_from_token(token)
    if not user_login:
        return jsonify({"message": "Unauthorized"}), 401

    if users.get(user_login, {}).get("password") != current_password:
        return jsonify({"message": "Current password is incorrect"}), 400

    users[user_login]["password"] = new_password
    users[user_login]["tokens"] = []

    return jsonify({"message": "Password updated successfully"})

def get_user_login_from_token(token: str) -> str:
    return "user1"
# Эндпоинт для добавления друга
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/dbname'
db = SQLAlchemy(app)


class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    friend_id = db.Column(db.Integer, nullable=False)

    def __init__(self, user_id, friend_id):
        self.user_id = user_id
        self.friend_id = friend_id


@app.route('/friends/add', methods=['POST'])
def add_friend():
    data = request.get_json()
    user_id = data.get('user_id')
    friend_id = data.get('friend_id')

    if not user_id or not friend_id:
        return jsonify({"error": "User ID or Friend ID is missing"}), 400

    # Проверяем, не является ли пользователь уже другом
    if Friend.query.filter_by(user_id=user_id, friend_id=friend_id).first():
        return jsonify({"error": "User is already a friend"}), 400

    # Добавляем друга в базу данных
    friend = Friend(user_id=user_id, friend_id=friend_id)
    db.session.add(friend)
    db.session.commit()

    return jsonify({"message": "Friend added successfully"})


@app.route('/friends/remove', methods=['POST'])
def remove_friend():
    data = request.get_json()
    user_id = data.get('user_id')
    friend_id = data.get('friend_id')

    if not user_id or not friend_id:
        return jsonify({"error": "User ID or Friend ID is missing"}), 400

    # Проверяем, является ли пользователь другом
    friend = Friend.query.filter_by(user_id=user_id, friend_id=friend_id).first()
    if not friend:
        return jsonify({"error": "User is not a friend"}), 400

    # Удаляем друга из базы данных
    db.session.delete(friend)
    db.session.commit()

    return jsonify({"message": "Friend removed successfully"})
@app.route('/friends', methods=['GET'])
def get_friends():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"error": "User ID is missing"}), 400

    # Получаем список друзей пользователя из базы данных
    friends = Friend.query.filter_by(user_id=user_id).all()

    # Преобразуем результат в формат JSON
    friends_list = [{"friend_id": friend.friend_id} for friend in friends]

    return jsonify({"friends": friends_list})

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Post {self.id}>"
@app.route('/posts', methods=['POST'])
def create_post():
    data = request.json
    user_id = data.get('user_id')
    content = data.get('content')

    if not user_id or not content:
        return jsonify({"error": "User ID or content is missing"}), 400

    # Создаем новую публикацию в базе данных
    post = Post(user_id=user_id, content=content)
    db.session.add(post)
    db.session.commit()

    return jsonify({"message": "Post created successfully"}), 201

@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get(post_id)

    if not post:
        return jsonify({"error": "Post not found"}), 404

    # Преобразуем данные о публикации в формат JSON и возвращаем
    return jsonify({"id": post.id, "user_id": post.user_id, "content": post.content, "created_at": post.created_at})

@app.route('/api/posts/feed', methods=['GET'])
def get_news_feed():
    user_id = get_user_id_from_token(request.headers.get('Authorization'))

    if user_id is None:
        return jsonify({'error': 'Unauthorized'}), 401

    # Получаем параметры пагинации из запроса
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 5, type=int)

    # Запрос на получение постов из ленты пользователя
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).offset(offset).limit(limit).all()

    # Преобразуем список постов в JSON и отправляем клиенту
    return jsonify([post.serialize() for post in posts])

def get_user_id_from_token(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
    token = parts[1]
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
        return user_id
    except jwt.ExpiredSignatureError:
        return None  # Токен истек
    except jwt.InvalidTokenError:
        return None

@app.route('/api/posts/like', methods=['POST'])
def like_post():
    user_id = get_user_id_from_token(request.headers.get('Authorization'))

    if user_id is None:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    post_id = data.get('post_id')
    reaction = data.get('reaction')  # 'like' or 'dislike'

    if post_id is None or reaction not in ['like', 'dislike']:
        return jsonify({'error': 'Invalid request'}), 400

    # Проверяем, существует ли пост с указанным post_id
    post = Post.query.get(post_id)

    if post is None:
        return jsonify({'error': 'Post not found'}), 404

    # Проверяем, не ставил ли пользователь уже реакцию на этот пост
    existing_reaction = Like.query.filter_by(user_id=user_id, post_id=post_id).first()

    if existing_reaction is not None:
        return jsonify({'error': 'Reaction already exists'}), 400

    # Создаем новую запись в таблице лайков с указанными данными
    new_reaction = Like(user_id=user_id, post_id=post_id, reaction=reaction)
    db.session.add(new_reaction)
    db.session.commit()

    return jsonify({'message': 'Reaction added successfully'}), 200

@app.route('/api/posts/likes', methods=['GET'])
def get_post_likes():
    post_id = request.args.get('post_id')

    if post_id is None:
        return jsonify({'error': 'Invalid request'}), 400

    # Получаем количество лайков и дизлайков для указанного поста
    likes_count = Like.query.filter_by(post_id=post_id, reaction='like').count()
    dislikes_count = Like.query.filter_by(post_id=post_id, reaction='dislike').count()

    return jsonify({'likes_count': likes_count, 'dislikes_count': dislikes_count}), 200

if __name__ == '__main__':
    app.run(debug=True)
