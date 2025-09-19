from flask import Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt, get_jwt_identity
from flask_bcrypt import Bcrypt
import datetime

from config.db import get_db_connection

import os
from dotenv import load_dotenv

load_dotenv()

usuarios_bp = Blueprint('usuarios', __name__)

bcrypt = Bcrypt()

@usuarios_bp.route("/registrar", methods=['POST'])
def registrar():
    data = request.get_json()

    nombre = data.get('nombre')
    email = data.get('email')
    password = data.get('password')

    if not nombre or not email or not password:
        return jsonify({"error": "Faltan datos"}), 400
    
    cursor = get_db_connection()

    try:
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email, ))

        user = cursor.fetchone()

        if user:
            return jsonify({'error': 'Usuario ya existe'}), 400
        
        pwd_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        cursor.execute('''INSERT INTO usuarios (nombre, email, password) values (%s, %s, %s)''', 
                       (nombre, email, pwd_hash))
        
        cursor.connection.commit()

        return jsonify({"mesaje": "Usuario creado"}), 201
    except Exception as e:
        return jsonify({"error": f"Error al registrar al usuario {str(e)}"}), 500
    finally:
        cursor.close()

@usuarios_bp.route("/login", methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "faltan datos"}), 400
    
    cursor = get_db_connection()

    cursor.execute("SELECT password FROM usuarios WHERE email = %s", (email,))

    usuario = cursor.fetchone()

    if usuario and bcrypt.check_password_hash(usuario[0], password):
        expires = datetime.timedelta(minutes=60)

        access_token = create_access_token(
            identity=str(usuario[1]),
            expires_delta=expires
        )

        cursor.close()

        return jsonify({"token": access_token}), 200
    
    return jsonify({"error": "Credenciales incorrectas"}), 401

@usuarios_bp.route('/datos', methods=['GET'])
@jwt_required()
def datos():
    user = get_jwt_identity()
    cursor = get_db_connection()

    query = "SELECT id_usuario, nombre, email FROM USUARIOS where id_usuarios = %s"

    cursor.execute(query, (user,))
    user = cursor.fetchone()

    cursor.close()

    if user:
        user_info = {
            "id_usuario": user[0],
            "nombre": user[1],
            "email": user[2] 
        }

        return jsonify({"datos": user_info}), 200
    
    return jsonify({"error": "usuario no encontrado"}), 404
