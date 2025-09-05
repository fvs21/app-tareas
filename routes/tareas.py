from flask import Blueprint, request, jsonify
from config.db import get_db_connection

tareas_bp=Blueprint("tareas", __name__)

@tareas_bp.route("/obtener", methods=["GET"])
def get():
    return jsonify({"mensaje": "Estas son tus tareas"})

@tareas_bp.route('/crear', methods=["POST"])
def crear():
    data=request.get_json()
    descripcion=data.get("descripcion")
    cursor = get_db_connection()

    try:
        cursor.execute("INSERT INTO tareas (descripcion) values (%s)", (descripcion,))
        cursor.connection.commit()
        return jsonify({"mensaje": "Tarea creada"}, 201)
    except Exception as e:
        return jsonify({"error":f"No se puede crear la tarea: {str(e)}"}), 500
    finally:
        cursor.close()

@tareas_bp.route("/modificar/<int:user_id>", methods=["PUT"])
def modificar(user_id):

    data=request.get_json()
    descripcion=data.get("descripcion")

    return jsonify({"saludo": descripcion})    