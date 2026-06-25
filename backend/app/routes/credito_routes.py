from flask import Blueprint, jsonify, session, request
from datetime import datetime, timedelta
from app import db
from app.models.credito_model import CreditoModel
from app.models.db_structure import (
    Credito, Clase, Turno, Reserva, ReservaTurno, ReservaClase,
    Abono, ClienteSuspendido
)
from app.services.email_services import enviar_comprobante_qr_turno

credito_bp = Blueprint("credito_bp", __name__)


@credito_bp.route("/creditos", methods=["GET"])
def get_creditos():
    id_usuario = session.get("usuario_id")
    if not id_usuario:
        return jsonify({"error": "No autenticado"}), 401
    if session.get("rol_id") != 1:
        return jsonify({"error": "Acceso denegado"}), 403

    creditos = CreditoModel.get_creditos_activos_by_usuario(id_usuario)
    return jsonify({"creditos": creditos}), 200


@credito_bp.route("/turnos_credito/<disciplina>", methods=["GET"])
def listar_turnos_credito(disciplina):
    id_usuario = session.get("usuario_id")
    if not id_usuario:
        return jsonify({"error": "No autenticado"}), 401
    if session.get("rol_id") != 1:
        return jsonify({"error": "Acceso denegado"}), 403

    ahora = datetime.now()
    hoy = ahora.date()
    hora_limite = (ahora + timedelta(hours=1)).time()

    clases = Clase.query.filter_by(disciplina=disciplina.lower(), habilitada=True).all()
    if not clases:
        return jsonify({"turnos": []}), 200

    resultado = []
    for clase in clases:
        turnos = Turno.query.filter(
            Turno.id_clase == clase.id,
            Turno.habilitado == True,
            Turno.fecha >= hoy,
        ).order_by(Turno.fecha).all()

        hora_clase = datetime.strptime(clase.hora, "%H:%M").time()

        for t in turnos:
            if t.fecha == hoy and hora_clase <= hora_limite:
                continue

            ocupados_turno = ReservaTurno.query.join(Reserva).filter(
                ReservaTurno.id_turno == t.id, Reserva.estado != 'Cancelada'
            ).count()
            ocupados_clase = ReservaClase.query.join(Reserva).filter(
                ReservaClase.id_clase == clase.id, Reserva.estado != 'Cancelada'
            ).count()
            ocupados = ocupados_turno + ocupados_clase

            resultado.append({
                "id_turno": t.id,
                "fecha": t.fecha.strftime("%d/%m/%Y"),
                "dia": clase.dia,
                "hora": clase.hora,
                "cupo": clase.cupo,
                "ocupados": ocupados,
                "disponibles": clase.cupo - ocupados,
                "_sort_fecha": t.fecha.isoformat(),
            })

    resultado.sort(key=lambda x: (x["_sort_fecha"], x["hora"]))
    for r in resultado:
        del r["_sort_fecha"]

    return jsonify({"turnos": resultado}), 200


@credito_bp.route("/reservar_turno_credito", methods=["POST"])
def reservar_turno_credito():
    id_cliente = session.get("usuario_id")
    if not id_cliente:
        return jsonify({"mensaje": "No autenticado"}), 401
    if session.get("rol_id") != 1:
        return jsonify({"mensaje": "Acceso denegado"}), 403

    datos = request.get_json()
    id_turno = datos.get("id_turno")
    disciplina = datos.get("disciplina")

    if not id_turno or not disciplina:
        return jsonify({"mensaje": "Faltan datos"}), 400

    credito = Credito.query.filter_by(
        id_usuario=id_cliente, disciplina=disciplina.lower(), activo=True
    ).first()
    if not credito:
        return jsonify({"mensaje": "No posee créditos disponibles para esta disciplina"}), 400

    turno = Turno.query.get(id_turno)
    if not turno or not turno.habilitado:
        return jsonify({"mensaje": "El turno no está disponible"}), 404

    clase = Clase.query.get(turno.id_clase)
    if not clase or clase.disciplina != disciplina.lower():
        return jsonify({"mensaje": "La disciplina del crédito no coincide con el turno"}), 400

    suspendido = ClienteSuspendido.query.filter(
        ClienteSuspendido.id_cliente == id_cliente,
        ClienteSuspendido.id_turno != None,
        ).first()

    if suspendido:
        return jsonify({"mensaje": "No se ha podido realizar la reserva, usted se encuentra suspendido"}), 400

    ocupados_turno = ReservaTurno.query.join(Reserva).filter(
        ReservaTurno.id_turno == id_turno, Reserva.estado != 'Cancelada'
    ).count()
    ocupados_clase = ReservaClase.query.join(Reserva).filter(
        ReservaClase.id_clase == clase.id, Reserva.estado != 'Cancelada'
    ).count()
    if (ocupados_turno + ocupados_clase) >= clase.cupo:
        return jsonify({"mensaje": "El cupo de este turno ya está lleno"}), 400

    ya_inscripto = ReservaTurno.query.join(Reserva).filter(
        ReservaTurno.id_turno == id_turno,
        Reserva.id_cliente == id_cliente,
        Reserva.estado != "Cancelada",
    ).first()
    if ya_inscripto:
        return jsonify({"mensaje": "Ya se encuentra inscripto en este turno"}), 400

    reserva = Reserva(id_cliente=id_cliente, estado="Pago")
    db.session.add(reserva)
    db.session.flush()

    db.session.add(ReservaTurno(id_reserva=reserva.id, id_turno=id_turno))
    db.session.add(Abono(id_reserva=reserva.id, monto=0, efectivo=True))

    credito.activo = False
    credito.id_turno = id_turno

    db.session.commit()

    enviar_comprobante_qr_turno(
        id_cliente=id_cliente,
        id_reserva=reserva.id,
        id_turno=turno.id,
        disciplina=clase.disciplina,
        fecha=turno.fecha.strftime("%d/%m/%Y"),
        hora=clase.hora,
    )

    return jsonify({"mensaje": "Pago realizado con éxito"}), 201
