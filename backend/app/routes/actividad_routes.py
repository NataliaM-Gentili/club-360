from app import db
from flask import Blueprint, jsonify, session
from app.models.actividad_model import ActividadModel
from app.models.db_structure import Cliente
from datetime import datetime

actividad_bp = Blueprint('actividad_bp', __name__) 

@actividad_bp.route('/cliente/mis_actividades', methods=['GET'])
def get_mis_actividades():
    id_usuario = session.get('usuario_id')
    
    if not id_usuario:
        return jsonify({"error": "Sesión no iniciada"}), 401

    try:
        cliente_actual = Cliente.query.filter_by(id_usuario=id_usuario).first()
        filas = ActividadModel.get_actividades(cliente_actual.id_usuario)

    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500

    resultado = []
    hoy = datetime.now().date()

    try:
        for reserva, turno, clase, asistencia in filas:
            if not turno.habilitado:
                estado = "cancelada por club"
            elif reserva.estado == "Cancelada":
                estado = "cancelada por cliente"
            elif asistencia is not None or turno.fecha < hoy:
                estado = "asistida"
            else:
                estado = "confirmada"

            resultado.append({
                "title": clase.disciplina,
                "start": turno.fecha.strftime('%Y-%m-%d'),
                "extendedProps": {
                    "estado": estado,
                    "hora": clase.hora,
                    "id_reserva": reserva.id
                }
            })
        return jsonify(resultado), 200

    except Exception as e:
        print(f"[actividad_routes] Error: {e}")
        return jsonify({"error": "Error al procesar datos"}), 500