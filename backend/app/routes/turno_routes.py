from flask import Blueprint, jsonify, session
from app.models.turno_model import TurnoModel

turno_bp = Blueprint('turno_bp', __name__)

@turno_bp.route('/visualizar_turnos', methods=['GET'])
def get_turnos_admin():
    if session.get('rol_id') != 2:
        return jsonify({"error": "Acceso denegado. Se requiere rol de administrador"}), 403

    turnos_data = TurnoModel.get_all_turnos_vigentes()

    if not turnos_data:
        return jsonify({"mensaje": "No hay turnos disponibles para mostrar"}), 200

    resultado = []
    for turno, clase, ocupados in turnos_data:
        resultado.append({
            "id_turno": turno.id,
            "actividad": clase.disciplina,
            "dia": clase.dia,
            "horario": clase.hora,
            "cupo_ocupado": ocupados,
            "cupo_total": clase.cupo,
            "fecha_turno": turno.fecha.strftime('%Y-%m-%d'),
            "opciones": ["cancelar turno", "cancelar clase"]
        })

    return jsonify(resultado), 200