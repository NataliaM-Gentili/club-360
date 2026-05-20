from datetime import datetime

from app.models.reserva_model import ReservaModel
from flask import Blueprint, request, jsonify, session
from app import db
from app.models.tarjeta_model import TarjetaModel
from app.models.db_structure import ReservaTurno, Turno, Clase

tarjeta_bp = Blueprint('tarjeta', __name__)

@tarjeta_bp.route('/registrar-tarjeta', methods=['POST'])
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
        return jsonify({
            "error": "Faltan datos obligatorios",
            "missing_fields": missing
        }), 400

    fecha_venc = datetime.strptime(data["fecha_vencimiento"], "%Y-%m")
    if fecha_venc.replace(day=1) < datetime.today().replace(day=1):
        return jsonify({"error": "La tarjeta está vencida"}), 400
    
    try:
        resultado = TarjetaModel.registrar_tarjeta_a_cliente(id, data)
        
        if resultado["status"] == "exists":
            return jsonify({"mensaje": resultado["mensaje"]}), 200
            
        return jsonify({"mensaje": resultado["mensaje"]}), 201

    except Exception as e:
        from app import db
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@tarjeta_bp.route('/tarjetas/<int:id_cliente>', methods=['GET'])
def obtener_tarjetas(id_cliente):
    tarjetas = TarjetaModel.obtener_tarjetas_usuario(id_cliente)
    return jsonify([{
        "id": t.id,
        "numero": t.numero[-4:],
        "titular": t.titular,
        "fecha_vencimiento": t.fecha_vencimiento
    } for t in tarjetas]), 200
    
@tarjeta_bp.route('/pago_tarjeta', methods=['POST'])
def pago_tarjeta():
    """ Recibo id_reserva y id_tarjeta (la seleccionada en obtener_tarjetas())"""
    data = request.get_json()
    
    id_reserva = data.get('id_reserva')
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

   
    abono = TarjetaModel.obtener_abono(id_reserva)
    if not abono:
        return jsonify({
            "mensaje": "Abono no encontrado"
        }), 404

    # retorna el ID del usuario
    user_id = TarjetaModel.obtener_usuario_con_reserva(id_reserva)
    if user_id == 2:
        return jsonify({"mensaje": "Saldo insuficiente!"}), 200
    
    id_tarjeta = data.get('id_tarjeta')
    abono.efectivo = False
    reserva.estado = "Pago"
    TarjetaModel.registrar_abono_tarjeta(id_reserva, id_tarjeta)
    
    db.session.commit()
    return jsonify({"mensaje": f"Pago realizado con exito! Se han descontado {abono.monto}"}), 200
