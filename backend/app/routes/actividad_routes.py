from flask import Blueprint, jsonify, session
from app.models.actividad_model import ActividadModel
from app.models.db_structure import Cliente
from datetime import datetime

actividad_bp = Blueprint('actividad_bp', __name__) 

@actividad_bp.route('/api/cliente/mis_actividades', methods=['GET'])
def get_mis_actividades():
    id_usuario = session.get('usuario_id')
    print(f"\n🔍 [RASTREO] ID de Usuario en sesión: {id_usuario}")
    
    if not id_usuario:
        print("❌ [RASTREO] Error: No se encontró usuario_id en la sesión.")
        return jsonify({"error": "Sesión no iniciada"}), 401

    try:
        # Buscamos el CLIENTE que le corresponde a ese usuario
        cliente_actual = Cliente.query.filter_by(id_usuario=id_usuario).first()
        
        if not cliente_actual:
            print(f"⚠️ [RASTREO] Alerta: El usuario ID {id_usuario} se logueó, pero NO existe en la tabla Cliente.")
            return jsonify([]), 200

        print(f"✅ [RASTREO] Cliente encontrado con éxito. ID de Cliente: {cliente_actual.id}")

        # Le pasamos el ID del cliente real a tu modelo
        filas = ActividadModel.get_actividades_por_cliente(cliente_actual.id)
        print(f"📊 [RASTREO] Cantidad de filas devueltas por la base de datos: {len(filas) if filas else 0}")

    except Exception as e:
        print(f"❌ [RASTREO] Error crítico ejecutando la consulta en la DB: {e}")
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
        print(f"🎉 [RASTREO] Envío exitoso al Front de {len(resultado)} eventos.")
        return jsonify(resultado), 200

    except Exception as e:
        print(f"❌ [RASTREO] Error procesando el bucle for de los eventos: {e}")
        return jsonify({"error": "Error al procesar datos"}), 500