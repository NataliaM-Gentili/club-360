from flask import Blueprint, request, jsonify, session
from app import db

from app.models.reserva_model import ReservaModel
from app.models.db_structure import EmpleadoRegistraAbono

from app.models.db_structure import Usuario, Cliente
from app.models.db_structure import Reserva, ReservaTurno
from app.models.db_structure import Turno, Clase
from app.models.db_structure import Abono

from sqlalchemy import exists
from app.models.db_structure import ReservaClase

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


# dado email de cliente, deporte, fecha y hora revisa si existe un turno reservado
# se usa para la página de registrar pago en efectivo
@reserva_bp.route('/revisar-reserva', methods=['POST'])
def revisar_reserva():

    datos = request.get_json()
    email = datos.get('email')

    if not email:
        return jsonify({"mensaje": "Email requerido"}), 400

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404

    cliente = Cliente.query.filter_by(id_usuario=usuario.id).first()
    if not cliente:
        return jsonify({"mensaje": "El usuario no es cliente"}), 404

    result = []

    # -------------------------
    # 🔹 TURNOS
    # -------------------------
    reservas_turno = (
        db.session.query(Reserva, Abono, Turno, Clase)
        .join(ReservaTurno, ReservaTurno.id_reserva == Reserva.id)
        .join(Turno, Turno.id == ReservaTurno.id_turno)
        .join(Clase, Clase.id == Turno.id_clase)
        .outerjoin(Abono, Abono.id_reserva == Reserva.id)
        .filter(
            Reserva.id_cliente == cliente.id_usuario,
            Reserva.estado == "Pendiente",

            # EXCLUDE monthly reservations
            ~exists().where(ReservaClase.id_reserva == Reserva.id)
        )
        .all()
    )

    for reserva, abono, turno, clase in reservas_turno:
        result.append({
            "id_reserva": reserva.id,
            "tipo": "turno",
            "disciplina": clase.disciplina,
            "fecha": str(turno.fecha),
            "hora": clase.hora,
            "monto_deuda": float(abono.monto),
        })

    # -------------------------
    # 🔹 CLASES (mensuales)
    # -------------------------

    reservas_clase = (
        db.session.query(Reserva, Abono, Clase)
        .join(ReservaClase, ReservaClase.id_reserva == Reserva.id)
        .join(Clase, Clase.id == ReservaClase.id_clase)
        .outerjoin(Abono, Abono.id_reserva == Reserva.id)
        .filter(
            Reserva.id_cliente == cliente.id_usuario,
            Reserva.estado == "Pendiente"
        )
        .all()
    )

    for reserva, abono, clase in reservas_clase:
        result.append({
            "id_reserva": reserva.id,
            "tipo": "clase",
            "disciplina": clase.disciplina,
            "fecha": "Mensual",
            "hora": "-",
            "monto_deuda": float(abono.monto),
        })

    if not result:
        return jsonify({"mensaje": "No hay deudas pendientes"}), 404

    return jsonify(result), 200