from flask import Blueprint, jsonify, session
from app.models.credito_model import CreditoModel

credito_bp = Blueprint("credito_bp", __name__)


@credito_bp.route("/creditos", methods=["GET"])
def get_creditos():
    id_usuario = session.get("usuario_id")  # misma clave que el resto del proyecto

    if not id_usuario:
        return jsonify({"error": "No autenticado"}), 401

    if session.get("rol_id") != 1:
        return jsonify({"error": "Acceso denegado"}), 403

    creditos = CreditoModel.get_creditos_activos_by_usuario(id_usuario)
    return jsonify({"creditos": creditos}), 200
