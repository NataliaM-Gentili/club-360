from flask import Blueprint, jsonify, session, request
from app.models.turno_model import TurnoModel
from app.models.db_structure import ReservaTurno, Turno, Clase, Reserva, ReservaClase, Abono, Usuario, AbonadoTurnoCancelado
from datetime import date
from app.models.db_structure import ReservaTurno, Turno, Clase, Reserva, ReservaClase, Abono, Usuario
from datetime import date, datetime, time, timedelta, timezone
from app.services.email_services import send_cancellation_email
from app import db

turno_bp = Blueprint("turno_bp", __name__)

@turno_bp.route("/visualizar_turnos", methods=["GET"])
def get_turnos_admin():
    if session.get("rol_id") != 2:
        return (
            jsonify({"error": "Acceso denegado. Se requiere rol de administrador"}),
            403,
        )

    turnos_data = TurnoModel.get_all_turnos_vigentes()

    if not turnos_data:
        return jsonify({"mensaje": "No hay turnos disponibles para mostrar"}), 200

    resultado = []
    for turno, clase, ocupados in turnos_data:
        resultado.append(
            {
                "id_turno": turno.id,
                "actividad": clase.disciplina,
                "dia": clase.dia,
                "horario": clase.hora,
                "cupo_ocupado": ocupados,
                "cupo_total": clase.cupo,
                "fecha_turno": turno.fecha.strftime("%Y-%m-%d"),
                "opciones": ["cancelar turno", "cancelar clase"],
            }
        )

    return jsonify(resultado), 200

# /BUSCAR_TURNOS --> lista turnos del mes corriente filtrados por disciplina, dia y hora
@turno_bp.route("/buscar_turnos", methods=["GET"])
def buscar_turnos():
    disciplina = request.args.get("disciplina")
    dia = request.args.get("dia")
    hora = request.args.get("hora")

    for nombre, valor in {"disciplina": disciplina, "dia": dia, "hora": hora}.items():
        if not valor:
            return jsonify({"error": f"Parámetro faltante: {nombre}"}), 400

    clase = Clase.query.filter_by(
        disciplina=disciplina.lower(), dia=dia, hora=hora
    ).first()

    if not clase:
        return jsonify({"turnos": []}), 200

    hoy = date.today()
    if hoy.month == 12:
        ultimo_dia_mes = date(hoy.year + 1, 1, 1)
    else:
        ultimo_dia_mes = date(hoy.year, hoy.month + 1, 1)

    rol_usuario = session.get("rol_id")
    es_admin_o_empleado = rol_usuario in [2, 3]

    query = Turno.query.filter(
        Turno.id_clase == clase.id,
        Turno.fecha >= hoy,
        Turno.fecha < ultimo_dia_mes,
    )

    if not es_admin_o_empleado:
        query = query.filter(Turno.habilitado == True)

    turnos = query.order_by(Turno.fecha).all()

    resultado = []
    for t in turnos:
        # Sumamos inscriptos individuales
        ocupados_turno = ReservaTurno.query.join(Reserva).filter(
            ReservaTurno.id_turno == t.id, Reserva.estado != 'Cancelada'
        ).count()
        
        # Sumamos inscriptos mensuales
        ocupados_clase = ReservaClase.query.join(Reserva).filter(
            ReservaClase.id_clase == clase.id, Reserva.estado != 'Cancelada'
        ).count()
        
        # Restamos los abonados que cancelaron ESTE turno específico
        cancelados_este_turno = AbonadoTurnoCancelado.query.filter_by(id_turno=t.id).count()
        
        # Ocupación real
        ocupados = (ocupados_clase - cancelados_este_turno) + ocupados_turno
        
        resultado.append(
            {
                "id": t.id,
                "fecha": t.fecha.strftime("%d/%m/%Y"),
                "disciplina": clase.disciplina,
                "dia": clase.dia,
                "hora": clase.hora,
                "cupo": clase.cupo,
                "ocupados": ocupados, # <-- Ahora resta los cancelados
                "id_clase": clase.id,
                "habilitada": clase.habilitada,
                "turno_cancelado": not t.habilitado
            }
        )

    return jsonify({"turnos": resultado}), 200

@turno_bp.route('/turnos_de_cliente', methods=['GET'])
def buscar_turnos_de_cliente():
    id_usuario = request.args.get("id_usuario")

    if not id_usuario:
        return jsonify({"error": "Parámetro faltante: id_usuario"}), 400

    try:
        id_usuario = int(id_usuario)
    except ValueError:
        return jsonify({"error": "id_usuario inválido"}), 400

    reservas = Reserva.query.filter_by(id_cliente=id_usuario).all()

    if not reservas:
        return jsonify({"turnos": []}), 200

    ids_reservas = [r.id for r in reservas]

    reservas_turno = ReservaTurno.query.filter(
        ReservaTurno.id_reserva.in_(ids_reservas)
    ).all()

    resultado = []
    for rt in reservas_turno:
        turno = Turno.query.get(rt.id_turno)
        if not turno:
            continue

        clase = Clase.query.get(turno.id_clase)
        if not clase:
            continue

        resultado.append({
            "id_reserva": rt.id_reserva,
            "id_turno": turno.id,
            "fecha": turno.fecha.strftime("%d/%m/%Y"),
            "disciplina": clase.disciplina,
            "dia": clase.dia,
            "hora": clase.hora,
            "cupo": clase.cupo,
            "habilitado": turno.habilitado,
        })

    return jsonify({"turnos": resultado}), 200
    
# Endpoint para calcular impacto antes de cancelar
@turno_bp.route("/calcular_impacto_clase/<int:id_clase>", methods=["GET"])
def calcular_impacto(id_clase):
    try:
        turnos = Turno.query.filter_by(id_clase=id_clase, habilitado=True).all()
        total_inscriptos = 0
        
        # 1. Contamos a los inscriptos mensuales
        total_mensuales = ReservaClase.query.join(Reserva).filter(
            ReservaClase.id_clase == id_clase, Reserva.estado != 'Cancelada'
        ).count()
        
        # 2. Iteramos por cada turno para restar las excepciones y sumar los sueltos
        for t in turnos:
            sueltos = ReservaTurno.query.join(Reserva).filter(
                ReservaTurno.id_turno == t.id, Reserva.estado != 'Cancelada'
            ).count()
            
            excepciones = AbonadoTurnoCancelado.query.filter_by(id_turno=t.id).count()
            
            # El impacto es la gente que realmente va a ir a ese turno (mensuales - excepciones + sueltos)
            ocupacion_real = (total_mensuales - excepciones) + sueltos
            total_inscriptos += ocupacion_real
            
        return jsonify({"total_inscriptos": total_inscriptos}), 200
    except Exception as e:
        return jsonify({"error": "Falla interna al calcular impacto"}), 500
    
def procesar_cancelacion_turno(turno):
    clase = Clase.query.get(turno.id_clase)
    turno.habilitado = False 
    reservas_turno = ReservaTurno.query.filter_by(id_turno=turno.id).all()
    inscriptos_afectados = 0

    for rt in reservas_turno:
        reserva = Reserva.query.get(rt.id_reserva)
        if reserva and reserva.estado != "Cancelada":
            reserva.estado = "Cancelada"
            inscriptos_afectados += 1
            usuario = Usuario.query.get(reserva.id_cliente)
            abono = Abono.query.filter_by(id_reserva=reserva.id).first()
            monto = float(abono.monto) if abono else 0.0
            
            send_cancellation_email(usuario.email, usuario.nombres, clase.disciplina.capitalize(), 
                                    turno.fecha.strftime("%d/%m/%Y"), clase.hora, monto)
    return inscriptos_afectados

@turno_bp.route("/cancelar_turno", methods=["POST"])
def cancelar_turno_admin():
    datos = request.get_json()
    id_turno = datos.get("id_turno")
    turno = Turno.query.get(id_turno)
    
    if not turno: return jsonify({"error": "Turno no encontrado"}), 404
    
    try:
        procesar_cancelacion_turno(turno)
        db.session.commit()
        return jsonify({"mensaje": "Turno cancelado exitosamente."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Ocurrió un error al intentar cancelar el turno."}), 500
    
@turno_bp.route("/turnos_hoy", methods=["GET"])
def get_turnos_hoy():
    if session.get("rol_id") != 3:
        return jsonify({"error": "Acceso denegado. Se requiere rol de empleado"}), 403

    turnos_data = TurnoModel.get_turnos_de_hoy()

    resultado = []
    for turno, clase in turnos_data:
        resultado.append({
            "id_turno": turno.id,
            "disciplina": clase.disciplina,
            "dia": clase.dia,
            "hora": clase.hora,
            "fecha": turno.fecha.strftime("%d/%m/%Y"),
        })

    return jsonify({"turnos": resultado}), 200

@turno_bp.route("/cancelar_clase", methods=["POST"])
def cancelar_clase_admin():
    datos = request.get_json()
    id_clase = datos.get("id_clase")
    
    if session.get("rol_id") != 2:
        return jsonify({"error": "Acceso denegado"}), 403

    turnos = Turno.query.filter_by(id_clase=id_clase).all()
    
    try:
        for t in turnos:
            procesar_cancelacion_turno(t)
            
        clase = Clase.query.get(id_clase)
        if clase:
            clase.habilitada = False
            
        db.session.commit()
        return jsonify({"mensaje": "Clase cancelada y usuarios notificados"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500