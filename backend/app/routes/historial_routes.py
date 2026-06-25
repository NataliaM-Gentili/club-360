from datetime import date
from flask import Blueprint, jsonify, session
from app import db
from app.models.db_structure import (
    Reserva,
    ReservaTurno,
    ReservaClase,
    Abono,
    AbonoTarjeta,
    Tarjeta,
    Turno,
    Clase,
    Credito,
    Cliente,
)

historial_bp = Blueprint("historial", __name__)


@historial_bp.route("/historial-pagos", methods=["GET"])
def historial_pagos():
    user_id = session.get("usuario_id")
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    cliente = Cliente.query.filter_by(id_usuario=user_id).first()
    if not cliente:
        return jsonify({"pagos": []}), 200

    id_cliente = cliente.id_usuario
    hoy = date.today()

    reservas = (
        db.session.query(Reserva, Abono)
        .join(Abono, Abono.id_reserva == Reserva.id)
        .filter(
            Reserva.id_cliente == id_cliente,
            Reserva.estado == "Pago",
        )
        .all()
    )

    creditos_usados = {
        c.id_turno: c
        for c in Credito.query.filter_by(id_usuario=user_id, activo=False).all()
        if c.id_turno is not None
    }

    pagos = []

    for reserva, abono in reservas:
        reserva_turno = ReservaTurno.query.filter_by(id_reserva=reserva.id).first()
        reserva_clase = ReservaClase.query.filter_by(id_reserva=reserva.id).first()

        disciplina = None
        hora = None
        dia = None
        fecha_turno = None
        id_turno_ref = None
        tipo_reserva = None

        if reserva_turno:
            turno = Turno.query.get(reserva_turno.id_turno)
            if not turno:
                continue

            clase = Clase.query.get(turno.id_clase)
            disciplina = clase.disciplina if clase else None
            hora = clase.hora if clase else None
            dia = clase.dia if clase else None
            fecha_turno = turno.fecha.strftime("%d/%m/%Y")
            id_turno_ref = turno.id
            tipo_reserva = "turno"

        elif reserva_clase:
            clase = Clase.query.get(reserva_clase.id_clase)
            if not clase:
                continue

            ultimo_turno = (
                Turno.query.filter(
                    Turno.id_clase == reserva_clase.id_clase, Turno.fecha < hoy
                )
                .order_by(Turno.fecha.desc())
                .first()
            )

            disciplina = clase.disciplina
            hora = clase.hora
            dia = clase.dia
            fecha_turno = None
            id_turno_ref = ultimo_turno.id if ultimo_turno else None
            tipo_reserva = "clase"
        else:
            continue

        # Método de pago: crédito tiene prioridad sobre efectivo
        if float(abono.monto) == 0:
            tipo_pago = "credito"
            numero_tarjeta = None
        else:
            abono_tarjeta = AbonoTarjeta.query.filter_by(id_abono=reserva.id).first()

            if abono_tarjeta:
                tipo_pago = "tarjeta"
                tarjeta = Tarjeta.query.get(abono_tarjeta.id_tarjeta)
                numero_tarjeta = tarjeta.numero[-4:] if tarjeta else None
            elif abono.efectivo:
                tipo_pago = "efectivo"
                numero_tarjeta = None
            elif id_turno_ref and id_turno_ref in creditos_usados:
                tipo_pago = "credito"
                numero_tarjeta = None
            else:
                tipo_pago = "efectivo"
                numero_tarjeta = None

        pagos.append(
            {
                "id_reserva": reserva.id,
                "fecha_reserva": (
                    reserva.fecha.strftime("%d/%m/%Y") if reserva.fecha else None
                ),
                "fecha_turno": fecha_turno,
                "tipo_reserva": tipo_reserva,
                "disciplina": disciplina,
                "hora": hora,
                "dia": dia,
                "tipo_pago": tipo_pago,
                "numero_tarjeta": numero_tarjeta,
                "monto": float(abono.monto),
            }
        )

    def sort_key(p):
        if p["fecha_turno"]:
            d, m, y = p["fecha_turno"].split("/")
            return f"{y}{m}{d}"
        return "99999999"

    pagos.sort(key=sort_key, reverse=True)

    return jsonify({"pagos": pagos}), 200
