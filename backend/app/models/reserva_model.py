from app import db

from app.models.db_structure import (
    Reserva,
    Abono
)


class ReservaModel:

    @staticmethod
    def obtener_reserva(id_reserva):
        return Reserva.query.filter_by(
            id=id_reserva
        ).first()
        

    @staticmethod
    def obtener_abono(id_reserva):
        return Abono.query.filter_by(
            id_reserva=id_reserva
        ).first()