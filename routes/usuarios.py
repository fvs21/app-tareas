from flask import Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt
from flask_bcrypt import Bcrypt

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
        
        cursor.connection.commit

        return jsonify({"mesaje": "Usuario creado"}), 201
    except Exception as e:
        return jsonify({"error": f"Error al registrar al usuario {str(e)}"}), 500
    finally:
        cursor.close()