from app import db
import unicodedata
from app.routes.clase_routes import FERIADOS_2026
from app.models.db_structure import (
    Reserva,
    Abono,
    ReservaTurno,
    ReservaClase,
    Turno,
    Clase,
    ClienteTarjeta,
    Cliente
)
from datetime import date 
from decimal import Decimal


PRECIOS_DISCIPLINA = {
    "futbol": 9000,
    "paddle": 12000,
    "voley": 8000,
    "basquet": 8500,
}

def _normalizar(texto: str) -> str:
    return unicodedata.normalize("NFD", texto).encode("ascii", "ignore").decode("utf-8").lower().strip()


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
        

   
    @staticmethod
    def obtener_precio_disciplina(disciplina: str):
        return PRECIOS_DISCIPLINA.get(_normalizar(disciplina))
        
    @staticmethod
    def cliente_ya_inscripto_turno(id_cliente, id_turno):
        """True si el cliente ya tiene una reserva activa para ese turno."""
        return (
            db.session.query(ReservaTurno)
            .join(Reserva, ReservaTurno.id_reserva == Reserva.id)
            .filter(
                ReservaTurno.id_turno == id_turno,
                Reserva.id_cliente == id_cliente,
                Reserva.estado != "Cancelada",
            )
            .first() is not None
        )
        
    @staticmethod
    def cliente_ya_inscripto_clase(id_cliente, id_clase):
        """True si el cliente ya tiene una reserva de abono activa para esa clase."""
        return (
            db.session.query(ReservaClase)
            .join(Reserva, ReservaClase.id_reserva == Reserva.id)
            .filter(
                ReservaClase.id_clase == id_clase,
                Reserva.id_cliente == id_cliente,
                Reserva.estado != "Cancelada",
            )
            .first() is not None
        )
        
    
    @staticmethod
    def cupos_disponibles_turno(id_turno):
        """True si el turno tiene al menos un cupo libre."""
        turno = Turno.query.get(id_turno)
        if not turno:
            return False
        clase = Clase.query.get(turno.id_clase)
        ocupados = ReservaTurno.query.filter_by(id_turno=id_turno).count()
        return ocupados < clase.cupo
    
    
    
    @staticmethod
    def turnos_restantes_mes(id_clase):
        """
        Retorna los turnos habilitados desde hoy hasta fin de mes para una clase,
        excluyendo feriados nacionales.
        """
        hoy = date.today()
        if hoy.month == 12:
            primer_dia_sig = date(hoy.year + 1, 1, 1)
        else:
            primer_dia_sig = date(hoy.year, hoy.month + 1, 1)

        turnos = (
            Turno.query.filter(
                Turno.id_clase == id_clase,
                Turno.habilitado == True,
                Turno.fecha >= hoy,
                Turno.fecha < primer_dia_sig,
            )
            .order_by(Turno.fecha)
            .all()
        )

        disponibles = []
        ocupados_ids = []

        for t in turnos:
            # excluir feriados
            if t.fecha in FERIADOS_2026:
                continue

            clase = Clase.query.get(t.id_clase)
            if not clase:
                continue

            # contar reservas activas (no Canceladas) para este turno
            ocupados = (
                db.session.query(ReservaTurno)
                .join(Reserva, ReservaTurno.id_reserva == Reserva.id)
                .filter(ReservaTurno.id_turno == t.id, Reserva.estado != "Cancelada")
                .count()
            )

            if ocupados >= clase.cupo:
                ocupados_ids.append(t.id)
            else:
                disponibles.append(t)

        # Retorna (turnos_disponibles, ids_turnos_ocupados)
        return disponibles, ocupados_ids
    
        
    @staticmethod
    def calcular_monto_abono_mensual(precio_clase, turnos_restantes):
        """
        Reglas de negocio del abono mensual:
        - Hasta el día 15 inclusive: precio normal × cantidad de turnos del mes.
        - Después del día 15 con más de 1 turno restante: precio × cantidad × 0.80.
        - Después del día 15 con solo 1 turno restante: precio × 1 (sin descuento).
        Retorna (monto: Decimal, descuento_aplicado: bool).
        """
        hoy = date.today()
        cantidad = len(turnos_restantes)
        precio = Decimal(str(precio_clase))

        if hoy.day <= 15:
            return precio * cantidad, False
        else:
            if cantidad > 1:
                return precio * cantidad * Decimal("0.80"), True
            else:
                return precio, False
    
    
    
    # NO abonado
    @staticmethod
    def reservar_turno_no_abonado(id_cliente, id_turno, monto_total):
        """
        Crea Reserva (Pendiente) + ReservaTurno + Abono con monto (50% del precio).
        El pago de la seña se delega luego al endpoint /pago_tarjeta.
        Retorna la Reserva creada.
        """
        monto_sena = Decimal(str(monto_total)) / 2

        reserva = Reserva(id_cliente=id_cliente, estado="Pendiente")
        db.session.add(reserva)
        db.session.flush()

        db.session.add(ReservaTurno(id_reserva=reserva.id, id_turno=id_turno))

        db.session.add(Abono(
            id_reserva=reserva.id,
            monto=monto_sena,
            efectivo=False,
        ))

        db.session.commit()
        return reserva




    # ABONADO
    @staticmethod
    def abonar_mensual(id_cliente, id_clase, monto):
        """
        Crea Reserva (Pendiente) + ReservaClase + Abono (monto según reglas de negocio).
        El pago se gestiona posteriormente.
        Retorna (reserva, turnos_restantes).
        """
        turnos_restantes, turnos_ocupados = ReservaModel.turnos_restantes_mes(id_clase)

        reserva = Reserva(id_cliente=id_cliente, estado="Pendiente")
        db.session.add(reserva)
        db.session.flush()

        db.session.add(ReservaClase(id_reserva=reserva.id, id_clase=id_clase))

        db.session.add(Abono(
            id_reserva=reserva.id,
            monto=monto,
            efectivo=False,
        ))

        db.session.commit()
        return reserva, turnos_restantes, turnos_ocupados

    
    
    