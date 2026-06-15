from flask import Blueprint, jsonify, session, request
from app.models.turno_model import TurnoModel
from app.models.db_structure import ReservaTurno, Turno, Clase, Reserva, ReservaClase, Abono, Usuario
from datetime import date
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
    #EN CASO DE QUERER FILTRAR TODO EL MES -> primer_dia_mes = date(hoy.year, hoy.month, 1)
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

    # si es cleinte,filtro para ocultar los deshabilitados
    if not es_admin_o_empleado:
        query = query.filter(Turno.habilitado == True)

    turnos = query.order_by(Turno.fecha).all()

    resultado = []
    for t in turnos:
        ocupados_turno = ReservaTurno.query.filter_by(id_turno=t.id).count()
        ocupados_clase = ReservaClase.query.filter_by(id_clase=clase.id).count()
        ocupados = ocupados_turno + ocupados_clase
        resultado.append(
            {
                "id": t.id,
                "fecha": t.fecha.strftime("%d/%m/%Y"),
                "disciplina": clase.disciplina,
                "dia": clase.dia,
                "hora": clase.hora,
                "cupo": clase.cupo,
                "ocupados": ocupados,
                "id_clase": clase.id,
                "habilitada": clase.habilitada,
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

    # 1. Buscar todas las reservas del cliente
    reservas = Reserva.query.filter_by(id_cliente=id_usuario).all()


    if not reservas:
        return jsonify({"turnos": []}), 200

    ids_reservas = [r.id for r in reservas]

    # 2. Buscar los ReservaTurno asociados a esas reservas
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

@turno_bp.route("/cancelar_turno", methods=["POST"])
def cancelar_turno_admin():
    datos = request.get_json()

    if not datos or "id_turno" not in datos:
        return jsonify({"error": "No se recibió el id_turno en la petición"}), 400
    
    id_turno = datos.get("id_turno")
    # 1. Validar que sea administrador (Rol 2)
    if session.get("rol_id") != 2:
        return jsonify({"error": "Acceso denegado. Se requiere rol de administrador"}), 403

    turno = Turno.query.get(id_turno)
    if not turno:
        return jsonify({"error": "Turno no encontrado"}), 404

    clase = Clase.query.get(turno.id_clase)

    # 2. Cambiar el estado del turno (lo saca de la cartelera)
    turno.habilitado = False 

    # 3. Buscar si hay inscriptos
    reservas_turno = ReservaTurno.query.filter_by(id_turno=id_turno).all()
    inscriptos_afectados = 0

    for rt in reservas_turno:
        reserva = Reserva.query.get(rt.id_reserva)
        
        if reserva and reserva.estado != "Cancelada":
            reserva.estado = "Cancelada"
            inscriptos_afectados += 1
            
            # Buscar datos del cliente y el monto
            usuario = Usuario.query.get(reserva.id_cliente)
            abono = Abono.query.filter_by(id_reserva=reserva.id).first()
            monto_a_devolver = float(abono.monto) if abono else 0.0

            # Disparar el correo electrónico con tu servicio centralizado
            send_cancellation_email(
                email_destino=usuario.email,
                nombre=usuario.nombres,
                disciplina=clase.disciplina.capitalize(),
                fecha=turno.fecha.strftime("%d/%m/%Y"),
                hora=clase.hora,
                monto=monto_a_devolver
            )

    try:
        db.session.commit()
        
        mensaje = "Turno cancelado exitosamente."
        if inscriptos_afectados > 0:
            mensaje += f" Se notificó a {inscriptos_afectados} inscripto(s) sobre la devolución."
        else:
            mensaje += " El turno no tenía inscriptos."
            
        return jsonify({"mensaje": mensaje}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Ocurrió un error al intentar cancelar el turno."}), 500
    
    
# /TURNOS_HOY --> lista los turnos de hoy para que el empleado pueda pasar asistencia manual
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
