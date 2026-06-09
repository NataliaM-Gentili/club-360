from flask import Blueprint, jsonify, session
from app.models.db_structure import Turno, Clase
from app.models.reserva_model import ReservaModel
from app.models.lista_espera_models import ListaEsperaModel

lista_espera_bp = Blueprint("lista_espera_bp", __name__)


# NO ABONADOS
@lista_espera_bp.route('/lista-espera-no-abonado/<int:id_cliente>/<int:id_turno>', methods=['POST'])
def lista_espera_no_abonado(id_cliente, id_turno):
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

    tipo_lista = ListaEsperaModel.obtener_tipo_lista_por_nombre('No abonados')
    if not tipo_lista:
        return jsonify({"mensaje": "Tipo de lista no encontrado"}), 500

    # el frontend evita éste caso pero se chequea igual por seguridad
    if ReservaModel.cliente_ya_inscripto_turno(id_cliente, id_turno):
        return jsonify({"mensaje": "Ya tiene una reserva activa para este turno"}), 400

    if ListaEsperaModel.existe_en_lista(
        id_cliente=id_cliente,
        tipo_lista_id=tipo_lista.id,
        turno_id=id_turno,
        clase_id=None,
    ):
        return jsonify({"mensaje": "Ya está anotado en esta lista de espera"}), 400

    # INSERCIÓN EN LISTA DE ESPERA
    lista = ListaEsperaModel.crear_lista_espera_no_abonado(
        id_cliente=id_cliente,
        tipo_lista_id=tipo_lista.id,
        id_turno=id_turno,
    )

    return jsonify({"mensaje": "Se agregó a la lista de espera no abonado", "id": lista.id}), 201


# ABONADOS
@lista_espera_bp.route('/lista-espera-abonado/<int:id_cliente>/<int:id_clase>', methods=['POST'])
def lista_espera_abonado(id_cliente, id_clase):
    if not session.get('usuario_id'):
        return jsonify({"mensaje": "No autenticado"}), 401

    if session.get('usuario_id') != id_cliente:
        return jsonify({"mensaje": "Acceso denegado"}), 403

    cliente = ListaEsperaModel.obtener_cliente(id_cliente)
    if not cliente:
        return jsonify({"mensaje": "Cliente no encontrado"}), 404

    clase = ListaEsperaModel.obtener_clase(id_clase)
    if not clase:
        return jsonify({"mensaje": "Clase no encontrada"}), 404

    tipo_lista = ListaEsperaModel.obtener_tipo_lista_por_nombre('Abonados')
    if not tipo_lista:
        return jsonify({"mensaje": "Tipo de lista no encontrado"}), 500

    if ReservaModel.cliente_ya_inscripto_clase(id_cliente, id_clase):
        return jsonify({"mensaje": "Ya tiene una reserva activa para esta clase"}), 400

    if ListaEsperaModel.existe_en_lista(
        id_cliente=id_cliente,
        tipo_lista_id=tipo_lista.id,
        turno_id=None,
        clase_id=id_clase,
    ):
        return jsonify({"mensaje": "Ya está anotado en esta lista de espera"}), 400

    # INSERCIÓN EN LISTA DE ESPERA
    lista = ListaEsperaModel.crear_lista_espera_abonado(
        id_cliente=id_cliente,
        tipo_lista_id=tipo_lista.id,
        id_clase=id_clase,
    )

    return jsonify({"mensaje": "Se agregó a la lista de espera abonado", "id": lista.id}), 201


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
@lista_espera_bp.route('/lista-espera/salir/<int:id_lista>/<int:id_cliente>', methods=['DELETE'])
def salir_lista_espera(id_lista, id_cliente):
    if not session.get('usuario_id'):
        return jsonify({"mensaje": "No autenticado"}), 401

    if session.get('usuario_id') != id_cliente:
        return jsonify({"mensaje": "Acceso denegado"}), 403

    lista = ListaEsperaModel.obtener_lista_por_id(id_lista)
    if not lista:
        return jsonify({"mensaje": "Registro de lista de espera no encontrado"}), 404

    if lista.id_cliente != id_cliente:
        return jsonify({"mensaje": "El cliente no pertenece a esta lista de espera"}), 403

    if not ListaEsperaModel.eliminar_lista_espera(id_lista):
        return jsonify({"mensaje": "No se pudo eliminar la lista de espera"}), 500

    return jsonify({"mensaje": "Se ha salido de la lista de espera"}), 200


