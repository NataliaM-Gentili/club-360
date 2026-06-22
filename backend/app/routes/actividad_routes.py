from flask import Blueprint, jsonify, session, request
from app.models.actividad_model import ActividadModel
from app.models.db_structure import Cliente, Reserva, ReservaClase, AbonadoTurnoCancelado
from datetime import datetime
from app import db

# NUEVO: Importamos la función directamente en vez de usar requests. 
# (Verificá que la ruta del import coincida con la carpeta de tu proyecto)
from app.routes.lista_espera_routes import ofrecimiento_turno

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
            
            # Verificamos si este abonado canceló este turno específico
            elif AbonadoTurnoCancelado.query.filter_by(id_cliente=id_usuario, id_turno=turno.id).first() is not None:
                estado = "cancelada por cliente"
            else:
                estado = "confirmada"

            resultado.append({
                "title": clase.disciplina,
                "start": turno.fecha.strftime('%Y-%m-%d'),
                "extendedProps": {
                    "estado": estado,
                    "hora": clase.hora,
                    "id_reserva": reserva.id,
                    "id_turno": turno.id # Usado al cancelar
                }
            })
        return jsonify(resultado), 200

    except Exception as e:
        print(f"[actividad_routes] Error: {e}")
        return jsonify({"error": "Error al procesar datos"}), 500

# Endpoint para procesar la cancelación que viene de React
@actividad_bp.route('/cliente/cancelar_actividad', methods=['POST'])
def cancelar_actividad():
    id_usuario = session.get('usuario_id')
    if not id_usuario:
        return jsonify({"error": "Sesión no iniciada"}), 401

    datos = request.get_json()
    id_reserva = datos.get('id_reserva')
    id_turno = datos.get('id_turno')

    if not id_reserva or not id_turno:
        return jsonify({"error": "Datos incompletos"}), 400

    try:
        reserva = Reserva.query.get(id_reserva)
        if not reserva or reserva.id_cliente != id_usuario:
            return jsonify({"error": "Reserva no válida"}), 404

        # Verificamos si la reserva es mensual
        es_mensual = ReservaClase.query.filter_by(id_reserva=id_reserva).first() is not None

        if es_mensual:
            # 1. Registramos que no va este día (liberamos el cupo físicamente)
            excepcion = AbonadoTurnoCancelado(id_cliente=id_usuario, id_turno=id_turno)
            db.session.add(excepcion)
            db.session.commit()
            
            # 2. LÓGICA DE LISTA DE ESPERA
            # Llamamos a la función de forma directa en Python
            try:
                ofrecimiento_turno(cliente_emisor=id_usuario, id_reserva=id_reserva, id_turno=id_turno)
            except Exception as ex_espera:
                print("No se pudo procesar la lista de espera:", ex_espera)

            return jsonify({"mensaje": "Turno cancelado exitosamente. Se ha liberado su cupo para este día."}), 200
            
        else:
            # Si era turno suelto, cancelamos la reserva entera 
            reserva.estado = "Cancelada"
            db.session.commit()
            
            # 2. LÓGICA DE LISTA DE ESPERA
            try:
                ofrecimiento_turno(cliente_emisor=id_usuario, id_reserva=id_reserva, id_turno=id_turno)
            except Exception as ex_espera:
                print("No se pudo procesar la lista de espera:", ex_espera)

            return jsonify({"mensaje": "Reserva cancelada exitosamente."}), 200

    except Exception as e:
        db.session.rollback()
        print("Error en cancelar_actividad:", e)
        return jsonify({"error": "Ocurrió un error al procesar la cancelación."}), 500