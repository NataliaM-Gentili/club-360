from flask import Blueprint, request, jsonify, session
from app.models.asistencia_manual_model import AsistenciaManualModel

asistencia_manual_bp = Blueprint("asistencia_manual", __name__)

# /ASISTENCIA/REGISTRAR_MANUAL --> empleado/admin registran asistencia ingresando el email del cliente
@asistencia_manual_bp.route("/asistencia/registrar_manual", methods=["POST"])
def registrar_asistencia_manual():
        if session.get("rol_id") != 3:
            return (
            jsonify({"ok": False, "mensaje": "Acceso denegado. Se requiere rol de empleado"}),
            403,
        )


        data = request.get_json(force=True) or {}
        email = (data.get("email") or "").strip()
        id_turno = data.get("id_turno")

        if not email or not id_turno:
            return jsonify({"ok": False, "mensaje": "Faltan datos: email y turno son obligatorios"}), 400

        ok, mensaje = AsistenciaManualModel.registrar_manual(email, id_turno)

        return jsonify({"ok": ok, "mensaje": mensaje}), 200 if ok else 400