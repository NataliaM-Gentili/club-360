from flask import Blueprint, jsonify, session
from app import db
from datetime import datetime, timedelta
from decimal import Decimal
from app.models.db_structure import (
    Turno, Clase, Reserva, ReservaTurno, ReservaClase, 
    Abono, ListaEspera, OfrecimientoReserva, AbonoTarjeta, ClienteSuspendido
)
from app.models.reserva_model import ReservaModel
from app.models.lista_espera_models import ListaEsperaModel

suspension_bp = Blueprint("suspension_bp", __name__)

@suspension_bp.route('/pagar-suspension/<int:id_suspension>', methods=['DELETE'])
def pagar_suspension(id_suspension):

    suspension = ClienteSuspendido.query.get(id_suspension)

    if not suspension:
        return jsonify({
            "mensaje": "Suspensión no encontrada"
        }), 404

    db.session.delete(suspension)
    db.session.commit()

    return jsonify({
        "mensaje": "Alta solicitada correctamente"
    }), 200

