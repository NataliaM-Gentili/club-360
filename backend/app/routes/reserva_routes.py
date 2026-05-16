from flask import Blueprint, request, jsonify, session
from app import db

from app.models.reserva_model import ReservaModel
from app.models.db_structure import EmpleadoRegistraAbono


reserva_bp = Blueprint('reserva_bp', __name__)


@reserva_bp.route('/registrar_pago_efectivo', methods=['POST'])
def registrar_pago_efectivo():

    # verifico de rol
    if session.get('rol_id') != 3:
        return jsonify({
            "mensaje": "Acceso denegado. Se requiere rol de empleado"
        }), 403

    datos = request.get_json()

    id_reserva = datos.get('id_reserva')
    monto_ingresado = datos.get('monto') # el input del empleado

    reserva = ReservaModel.obtener_reserva(id_reserva)

    if not reserva:
        return jsonify({
            "mensaje": "Reserva no encontrada"
        }), 404

    # reserva ya abonada
    if reserva.estado != "Pendiente":
        return jsonify({
            "mensaje": "La reserva ya fue abonada"
        }), 400

    abono = ReservaModel.obtener_abono(id_reserva)

    if not abono:
        return jsonify({
            "mensaje": "Abono no encontrado"
        }), 404

    # monto insuficiente
    if monto_ingresado < float(abono.monto):
        return jsonify({
            "mensaje": "El monto ingresado es insuficiente"
        }), 400

    # monto excedente
    if monto_ingresado > float(abono.monto):
        return jsonify({
            "mensaje": "El monto ingresado excede el monto pendiente"
        }), 400


    abono.efectivo = True
    reserva.estado = "Pago"

    registro_empleado = EmpleadoRegistraAbono(
        id_empleado=session.get('usuario_id'),
        id_abono=abono.id_reserva
    )

    db.session.add(registro_empleado)

    db.session.commit()

    return jsonify({
        "mensaje": "El pago ha sido registrado correctamente"
    }), 200