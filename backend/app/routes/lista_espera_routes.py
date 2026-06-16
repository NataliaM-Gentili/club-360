from flask import Blueprint, jsonify, session
from app import db
from datetime import datetime, timedelta
from decimal import Decimal
from app.models.db_structure import (
    Turno, Clase, Reserva, ReservaTurno, ReservaClase, 
    Abono, ListaEspera, OfrecimientoReserva
)
from app.models.reserva_model import ReservaModel
from app.models.lista_espera_models import ListaEsperaModel
from app.services.email_services import send_admin_waitlist_warning, send_ofrecimiento_turno_mail
from app.routes.reserva_routes import reset_reserva

lista_espera_bp = Blueprint("lista_espera_bp", __name__)


# INSERTAR CLIENTE EN LISTA_ESPERA 
#   única funcón multiuso
#   el tipo de lista es definido por el botón del front que tocó
#   la lista general es conceptual --> por orden de llegada
#   el campo clase_id en lista_espera NO SE USA
@lista_espera_bp.route('/lista-espera/<int:id_cliente>/<int:id_turno>/<int:tipo_lista>', methods=['POST'])
def lista_espera_no_abonado(id_cliente, id_turno, tipo_lista):
    if not session.get('usuario_id'):
        return jsonify({"mensaje": "No autenticado"}), 401

    if session.get('usuario_id') != id_cliente:
        return jsonify({"mensaje": "Acceso denegado"}), 403

    cliente = ListaEsperaModel.obtener_cliente(id_cliente)
    if not cliente:
        return jsonify({"mensaje": "Cliente no encontrado"}), 404

    turno = ListaEsperaModel.obtener_turno(id_turno)
    if not turno:
        return jsonify({"mensaje": "Turno no encontrado"}), 404

    if not tipo_lista:
        return jsonify({"mensaje": "No se recuperó el tipo de lista"}), 500

    # el frontend evita éste caso pero se chequea igual por seguridad
    if ReservaModel.cliente_ya_inscripto_turno(id_cliente, id_turno):
        return jsonify({"mensaje": "Ya tiene una reserva activa para este turno"}), 400

    if ListaEsperaModel.existe_en_lista(
        id_cliente=id_cliente,
        tipo_lista_id=tipo_lista,
        turno_id=id_turno,
        clase_id=None,
    ):
        return jsonify({"mensaje": "Ya está anotado en esta lista de espera"}), 400

    # INSERCIÓN EN LISTA DE ESPERA
    lista = ListaEsperaModel.crear_lista_espera_no_abonado(
        id_cliente=id_cliente,
        tipo_lista_id=tipo_lista, 
        id_turno=id_turno,
    )

    interesados = ListaEsperaModel.contar_interesados_por_turno(id_turno)
    if interesados == 10:
        send_admin_waitlist_warning(turno, interesados)

    return jsonify({"mensaje": "Se agregó a la lista de espera no abonado", "id": lista.id}), 201


# BUSCAR TODAS LAS INSTANCIAS DE UN USUARIO EN AMBAS LISTAS
@lista_espera_bp.route('/listas-espera/<int:id_cliente>')
def buscar_cliente_id(id_cliente):
    if not session.get('usuario_id'):
        return jsonify({"mensaje": "No autenticado"}), 401

    if session.get('usuario_id') != id_cliente:
        return jsonify({"mensaje": "Acceso denegado"}), 403

    cliente = ListaEsperaModel.obtener_cliente(id_cliente)
    if not cliente:
        return jsonify({"mensaje": "Cliente no encontrado"}), 404

    listas = ListaEsperaModel.obtener_listas_por_cliente(id_cliente)
    return jsonify({
        "listas": [lista.to_dict() for lista in listas]
    }), 200


# ELIMINA FILA DE LISTA_ESPERA
#@lista_espera_bp.route('/lista-espera/salir/<int:id_lista>/<int:id_cliente>', methods=['DELETE'])
#def salir_lista_espera(id_lista, id_cliente):
#    if not session.get('usuario_id'):
#        return jsonify({"mensaje": "No autenticado"}), 401
#
#    if session.get('usuario_id') != id_cliente:
#        return jsonify({"mensaje": "Acceso denegado"}), 403

#    lista = ListaEsperaModel.obtener_lista_por_id(id_lista)
#    if not lista:
#        return jsonify({"mensaje": "Registro de lista de espera no encontrado"}), 404

#    if lista.id_cliente != id_cliente:
#        return jsonify({"mensaje": "El cliente no pertenece a esta lista de espera"}), 403

#    if not ListaEsperaModel.eliminar_lista_espera(id_lista):
#        return jsonify({"mensaje": "No se pudo eliminar la lista de espera"}), 500

#    return jsonify({"mensaje": "Se ha salido de la lista de espera"}), 200


@lista_espera_bp.route('/lista-espera/salir/<int:id_cliente>/<int:id_turno>', methods=['DELETE'])
def salir_lista_espera_por_turno(id_cliente, id_turno):
    if not session.get('usuario_id'):
        return jsonify({"mensaje": "No autenticado"}), 401

    if session.get('usuario_id') != id_cliente:
        return jsonify({"mensaje": "Acceso denegado"}), 403

    cliente = ListaEsperaModel.obtener_cliente(id_cliente)
    if not cliente:
        return jsonify({"mensaje": "Cliente no encontrado"}), 404

    turno = ListaEsperaModel.obtener_turno(id_turno)
    if not turno:
        return jsonify({"mensaje": "Turno no encontrado"}), 404

    # Eliminar todas las entradas de lista de espera del cliente para ese turno
    deleted = ListaEsperaModel.eliminar_por_cliente_turno(id_cliente, id_turno)
    if not deleted:
        return jsonify({"mensaje": "No se encontraron entradas de lista de espera para eliminar"}), 404

    return jsonify({"mensaje": "Se ha salido de la lista de espera"}), 200


# FUNCIONALIDAD DE OFRECER TURNO LIBERADO
# debe ser disparada al cancelar una reserva de un turno
@lista_espera_bp.route('/lista-espera/ofrecer-turno/<int:cliente_emisor>/<int:id_reserva>/<int:id_turno>')
def ofrecimiento_turno(cliente_emisor, id_reserva, id_turno):
    
    # FLUJO:
    # 1. Se resuelve si el id_reserva está en reserva_turno o reserva_clase
    # 2. Se busca el id cliente elegido de la lista de espera (id_cliente_elegido) de la siguiente manera:
    # 2.1   Si es reserva_turno: 
        # 2.1.1 se elige de la lista de espera del turno id_turno el cliente con fecha_inscripción más antigua
        # 2.1.2 se elimina de lista de espera al cliente elegido
        # 2.1.3 se llama a reset_reserva(id_reserva)

    # 2.2 Si es reserva_clase:
        # 2.1.1 Se busca en la lista de espera del turno id_turno al cliente con fecha_inscripción más antigua y tipo_lista_id = 2. Si no hay se filtra solo por fecha
        # 2.1.2 se elimina de lista de espera al cliente elegido
        # 2.1.3 Crear una reserva id_cliente = 0 y abono asociado con el monto de turno individual y efectivo = 0
        # 2.1.4 Crear una reserva_turno asociada a la reserva y al turno liberado

    # 3. Crear ofrecimiento_reserva, la fecha de vencimiento será la fecha del turno

    # 4. Enviar mail de ofrecimiento llamando a send_ofrecimiento_turno_mail(ofrecimiento, id_cliente_elegido, id_turno, cliente_emisor)

    try:
        # 1. primero se fija si el turno cancelado corresponde a un no - abonado
        reserva = ReservaTurno.query.get(id_reserva)
        if (reserva): 
            cliente_elegido = (
                ListaEspera.query
                .filter_by(turno_id=id_turno)
                .order_by(ListaEspera.fecha_inscripcion)
                .first()
            )


            if (not cliente_elegido):
                return jsonify({
                    "mensaje": "No hay clientes en lista de espera"
                }), 200
            
            id_cliente_elegido = cliente_elegido.id_cliente

            inscripcion = ListaEspera.query.filter_by(id_cliente=id_cliente_elegido, turno_id=id_turno).first()
            db.session.delete(inscripcion)

            reset_reserva(id_reserva)
        
        else:
            # 2. si no corresponde a un no abonado, se fija si corresponde a un abonado
            reserva = ReservaClase.query.get(id_reserva)
            if (reserva): # turno en una clase
                # primero busca los abonados en lista de espera
                cliente_elegido = ListaEspera.query.filter_by(turno_id=id_turno, tipo_lista_id=2).order_by(ListaEspera.fecha_inscripcion).first()
                
                if (not cliente_elegido):
                    # si no encuentra, va por los no abonados
                    cliente_elegido = ListaEspera.query.filter_by(turno_id=id_turno).order_by(ListaEspera.fecha_inscripcion).first()

                if (not cliente_elegido):
                    return jsonify({
                        "mensaje": "No hay clientes en lista de espera"
                    }), 200

                id_cliente_elegido = cliente_elegido.id_cliente
            
                inscripcion = ListaEspera.query.filter_by(id_cliente=id_cliente_elegido, turno_id=id_turno).first()
                db.session.delete(inscripcion)

                # crea la reserva
                nueva_reserva = Reserva(id_cliente=None, estado="Pendiente")
                
                db.session.add(nueva_reserva)
                db.session.flush()

                # crea el abono con el mismo monto que la reserva original
                abono_original = Abono.query.filter_by(id_reserva=id_reserva).first()
                abono = Abono(
                    id_reserva=nueva_reserva.id,
                    monto=abono_original.monto,
                    efectivo=False
                )

                db.session.add(abono)

                # creo reserva_turno
                reserva_turno = ReservaTurno(
                    id_reserva=nueva_reserva.id,
                    id_turno=id_turno
                )

                db.session.add(reserva_turno)

                db.session.commit()

                id_reserva = nueva_reserva.id # sobreescribo la vieja reserva con la nueva

            else:
                return jsonify({"mensaje": "No existe la reserva"}), 404
        
        # Crea ofrecimiento_reserva
        vencimiento = Turno.query.filter_by(id = id_turno).first()

        ofrecimiento = OfrecimientoReserva(
            id_cliente = id_cliente_elegido,
            cliente_emisor = cliente_emisor,
            id_reserva = id_reserva,
            fecha_vencimiento = vencimiento.fecha
        )

        db.session.add(ofrecimiento)
        db.session.flush()
        db.session.commit()

        # Envia el mail
        send_ofrecimiento_turno_mail(ofrecimiento, id_cliente_elegido, id_turno, cliente_emisor)

        return jsonify({
            "mensaje": "Ofrecimiento creado correctamente"
        }), 201
    
    except Exception as e:
        return jsonify({"mensaje": str(e)}), 500


@lista_espera_bp.route("/ofrecer/aceptar/<int:id_ofrecimento>/<int:id_cliente_elegido>", methods=["POST"])
def aceptar_ofrecimiento(id_ofrecimento, id_cliente_elegido):

    ofrecimiento = OfrecimientoReserva.query.get(id_ofrecimento)

    if not ofrecimiento:
        return jsonify({"error": "El ofrecimiento no existe"}), 404

    if ofrecimiento.estado != "Pendiente":
        return jsonify({
            "error": "Este ofrecimiento ya fue procesado"
        }), 400

    if datetime.utcnow() > ofrecimiento.fecha_vencimiento:
        return jsonify({
            "error": "El ofrecimiento venció"
        }), 400

    try:
        # 1. Cambiar ofrecimiento.estado a "Aceptado"
        ofrecimiento.estado = "Aceptado"

        # 2. Para la reserva en ofrecimiento.id_reserva, cambiar reserva.id_cliente a id_cliente_elegido
        reserva_ofrecida = Reserva.query.get(id=ofrecimiento.id_reserva)
        if not reserva_ofrecida :
            return jsonify({"error": "La reserva no existe"}), 404
        
        reserva_ofrecida.id_cliente = id_cliente_elegido

        db.session.commit()

    except Exception as e:
        return jsonify({"mensaje": "Ocurrió un error"}), 500


@lista_espera_bp.route("/ofrecer/rechazar/<int:id_ofrecimento>/<int:id_turno>/<int:cliente_emisor>", methods=["POST"])
def rechazar_ofrecimiento(id_ofrecimento, id_turno, cliente_emisor):

    try:
        ofrecimiento = OfrecimientoReserva.query.get(id_ofrecimento)

        if not ofrecimiento:
            return jsonify({"error": "El ofrecimiento no existe"}), 404

        ofrecimiento.estado = "Rechazado"

        db.session.commit()

        ofrecimiento_turno(ofrecimiento.id_reserva, id_turno, cliente_emisor)
    
    except Exception as e:
        return jsonify({"mensaje": "Ocurrió un error"}), 500