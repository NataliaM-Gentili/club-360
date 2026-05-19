from flask import Blueprint, request, jsonify, session
from app import db

from app.models.reserva_model import ReservaModel
from app.models.tarjeta_model import TarjetaModel
from app.models.db_structure import EmpleadoRegistraAbono

from app.models.db_structure import Usuario, Cliente
from app.models.db_structure import Reserva, ReservaTurno
from app.models.db_structure import Turno, Clase
from app.models.db_structure import Abono


from sqlalchemy import exists
from app.models.db_structure import ReservaClase
from app.services.email_services import enviar_comprobante_qr_turno, enviar_comprobantes_qr_clase


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
    # TURNOS SUELTOS
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
            "id_cliente": cliente.id_usuario,
            "tipo": "turno",
            "disciplina": clase.disciplina,
            "fecha": str(turno.fecha),
            "hora": clase.hora,
            "monto_deuda": float(abono.monto),
        })

    # -------------------------
    # CLASES (mensuales)
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
            "id_cliente": cliente.id_usuario,
            "tipo": "clase",
            "disciplina": clase.disciplina,
            "fecha": "Mensual",
            "hora": clase.hora,
            "monto_deuda": float(abono.monto),
        })

    if not result:
        return jsonify({"mensaje": "No hay deudas pendientes"}), 404

    return jsonify(result), 200




# NO Abonado
@reserva_bp.route("/reservar_turno", methods=["POST"])
def reservar_turno():
    """""
    Flujo:
    1. Valida turno, cupo y que no esté ya inscripto.
    2. Verifica que la tarjeta pertenezca al cliente.
    3. Crea Reserva (en estado pendiente) + ReservaTurno + Abono (monto 50% del total).
    4. Procesa el pago de la seña con tarjeta.
       - Si el pago falla: revierte la reserva.
       - Si el pago es exitoso: registra AbonoTarjeta y envía QR por email.
    """
    if session.get("rol_id") != 1:
        return jsonify({"mensaje": "Acceso denegado. Debés iniciar sesión como cliente"}), 403

    id_cliente = session.get("usuario_id")
    datos = request.get_json()
    id_turno = datos.get("id_turno")
    id_tarjeta = datos.get("id_tarjeta")

    if not id_turno or not id_tarjeta:
        return jsonify({"mensaje": "Faltan datos requeridos (id_turno, id_tarjeta)"}), 400

    # Verificar que el turno existe y está habilitado
    turno = Turno.query.get(id_turno)
    if not turno or not turno.habilitado:
        return jsonify({"mensaje": "El turno no está disponible"}), 404

    # Verificar cupo
    if not ReservaModel.cupos_disponibles_turno(id_turno):
        return jsonify({"mensaje": "El turno no tiene cupos disponibles"}), 400

    # Verificar que no esté ya inscripto
    if ReservaModel.cliente_ya_inscripto_turno(id_cliente, id_turno):
        return jsonify({"mensaje": "Usted ya se encuentra inscripto al turno seleccionado"}), 400

    # Verificar que la tarjeta pertenezca al cliente
    tarjetas = ReservaModel.obtener_tarjetas_cliente(id_cliente)
    if not tarjetas:
        return jsonify({"mensaje": "No tenés tarjetas asociadas a tu cuenta"}), 400


    # Obtener precio según disciplina
    clase = Clase.query.get(turno.id_clase)
    precio = ReservaModel.obtener_precio_disciplina(clase.disciplina)
    if precio is None:
        return jsonify({"mensaje": "No se pudo determinar el precio de la disciplina"}), 400

    # Crear reserva con abono al 50% — queda Pendiente hasta confirmar pago
    reserva = ReservaModel.reservar_turno_no_abonado(
        id_cliente=id_cliente,
        id_turno=id_turno,
        monto_total=precio,
    )

    # Procesar pago de la seña con tarjeta
    pago_exitoso, mensaje_pago = _procesar_pago_tarjeta(reserva.id, id_tarjeta)

    if not pago_exitoso:
        # Revierte la reserva si el pago falló
        db.session.delete(ReservaModel.obtener_abono(reserva.id))
        db.session.delete(reserva)
        db.session.commit()
        return jsonify({
            "mensaje": "No se ha realizado el pago correctamente, no se ha podido reservar el turno"
        }), 402

    # Envia QR por email 
    enviar_comprobante_qr_turno(
        id_cliente=id_cliente,
        id_reserva=reserva.id,
        id_turno=turno.id,
        disciplina=clase.disciplina,
        fecha=turno.fecha.strftime("%d/%m/%Y"),
        hora=clase.hora,
    )

    return jsonify({"mensaje": "Turno reservado con éxito"}), 201




# Abonado
@reserva_bp.route("/abonar_mensual", methods=["POST"])
def abonar_mensual():
    """
    Flujo:
    1. Valido la clase y que no esté inscripto.
    2. Calcula monto según reglas del día 15.
    3. Crea Reserva (Pendiente) + ReservaClase + Abono.
    4. Envía un QR por cada turno restante del mes por email.
    """
    if session.get("rol_id") != 1:
        return jsonify({"mensaje": "Acceso denegado. Debés iniciar sesión como cliente"}), 403

    id_cliente = session.get("usuario_id")
    datos = request.get_json()
    id_clase = datos.get("id_clase")

    if not id_clase:
        return jsonify({"mensaje": "Falta el id_clase"}), 400

    # Verificar que la clase existe y está habilitada
    clase = Clase.query.get(id_clase)
    if not clase or not clase.habilitada:
        return jsonify({"mensaje": "La clase no está disponible"}), 404

    # Verificar que no esté ya inscripto
    if ReservaModel.cliente_ya_inscripto_clase(id_cliente, id_clase):
        return jsonify({"mensaje": "Usted ya se encuentra inscripto a la clase seleccionada"}), 400

    # Obtener precio según disciplina
    precio = ReservaModel.obtener_precio_disciplina(clase.disciplina)
    if precio is None:
        return jsonify({"mensaje": "No se pudo determinar el precio de la disciplina"}), 400

    # Obtener turnos restantes del mes (sin feriados)
    turnos_restantes = ReservaModel.turnos_restantes_mes(id_clase)
    if not turnos_restantes:
        return jsonify({"mensaje": "No hay turnos disponibles para esta clase en el mes actual"}), 400

    # Calcular monto con reglas de negocio
    monto, descuento_aplicado = ReservaModel.calcular_monto_abono_mensual(precio, turnos_restantes)

    # Crear reserva
    reserva, turnos = ReservaModel.abonar_mensual(
        id_cliente=id_cliente,
        id_clase=id_clase,
        monto=monto,
    )

    # Enviar QRs por email (uno por turno del mes, sin feriados)
    enviar_comprobantes_qr_clase(
        id_cliente=id_cliente,
        id_reserva=reserva.id,
        disciplina=clase.disciplina,
        hora=clase.hora,
        turnos=turnos,
    )

    respuesta = {
        "mensaje": "Clase reservada con éxito",
        "id_reserva": reserva.id,
        "monto_a_pagar": float(monto),
        "turnos_reservados": len(turnos),
    }
    if descuento_aplicado:
        respuesta["descuento"] = "20% aplicado por reserva después del día 15"

    return jsonify(respuesta), 201



def _procesar_pago_tarjeta(id_reserva, id_tarjeta):
    """
    Llama a la lógica de TarjetaModel para procesar el pago.
    Registra AbonoTarjeta si el pago es exitoso.
    Retorna (exitoso: bool, mensaje: str).

    El comportamiento de aprobación/rechazo está simulado en TarjetaModel
    (user_id == 2 → fallo, cualquier otro → éxito).
    """
    try:
        abono = ReservaModel.obtener_abono(id_reserva)
        if not abono:
            return False, "Abono no encontrado"

        # Simular resultado del pago (misma lógica que pago_tarjeta de tarjeta_routes)
        user_id = TarjetaModel.obtener_usuario_con_reserva(id_reserva)
        if user_id == 2:
            return False, "Saldo insuficiente"

        # Registrar el pago exitoso
        TarjetaModel.registrar_abono_tarjeta(id_reserva, id_tarjeta)

        return True, "Pago realizado con éxito"

    except Exception as e:
        return False, str(e)











