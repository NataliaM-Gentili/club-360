from datetime import datetime

from app.models.reserva_model import ReservaModel
from flask import Blueprint, request, jsonify, session
from app import db
from app.models.tarjeta_model import TarjetaModel
from app.models.db_structure import ReservaTurno, Turno, Clase, Tarjeta
from app.models.db_structure import AbonoTarjeta

tarjeta_bp = Blueprint("tarjeta", __name__)


@tarjeta_bp.route("/registrar-tarjeta", methods=["POST"])
def registrar_tarjeta():
    data = request.get_json()

    # Extraemos el id_cliente (asegúrate de enviarlo en el JSON) --> lo recupero de las cookies
    # id = data.get("id")
    id = session.get("usuario_id")

    # if not id or "numero" not in data:
    #    return jsonify({"error": "Faltan datos obligatorios"}), 400

    if not id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    required_fields = ["numero", "fecha_vencimiento", "cvv", "titular"]

    missing = [f for f in required_fields if f not in data]

    if missing:
        return (
            jsonify({"error": "Faltan datos obligatorios", "missing_fields": missing}),
            400,
        )

    fecha_venc = datetime.strptime(data["fecha_vencimiento"], "%Y-%m")
    if fecha_venc.replace(day=1) < datetime.today().replace(day=1):
        return jsonify({"error": "La tarjeta está vencida"}), 400

    try:
        resultado = TarjetaModel.registrar_tarjeta_a_cliente(id, data)

        if resultado["status"] == "exists":
            return jsonify({"mensaje": resultado["mensaje"]}), 409

        return jsonify({"mensaje": resultado["mensaje"]}), 201

    except Exception as e:
        from app import db

        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@tarjeta_bp.route("/tarjetas/<int:id_cliente>", methods=["GET"])
def obtener_tarjetas(id_cliente):
    tarjetas = TarjetaModel.obtener_tarjetas_usuario(id_cliente)
    return (
        jsonify(
            [
                {
                    "id": t.id,
                    "numero": t.numero[-4:],
                    "titular": t.titular,
                    "fecha_vencimiento": t.fecha_vencimiento,
                }
                for t in tarjetas
            ]
        ),
        200,
    )


@tarjeta_bp.route("/pago_tarjeta", methods=["POST"])
def pago_tarjeta():
    """
    Maneja dos flujos:
    1. Standalone booking (50% deposit): Primer pago mantiene Pendiente, segundo pago completa a Pago
    2. Monthly booking (full amount): Un solo pago, completa a Pago
    """
    data = request.get_json()

    id_reserva = data.get("id_reserva")
    reserva = ReservaModel.obtener_reserva(id_reserva)

    if not reserva:
        return jsonify({"mensaje": "Reserva no encontrada"}), 404

    # reserva ya abonada
    if reserva.estado != "Pendiente":
        return jsonify({"mensaje": "La reserva ya fue abonada"}), 400

    abono = TarjetaModel.obtener_abono(id_reserva)
    if not abono:
        return jsonify({"mensaje": "Abono no encontrado"}), 404

    id_tarjeta = data.get("id_tarjeta")

    # Verificar que la tarjeta no esté vencida
    tarjeta = Tarjeta.query.get(id_tarjeta)
    if not tarjeta:
        return jsonify({"error": "Tarjeta no encontrada"}), 404

    fecha_venc = datetime.strptime(tarjeta.fecha_vencimiento, "%Y-%m")
    if fecha_venc.replace(day=1) < datetime.today().replace(day=1):
        return jsonify({"error": "La tarjeta está vencida"}), 404

    # retorna el ID del usuario
    user_id = TarjetaModel.obtener_usuario_con_reserva(id_reserva)
    if user_id == 4:
        return jsonify({"mensaje": "Saldo insuficiente!"}), 200

    abono.efectivo = False

    # Determinar si es standalone (ReservaTurno) o monthly (ReservaClase)
    from app.models.db_structure import ReservaClase

    is_standalone = (
        ReservaTurno.query.filter_by(id_reserva=id_reserva).first() is not None
    )
    is_monthly = ReservaClase.query.filter_by(id_reserva=id_reserva).first() is not None

    # Verificar si ya existe un pago previo (AbonoTarjeta)
    existing_payment = AbonoTarjeta.query.filter_by(id_abono=id_reserva).first()

    if is_standalone and existing_payment:
        # STANDALONE - Segundo pago (50% restante): Actualizar a 100% y completar
        abono.monto = abono.monto * 2  # 50% * 2 = 100%
        reserva.estado = "Pago"
    elif is_standalone and not existing_payment:
        # STANDALONE - Primer pago (50% seña): Crear registro de pago, mantener Pendiente
        TarjetaModel.registrar_abono_tarjeta(id_reserva, id_tarjeta)
    else:
        # MONTHLY - Primer y único pago (monto completo): Completar a Pago
        reserva.estado = "Pago"
        TarjetaModel.registrar_abono_tarjeta(id_reserva, id_tarjeta)

    db.session.commit()
    return jsonify({"mensaje": f"Pago realizado con exito!"}), 200

# --- RUTA PARA OBTENER LOS DATOS COMPLETOS DE UNA SOLA TARJETA ---
@tarjeta_bp.route("/tarjeta/<int:id_tarjeta>", methods=["GET"])
def obtener_tarjeta_individual(id_tarjeta):
    id_cliente = session.get("usuario_id")
    if not id_cliente:
        return jsonify({"error": "Usuario no autenticado"}), 401
    
    # Validar que le pertenezca al usuario
    from app.models.db_structure import ClienteTarjeta
    relacion = ClienteTarjeta.query.filter_by(id_cliente=id_cliente, id_tarjeta=id_tarjeta).first()
    if not relacion:
        return jsonify({"error": "No autorizado"}), 403
        
    t = Tarjeta.query.get(id_tarjeta)
    return jsonify({
        "numero": t.numero,
        "titular": t.titular,
        "fecha_vencimiento": t.fecha_vencimiento,
        "cvv": t.cvv
    }), 200

# --- RUTA PARA APLICAR LA EDICIÓN ---
@tarjeta_bp.route("/editar-tarjeta/<int:id_tarjeta>", methods=["PUT"])
def editar_tarjeta_route(id_tarjeta):
    data = request.get_json()
    id_cliente = session.get("usuario_id")

    if not id_cliente:
        return jsonify({"error": "Usuario no autenticado"}), 401

    required_fields = ["numero", "fecha_vencimiento", "cvv", "titular"]
    missing = [f for f in required_fields if f not in data]

    if missing:
        return jsonify({"error": "Faltan datos obligatorios", "missing_fields": missing}), 400

    fecha_venc = datetime.strptime(data["fecha_vencimiento"], "%Y-%m")
    if fecha_venc.replace(day=1) < datetime.today().replace(day=1):
        return jsonify({"error": "La tarjeta está vencida"}), 400

    try:
        resultado = TarjetaModel.editar_tarjeta(id_tarjeta, id_cliente, data)

        if "error" in resultado:
            return jsonify({"error": resultado["error"]}), 403

        return jsonify({"mensaje": resultado["mensaje"]}), 200

    except Exception as e:
        from app import db
        db.session.rollback()
        return jsonify({"error": str(e)}), 500