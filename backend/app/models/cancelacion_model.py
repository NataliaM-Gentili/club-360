from datetime import datetime
from decimal import Decimal
from app import db
from app.models.db_structure import Reserva, ReservaTurno, Usuario

LIMITE_CANCELACIONES_SUELTAS = 3  # más de 3 en el mes => suspensión


class CancelacionModel:
    @staticmethod
    def contar_sueltas_mes(id_cliente):
        from datetime import datetime, timedelta

        limite = datetime.utcnow() - timedelta(minutes=10)

        cantidad = (
            db.session.query(Reserva)
            .join(ReservaTurno, ReservaTurno.id_reserva == Reserva.id and Reserva.id_cliente == id_cliente)
            .filter(Reserva.estado == "Pendiente")
            .filter(Reserva.fecha <= limite)
            .count()
        )
        return cantidad;

    @staticmethod
    def supera_limite_sueltas(id_cliente):
        return CancelacionModel.contar_sueltas_mes(id_cliente) > LIMITE_CANCELACIONES_SUELTAS


    @staticmethod
    def total_descuento_abono_mes(id_cliente):
        """Suma de montos de cancelaciones de abono del mes (para descontar de la cuota)."""
        return 8000.00