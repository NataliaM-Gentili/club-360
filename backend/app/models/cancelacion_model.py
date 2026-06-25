from datetime import datetime
from decimal import Decimal
from app import db
from app.models.db_structure import Reserva, ReservaTurno, Usuario

LIMITE_CANCELACIONES_SUELTAS = 3  # más de 3 en el mes => suspensión
CANCELACIONES_SEGUIDAS_PIERDE_BENEFICIO = 3


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
    def perdio_beneficio_abono(id_cliente, id_clase):
        """
        True si el cliente canceló 3 turnos CONSECUTIVOS de la clase dentro del
        mes actual, sin ninguno asistido en el medio.
        El conteo se reinicia cada mes (solo mira los turnos del mes corriente).
        """
        from datetime import date
        from app.models.db_structure import Turno, AbonadoTurnoCancelado

        hoy = date.today()
        primer_dia_mes = hoy.replace(day=1)
        if hoy.month == 12:
            primer_dia_sig = date(hoy.year + 1, 1, 1)
        else:
            primer_dia_sig = date(hoy.year, hoy.month + 1, 1)

        turnos = (
            Turno.query
            .filter(
                Turno.id_clase == id_clase,
                Turno.habilitado == True,
                Turno.fecha >= primer_dia_mes,
                Turno.fecha <  primer_dia_sig,
            )
            .order_by(Turno.fecha)
            .all()
        )
        if len(turnos) < CANCELACIONES_SEGUIDAS_PIERDE_BENEFICIO:
            return False

        cancelados = {
            c.id_turno
            for c in AbonadoTurnoCancelado.query.filter_by(id_cliente=id_cliente).all()
        }

        seguidas = 0
        for t in turnos:
            seguidas = seguidas + 1 if t.id in cancelados else 0
            if seguidas >= CANCELACIONES_SEGUIDAS_PIERDE_BENEFICIO:
                return True
        return False

    @staticmethod
    def supera_limite_sueltas(id_cliente):
        return CancelacionModel.contar_sueltas_mes(id_cliente) > LIMITE_CANCELACIONES_SUELTAS


    @staticmethod
    def total_descuento_abono_mes(id_cliente):
        """Suma de montos de cancelaciones de abono del mes (para descontar de la cuota)."""
        return 8000.00