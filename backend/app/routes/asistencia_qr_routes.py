from flask import Blueprint, request, jsonify
from app.models.asistencia_qr_model import AsistenciaModel

asistencia_bp = Blueprint("asistencia", __name__)


@asistencia_bp.route("/asistencia/registrar", methods=["POST"])
def registrar_asistencia():
    data = request.get_json(force=True)
    qr_data = data.get("qr_data", "").strip()

    if not qr_data:
        return (
            jsonify(
                {
                    "ok": False,
                    "mensaje": "Lo sentimos, el qr escaneado es incorrecto, por favor, vuelva a intentarlo.",
                }
            ),
            400,
        )

    ok, mensaje, payload = AsistenciaModel.registrar(qr_data)

    response = {"ok": ok, "mensaje": mensaje}

    if payload and payload.get("accion") == "completar_pago":
        response["codigo"] = "PAGO_INCOMPLETO"
        response["reserva_id"] = payload["reserva_id"]

    return jsonify(response), 200 if ok else 400
