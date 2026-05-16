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