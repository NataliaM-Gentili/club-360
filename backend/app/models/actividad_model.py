from app import db
from app.models.db_structure import Reserva, ReservaTurno, Turno, Clase, cliente_asistio_turno, ReservaClase

class ActividadModel:
    @staticmethod
    def get_actividades_por_cliente(id_cliente):
        # Trae la reserva el turno y la clase, y asistencia
        return db.session.query(
            Reserva, Turno, Clase, cliente_asistio_turno.c.id_cliente.label('asistencia')
        ).join(ReservaTurno, Reserva.id == ReservaTurno.id_reserva)\
         .join(Turno, ReservaTurno.id_turno == Turno.id)\
         .join(Clase, Turno.id_clase == Clase.id)\
         .outerjoin(cliente_asistio_turno, 
                    db.and_(Turno.id == cliente_asistio_turno.c.id_turno, 
                            cliente_asistio_turno.c.id_cliente == id_cliente))\
         .filter(Reserva.id_cliente == id_cliente)\
         .all()
    
    @staticmethod
    def get_actividades(id_cliente):
        resultados = []

        # 1) standalone (existing)
        standalone = ActividadModel.get_actividades_por_cliente(id_cliente)
        resultados.extend(standalone)

        # 2) monthly: for each ReservaClase, find Turno rows in the relevant month(s)
        from datetime import date
        hoy = date.today()
        # month range (current month)
        if hoy.month == 12:
            primer_dia_sig = date(hoy.year + 1, 1, 1)
        else:
            primer_dia_sig = date(hoy.year, hoy.month + 1, 1)

        monthly_query = (
            db.session.query(Reserva, Turno, Clase, cliente_asistio_turno.c.id_cliente.label('asistencia'))
            .join(ReservaClase, Reserva.id == ReservaClase.id_reserva)
            .join(Clase, ReservaClase.id_clase == Clase.id)
            .join(Turno, Turno.id_clase == Clase.id)
            .outerjoin(cliente_asistio_turno,
                       db.and_(Turno.id == cliente_asistio_turno.c.id_turno,
                               cliente_asistio_turno.c.id_cliente == id_cliente))
            .filter(
                Reserva.id_cliente == id_cliente,
                Turno.habilitado == True,
                Turno.fecha >= hoy,
                Turno.fecha < primer_dia_sig
            )
            .order_by(Turno.fecha)
            .all()
        )

        resultados.extend(monthly_query)
        return resultados