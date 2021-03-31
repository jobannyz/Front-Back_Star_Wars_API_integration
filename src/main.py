"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Favorites, Characters, Planets

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def list_user():
    all_user = User.query.all()
    all_user = list(map(lambda x: x.serialize(), all_user))
    return jsonify(all_user), 200

@app.route('/planets', methods=['GET'])
def list_planets():
    all_planets = Planets.query.all()
    all_planets = list(map(lambda x: x.serialize(), all_planets))
    return jsonify(all_planets), 200

@app.route('/characters', methods=['GET'])
def list_characters():
    all_characters = Characters.query.all()
    all_characters = list(map(lambda x: x.serialize(), all_characters))
    return jsonify(all_characters), 200

@app.route('/updated_favorites', methods=['GET'])
def list_favorites():
    all_favorites = Favorites.query.all()
    all_favorites = list(map(lambda x: x.serialize(), all_favorites))
    return jsonify(all_favorites), 200

@app.route("/favorites", methods=["GET"])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user_favorites = Favorites.query.filter_by(user_id=current_user_id)
    user_favorites = list(map(lambda x: x.serialize(), user_favorites))

    return jsonify(user_favorites), 200

@app.route('/user', methods=['POST'])
def create_user():
    body = request.get_json()
    if body is None:
        return 'El cuerpo del request es Null', 400
    if 'email' not in body:
        return 'Especificar email', 400
    if 'password' not in body:
        return 'Especificar password', 400
    
    user = User()
    user.email = body['email']
    user.password = body['password']
    user.is_active = True

    db.session.add(user) # agrega el usuario a la base de datos
    db.session.commit() # guarda los cambios

    response_body = {
        "msg": "El usuario ha sido agregado correctamente"
    }

    return jsonify(response_body), 200

@app.route('/favorites', methods=['POST'])
@jwt_required()
def create_favorites():
    current_user_id = get_jwt_identity()
    
    body = request.get_json()
    if body is None:
        return 'El cuerpo del request es Null', 400
    if 'name' not in body:
        return 'Especificar nombre del favorito', 400
    
    favorites = Favorites()
    favorites.user_id = current_user_id
    favorites.name = body['name']

    db.session.add(favorites) # agrega el usuario a la base de datos
    db.session.commit() # guarda los cambios

    response_body = {
        "msg": "El Favorito ha sido agregado correctamente"
    }

    return jsonify(response_body), 200

@app.route('/favorites', methods=['DELETE'])
@jwt_required()
def delete_favorites():
    current_user_id = get_jwt_identity()
    
    body = request.get_json()
    if body is None:
        return 'El cuerpo del request es Null', 400
    if 'name' not in body:
        return 'Especificar nombre del favorito', 400
    
    favorites = Favorites()
    favorites.user_id = current_user_id
    favorites.name = body['name']

    db.session.add(favorites) # agrega el usuario a la base de datos
    db.session.commit() # guarda los cambios

    response_body = {
        "msg": "El Favorito ha sido agregado correctamente"
    }

    return jsonify(response_body), 200

@app.route("/token", methods=["POST"])
def create_token():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    # Query your database for username and password
    user = User.query.filter_by(email=email, password=password).first()
    if user is None:
        # the user was not found on the database
        return jsonify({"msg": "Correo electrónico o contraseña erróneos"}), 401
    
    # create a new token with the user id inside
    access_token = create_access_token(identity=user.id)
    return jsonify({ "token": access_token, "user_id": user.id })

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
