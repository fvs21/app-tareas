from flask import Blueprint, request, jsonify
from config.db import get_db_connection
from flask_jwt_extended import jwt_required, get_jwt_identity

tareas_bp=Blueprint("tareas", __name__)

@tareas_bp.route("/obtener", methods=["GET"])
@jwt_required()
def get():
    user = get_jwt_identity()

    cursor = get_db_connection()
    query = '''
        SELECT a.id_usuario, a.descripcion, b.nombre, b.email, a.creado_en
        FROM tareas as a
        INNER JOIN usuarios as b
        ON a.id_usuario=b.id_usuario
        WHERE a.id_usuario=%s
        '''
    
    cursor.execute(query, (user,))
    lista = cursor.fetchall()
    cursor.close()

    if not lista:
        return jsonify({"mensaje": "No tienes tareas"}), 404
    else:
        return jsonify({"tareas": lista}), 200
    
@tareas_bp.route('/crear', methods=["POST"])
@jwt_required()
def crear():
    user = get_jwt_identity()

    data = request.get_json()
    descripcion=data.get("descripcion")

    if not descripcion:
        return jsonify({"error": "Debes agregar una descripcion"}), 400

    cursor = get_db_connection()

    try:
        cursor.execute("INSERT INTO tareas (descripcion, id_usuario) values (%s, %s)", (descripcion, user))
        cursor.connection.commit()
        return jsonify({"mensaje": "Tarea creada"}, 201)
    except Exception as e:
        return jsonify({"error":f"No se puede crear la tarea: {str(e)}"}), 500
    finally:
        cursor.close()

@tareas_bp.route("/modificar/<int:id_tarea>", methods=["PUT"])
@jwt_required()
def modificar(id_tarea):
    user = get_jwt_identity()

    data=request.get_json()
    descripcion=data.get("descripcion")

    cursor=get_db_connection()
    query="SELECT * FROM tareas WHERE id_tarea=%s"
    cursor.execute(query, (id_tarea,))
    tarea=cursor.fetchone()

    if not tarea:
        cursor.close()
        return jsonify({"error": "La tarea no existe"}), 404
    if not tarea[2] == int(user):
        cursor.close()
        return jsonify({"error": "Credenciales invalidas"}), 401
    
    try:
        cursor.execute("UPDATE tareas SET descripcion=%s WHERE id_tarea=%s", (descripcion, id_tarea))
        cursor.connection.commit()
        return jsonify({"mensaje": "Tarea modificada"}), 200
    except Exception as e:
        return jsonify({"error": f"No se puede modificar la tarea: {str(e)}"}), 500
    finally:

        cursor.close()
