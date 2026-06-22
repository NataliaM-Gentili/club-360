from app import db
from flask import Blueprint, jsonify, session
from app.models.actividad_model import ActividadModel
from app.models.db_structure import Clase, Cliente, Reserva, ReservaClase, ReservaTurno, Turno, OfrecimientoReserva 
from datetime import date, datetime  


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
 
@actividad_bp.route('/cliente/mis_turnos_pendientes', methods=['GET'])
def mis_turnos_pendientes():
    id_cliente = session.get('usuario_id')
    if not id_cliente:
        return jsonify({"mensaje": "No autenticado"}), 401
    if session.get('rol_id') != 1:
        return jsonify({"mensaje": "Acceso denegado"}), 403

    hoy = date.today()
    if hoy.month == 12:
        primer_dia_sig = date(hoy.year + 1, 1, 1)
    else:
        primer_dia_sig = date(hoy.year, hoy.month + 1, 1)

    resultado = []

    # ---------- SUELTOS ----------
    filas = (
        db.session.query(ReservaTurno, Turno, Clase)
        .join(Reserva, ReservaTurno.id_reserva == Reserva.id)
        .join(Turno, ReservaTurno.id_turno == Turno.id)
        .join(Clase, Turno.id_clase == Clase.id)
        .filter(
            Reserva.id_cliente == id_cliente,
            Reserva.estado != 'Cancelada',
            Turno.habilitado == True,
            Turno.fecha >= hoy,
        )
        .order_by(Turno.fecha)
        .all()
    )
    for rt, turno, clase in filas:
        resultado.append({
            "id_reserva": rt.id_reserva,
            "id_turno": turno.id,
            "disciplina": clase.disciplina,
            "fecha": turno.fecha.strftime("%d/%m/%Y"),
            "hora": clase.hora,
            "tipo": "suelto",
        })

    # ---------- ABONOS ----------
    # El abono no materializa ReservaTurno -> derivamos los turnos del mes de la clase.
    # Los ya cancelados quedan registrados en OfrecimientoReserva.cliente_emisor.
    cancelados = (
        db.session.query(ReservaTurno.id_turno)
        .join(OfrecimientoReserva, OfrecimientoReserva.id_reserva == ReservaTurno.id_reserva)
        .filter(OfrecimientoReserva.cliente_emisor == id_cliente)
        .all()
    )
    ids_cancelados = {row.id_turno for row in cancelados}

    abonos = (
        db.session.query(ReservaClase, Clase)
        .join(Reserva, ReservaClase.id_reserva == Reserva.id)
        .join(Clase, ReservaClase.id_clase == Clase.id)
        .filter(
            Reserva.id_cliente == id_cliente,
            Reserva.estado != 'Cancelada',
        )
        .all()
    )
    for rc, clase in abonos:
        turnos = (
            Turno.query.filter(
                Turno.id_clase == rc.id_clase,
                Turno.habilitado == True,
                Turno.fecha >= hoy,
                Turno.fecha < primer_dia_sig,
            )
            .order_by(Turno.fecha)
            .all()
        )
        for turno in turnos:
            if turno.id in ids_cancelados:
                continue
            resultado.append({
                "id_reserva": rc.id_reserva,
                "id_turno": turno.id,
                "disciplina": clase.disciplina,
                "fecha": turno.fecha.strftime("%d/%m/%Y"),
                "hora": clase.hora,
                "tipo": "abono",
            })

    return jsonify(resultado), 200