from flask import Blueprint, request, jsonify, session
from app import db
from datetime import date
from app.models.credito_model import CreditoModel
from app.services.email_services import (
    send_cancelacion_turno_cliente_email,
    send_cancellation_email,
    send_solicitud_reintegro_efectivo_mail,
)
from app.models.cancelacion_model import CancelacionModel
from app.models.db_structure import Usuario
from app.models.reserva_model import ReservaModel
from app.models.tarjeta_model import TarjetaModel
from app.models.db_structure import EmpleadoRegistraAbono

from app.models.db_structure import Usuario, Cliente
from app.models.db_structure import Reserva, ReservaTurno
from app.models.db_structure import Turno, Clase
from app.models.db_structure import Abono, AbonoTarjeta


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


# dado el email de un usuario. retorna sus RESERVAS PENDIENTES
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
    """
    Body JSON: { "id_turno": 5 }
    Requiere sesión de cliente (rol_id == 1).

    Flujo:
    1. Valida turno, cupo y que no esté ya inscripto.
    2. Verifica que el cliente tenga al menos una tarjeta asociada.
    3. Crea Reserva (Pendiente) + ReservaTurno + Abono (50% del precio).
    4. Devuelve id_reserva — el pago y el QR los maneja /pago_tarjeta.
    """
    id_cliente = session.get("usuario_id")
    datos = request.get_json()
    id_turno = datos.get("id_turno")

    if not id_turno:
        return jsonify({"mensaje": "Falta el id_turno"}), 400

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

    # Verificar que el cliente tenga al menos una tarjeta asociada
    tarjetas = TarjetaModel.obtener_tarjetas_usuario(id_cliente)
    if not tarjetas:
        return jsonify({"mensaje": "Usted no posee tarjetas asociadas para abonar la seña correspondiente"}), 400

    # Obtener precio según disciplina
    clase = Clase.query.get(turno.id_clase)
    precio = ReservaModel.obtener_precio_disciplina(clase.disciplina)
    if precio is None:
        return jsonify({"mensaje": "No se pudo determinar el precio de la disciplina"}), 400

    # Crear reserva con abono al 50% — queda Pendiente hasta que /pago_tarjeta confirme
    reserva = ReservaModel.reservar_turno_no_abonado(
        id_cliente=id_cliente,
        id_turno=id_turno,
        monto_total=precio,
    )

    # Enviar QR por email
    enviar_comprobante_qr_turno(
        id_cliente=id_cliente,
        id_reserva=reserva.id,
        id_turno=turno.id,
        disciplina=clase.disciplina,
        fecha=turno.fecha.strftime("%d/%m/%Y"),
        hora=clase.hora,
    )

    return jsonify({
        "mensaje": "Turno reservado con éxito",
        "id_reserva": reserva.id,
        "monto_total": precio
    }), 201



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
    # También retorna aquellos id_turno que no estén disponibles por cupo lleno
    turnos_restantes, turnos_ocupados = ReservaModel.turnos_restantes_mes(id_clase)
    if not turnos_restantes:
        return jsonify({"mensaje": "No hay turnos disponibles para esta clase en el mes actual"}), 400

    # Calcular monto con reglas de negocio
    monto, descuento_aplicado = ReservaModel.calcular_monto_abono_mensual(precio, turnos_restantes)

    # -----

    # Verificar si el cliente ya tiene reservas sueltas
    # para turnos de esta clase en el mes actual
    
    hoy = date.today()
    if hoy.month == 12:
        primer_dia_sig = date(hoy.year + 1, 1, 1)
    else:
        primer_dia_sig = date(hoy.year, hoy.month + 1, 1)

    ids_turnos_clase = [t.id for t in Turno.query.filter(
        Turno.id_clase == id_clase,
        Turno.habilitado == True,
        Turno.fecha >= hoy,
        Turno.fecha < primer_dia_sig,
    ).all()]

    reservas_turno_existentes = (
        db.session.query(ReservaTurno)
        .join(Reserva, ReservaTurno.id_reserva == Reserva.id)
        .filter(
            ReservaTurno.id_turno.in_(ids_turnos_clase),
            Reserva.id_cliente == id_cliente,
            Reserva.estado != "Cancelada",
        )
        .first()
    )

    if reservas_turno_existentes:
        return jsonify({
            "mensaje": "Ya posee reservas individuales para esta clase en el mes actual"
        }), 400

    # -----

    # Crear reserva
    reserva, turnos, turnos_ocupados = ReservaModel.abonar_mensual(
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
        "turnos_ocupados": turnos_ocupados,
    }
    if descuento_aplicado:
        respuesta["descuento"] = "20% aplicado por reserva después del día 15"

    return jsonify(respuesta), 201


# ELIMINAR RESERVA POR ID
@reserva_bp.route('/cancelar_reserva/<int:id_reserva>', methods=['DELETE'])
def cancelar_reserva(id_reserva):
    """Cancela una reserva pendiente (para cuando falla el pago)"""
    reserva = ReservaModel.obtener_reserva(id_reserva)
    
    if not reserva:
        return jsonify({"mensaje": "Reserva no encontrada"}), 404
    
    # Solo se pueden cancelar reservas pendientes
    if reserva.estado != "Pendiente":
        return jsonify({"mensaje": "Solo se pueden cancelar reservas pendientes"}), 400
    
    # Eliminar registros relacionados
    ReservaTurno.query.filter_by(id_reserva=id_reserva).delete()
    ReservaClase.query.filter_by(id_reserva=id_reserva).delete()
    Abono.query.filter_by(id_reserva=id_reserva).delete()
    AbonoTarjeta.query.filter_by(id_abono=id_reserva).delete()
    
    db.session.delete(reserva)
    db.session.commit()
    
    return jsonify({"mensaje": "Reserva cancelada"}), 200


# FUNCION AUXILIAR DE OFRECIMIENTO DE TURNOS LIBERADOS
def reset_reserva(id_reserva):
    # 1. Buscar la reserva cuyo id = id.reserva
    reserva = Reserva.query.filter_by(id=id_reserva).first()
    
    if not reserva:
        return False
    
    # 2. reserva.id_cliente = None (la desvinculamos del cliente original)
    reserva.id_cliente = None
    
    # 3. reserva.estado = "Pendiente"
    reserva.estado = "Pendiente"
    
    # 4. Buscar en tabla abono el que corresponda para reserva.id
    abono = Abono.query.filter_by(id_reserva=id_reserva).first()
    
    if abono:
        # 5. abono.efectivo = 0
        abono.efectivo = 0

        abono.monto = abono.monto * 2 # duplica el precio porque el nuevo cliente no habrá pagado la seña
        
        # 6. Buscar abono_tarjeta el que corresponda para abono.id_reserva (abono_tarjeta.id_abono = abono.id_reserva)
        abono_tarjeta = AbonoTarjeta.query.filter_by(id_abono=abono.id_reserva).first()
        
        # 7. Eliminar esa fila de abono_tarjeta si existe
        if abono_tarjeta:
            db.session.delete(abono_tarjeta)
    
    db.session.commit()
    return True

@reserva_bp.route('/cancelar_turno/<int:id_reserva>', methods=['POST'])
def cancelar_turno_cliente(id_reserva):
    """ recibe la reserva que se desea cancelar (seleccion)
    Flujo:
        1. Turno suelta: R.N: si cancela tres clases sueltas consecutivas, pierde el reintegro del 20%
            a) El turno ya fue abonado:
                i) Se listan las tarjetas del cliente
                ii) Si no posee tarjetas, se envía un mail para reintegro en efectivo
            b) El turno no fue abonado:
                i) se cancela normalmente
        2. Clase (mensual): 
            a) La clase ya fue abonada: 
                i) Se genera un crédito a favor para ESA actividad
            b) La clase no fue abonada:
                i) Se descuenta el turno del abono mensual
    """
    id_cliente = session.get('usuario_id')
    if not id_cliente:
        return jsonify({"mensaje": "No autenticado"}), 401
    if session.get('rol_id') != 1:
        return jsonify({"mensaje": "Acceso denegado"}), 403

    reserva = Reserva.query.get(id_reserva)
    if not reserva:
        return jsonify({"mensaje": "Reserva no encontrada"}), 404
    if reserva.id_cliente != id_cliente:
        return jsonify({"mensaje": "La reserva no pertenece a este cliente"}), 403
    if reserva.estado == "Cancelada":
        return jsonify({"mensaje": "La reserva ya estaba cancelada"}), 400

    from app.routes.lista_espera_routes import ofrecimiento_turno

    es_clase = ReservaClase.query.filter_by(id_reserva=id_reserva).first()
    es_turno = ReservaTurno.query.filter_by(id_reserva=id_reserva).first()

    # ---------- TURNO SUELTO ----------
    if es_turno and not es_clase:
        turno = Turno.query.get(es_turno.id_turno)
        clase = Clase.query.get(turno.id_clase)
        abono = Abono.query.filter_by(id_reserva=id_reserva).first()
        monto = float(abono.monto) if abono else 0

        tarjetas = TarjetaModel.get_by_user(id_cliente)
        if not tarjetas:
            send_solicitud_reintegro_efectivo_mail(id_cliente, clase.disciplina, monto)
            reintegro = "Sin tarjetas asociadas: se envió un mail para el reintegro en efectivo"
        else:
            reintegro = f"Se reintegraron ${monto:.2f} a su tarjeta"

        usuario = Usuario.query.get(id_cliente)
        turno = Turno.query.get(id_turno)
        send_cancelacion_turno_cliente_email(
            usuario.nombres, clase.disciplina,
            turno.fecha.strftime("%d/%m/%Y"), clase.hora,
            detalle=detalle        # "Se otorgó un crédito..." / "Se descontarán $X..."
        )

        resp, status = ofrecimiento_turno(cliente_emisor=id_cliente, id_reserva=id_reserva, id_turno=turno.id)
        if status not in (200, 201):
            return resp, status

        # suspensión por exceso de cancelaciones de turnos sueltos en el mes
        #sacarBeneficio = False
        #if CancelacionModel.supera_limite_sueltas(id_cliente):
            # pierde el beneficio del 20% 
        #    sacarBeneficio = True

        return jsonify({"mensaje": "Turno cancelado", "reintegro": reintegro}), 200

    # ---------- ABONO MENSUAL ----------
    if es_clase:
        id_turno = (request.get_json(silent=True) or {}).get('id_turno')
        if not id_turno:
            return jsonify({"mensaje": "Para cancelar un turno del abono debe indicar id_turno"}), 400

        clase = Clase.query.get(es_clase.id_clase)

        if es_clase.id_clase == 1:  # Voley -> crédito a favor
            CreditoModel.crear_credito(id_cliente, clase.disciplina)
            detalle = f"Se otorgó un crédito a favor para {clase.disciplina.capitalize()}"
            monto_descuento = 0  # se compensa con crédito, no con descuento de cuota
        else:
            monto_descuento = float(ReservaModel.obtener_precio_disciplina(clase.disciplina))
            detalle = f"Se descontarán ${monto_descuento:.2f} de la cuota mensual"

    
        resp, status = ofrecimiento_turno(cliente_emisor=id_cliente, id_reserva=id_reserva, id_turno=id_turno)
        if status not in (200, 201):
            return resp, status

        return jsonify({"mensaje": "Turno cancelado", "detalle": detalle}), 200

    return jsonify({"mensaje": "La reserva no corresponde a un turno ni a una clase"}), 404