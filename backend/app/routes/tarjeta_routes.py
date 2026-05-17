from flask import Blueprint, request, jsonify, session
from app import db
from app.models.tarjeta_model import TarjetaModel

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
    data = request.get_json()
    
    id_reserva = data.get("id_reserva")
    id_tarjeta = data.get("id_tarjeta")
    
    abono = TarjetaModel.obtener_abono(id_reserva)
    
    user_id = TarjetaModel.obtener_usuario_con_reserva(id_reserva)
    #user_id = data.get("id_cliente")
    
    if user_id == 2:
        return jsonify({"mensaje": "Saldo insuficiente!"}), 200
    
    TarjetaModel.registrar_abono_tarjeta(id_reserva, id_tarjeta)
    
    return jsonify({"mensaje": f"Pago realizado con exito! Se han descontado {abono.monto} de la tarjeta {id_tarjeta}"}), 200
    
    
    