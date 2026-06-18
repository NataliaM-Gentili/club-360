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
    """
    Devuelve el historial de pagos del usuario autenticado.
    Solo incluye reservas con estado 'Pago' cuyo turno ya ocurrió (fecha pasada).
    El método de pago se determina así:
      - Tarjeta  → existe registro en AbonoTarjeta
      - Efectivo → abono.efectivo = True  (y sin AbonoTarjeta)
      - Crédito  → crédito usado (activo=False) con id_turno apuntando al turno de la reserva
    """
    user_id = session.get("usuario_id")
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    cliente = Cliente.query.filter_by(id_usuario=user_id).first()
    if not cliente:
        return jsonify({"pagos": []}), 200

    id_cliente = cliente.id_usuario
    hoy = date.today()

    # Reservas del cliente en estado Pago con su abono
    reservas = (
        db.session.query(Reserva, Abono)
        .join(Abono, Abono.id_reserva == Reserva.id)
        .filter(
            Reserva.id_cliente == id_cliente,
            Reserva.estado == "Pago",
        )
        .all()
    )

    # Créditos usados del usuario (activo=False) indexados por id_turno
    creditos_usados = {
        c.id_turno: c
        for c in Credito.query.filter_by(id_usuario=user_id, activo=False).all()
        if c.id_turno is not None
    }

    pagos = []

    for reserva, abono in reservas:
        # ── Turno individual ──────────────────────────────────────────────
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
            if turno:
                # Solo mostrar si el turno ya pasó
                if turno.fecha >= hoy:
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
            # Para reservas mensuales buscamos el turno más reciente pasado de esa clase
            ultimo_turno = (
                Turno.query.filter(
                    Turno.id_clase == reserva_clase.id_clase, Turno.fecha < hoy
                )
                .order_by(Turno.fecha.desc())
                .first()
            )
            if not ultimo_turno:
                continue  # la clase todavía no tuvo ningún turno pasado
            disciplina = clase.disciplina if clase else None
            hora = clase.hora if clase else None
            dia = clase.dia if clase else None
            fecha_turno = None  # mensual: sin fecha única
            id_turno_ref = ultimo_turno.id
            tipo_reserva = "clase"
        else:
            continue  # reserva sin turno ni clase asociada, ignorar

        # ── Método de pago ────────────────────────────────────────────────
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
            # Fallback: efectivo si no se puede determinar otro método
            tipo_pago = "efectivo"
            numero_tarjeta = None

        pagos.append(
            {
                "id_reserva": reserva.id,
                "fecha_reserva": (
                    reserva.fecha.strftime("%d/%m/%Y") if reserva.fecha else None
                ),
                "fecha_turno": fecha_turno,
                "tipo_reserva": tipo_reserva,  # "turno" | "clase"
                "disciplina": disciplina,
                "hora": hora,
                "dia": dia,
                "tipo_pago": tipo_pago,
                "numero_tarjeta": numero_tarjeta,
                "monto": float(abono.monto),
            }
        )

    # Ordenar: turnos individuales por fecha_turno desc; clases van al final
    def sort_key(p):
        if p["fecha_turno"]:
            # Convertir dd/mm/yyyy → yyyymmdd para orden lexicográfico
            d, m, y = p["fecha_turno"].split("/")
            return f"{y}{m}{d}"
        return "00000000"

    pagos.sort(key=sort_key, reverse=True)

    return jsonify({"pagos": pagos}), 200
