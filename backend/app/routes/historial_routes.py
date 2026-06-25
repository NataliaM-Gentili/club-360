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
    Cliente,
)
 
historial_bp = Blueprint("historial-pagos", __name__)
 
 
@historial_bp.route("/historial-pagos", methods=["GET"])
def historial_pagos():
    """
    Devuelve el historial de pagos del usuario autenticado (reservas en
    estado "Pago").
      - Turno individual: informa la fecha del turno, disciplina, horario y monto.
      - Clase (abono mensual): se paga en una sola cuota; se informa día,
        horario, disciplina y monto total abonado (sin fecha única).
    Método de pago:
      - Tarjeta  -> existe registro en AbonoTarjeta (se muestran los 4 últimos dígitos)
      - Efectivo -> cualquier otro caso (abono.efectivo o sin registro de tarjeta)
    """
    user_id = session.get("usuario_id")
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401
 
    cliente = Cliente.query.filter_by(id_usuario=user_id).first()
    if not cliente:
        return jsonify({"pagos": []}), 200
 
    id_cliente = cliente.id_usuario
 
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
    pagos = []
 
    for reserva, abono in reservas:
        reserva_turno = ReservaTurno.query.filter_by(id_reserva=reserva.id).first()
        reserva_clase = ReservaClase.query.filter_by(id_reserva=reserva.id).first()
 
        disciplina = None
        hora = None
        dia = None
        fecha_turno = None
        tipo_reserva = None

        # ── Turno individual ──────────────────────────────────────────────
        if reserva_turno:
            turno = Turno.query.get(reserva_turno.id_turno)
            if not turno:
                continue
            
            clase = Clase.query.get(turno.id_clase)
            disciplina = clase.disciplina if clase else None
            hora = clase.hora if clase else None
            dia = clase.dia if clase else None
            fecha_turno = turno.fecha.strftime("%d/%m/%Y")
            tipo_reserva = "Turno"
 
        # ── Clase (abono mensual) ─────────────────────────────────────────
        elif reserva_clase:
            clase = Clase.query.get(reserva_clase.id_clase)
            if not clase:
                continue
 
            disciplina = clase.disciplina
            hora = clase.hora
            dia = clase.dia
            fecha_turno = None  # mensual: sin fecha única
            tipo_reserva = "Clase"
        else:
            continue  # reserva sin turno ni clase asociada, ignorar
 
        # ── Método de pago ────────────────────────────────────────────────
        if float(abono.monto) == 0:
            tipo_pago = "credito"
            numero_tarjeta = None
        else:
            abono_tarjeta = AbonoTarjeta.query.filter_by(id_abono=reserva.id).first()
            if abono_tarjeta:
                tipo_pago = "tarjeta"
                tarjeta = Tarjeta.query.get(abono_tarjeta.id_tarjeta)
                numero_tarjeta = tarjeta.numero[-4:] if tarjeta else None
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
                "tipo_reserva": tipo_reserva,  # "turno" | "clase"
                "disciplina": disciplina,
                "hora": hora,
                "dia": dia,
                "tipo_pago": tipo_pago,
                "numero_tarjeta": numero_tarjeta,
                "monto": float(abono.monto),
            }
        )
 
    # Ordenar: turnos por fecha desc; clases (sin fecha única) primero.
    def sort_key(p):
        if p["fecha_turno"]:
            d, m, y = p["fecha_turno"].split("/")
            return f"{y}{m}{d}"
        return "99999999"
 
    pagos.sort(key=sort_key, reverse=True)
 
    return jsonify({"pagos": pagos}), 200
