from flask import Blueprint, jsonify, session
from app.models.db_structure import Turno, Clase
from app.models.reserva_model import ReservaModel
from app.models.lista_espera_models import ListaEsperaModel

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


