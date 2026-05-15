from flask import Blueprint, request, jsonify
from app import db
from app.models.tarjeta_model import TarjetaModel

tarjeta_bp = Blueprint('tarjeta', __name__, url_prefix='/tarjeta')

@tarjeta_bp.route('/registrar-tarjeta', methods=['POST'])
def registrar_tarjeta():
    data = request.get_json()
    
    # Extraemos el id_cliente (asegúrate de enviarlo en el JSON)
    id = data.get("id")
    
    if not id or "numero" not in data:
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    try:
        resultado = TarjetaModel.registrar_tarjeta_a_cliente(id, data)
        
        if resultado["status"] == "exists":
            return jsonify({"mensaje": resultado["mensaje"]}), 200
            
        return jsonify({"mensaje": resultado["mensaje"]}), 201

    except Exception as e:
        from app import db
        db.session.rollback()
        return jsonify({"error": str(e)}), 500