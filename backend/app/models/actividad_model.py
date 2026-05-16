from app import db
from app.models.db_structure import Reserva, ReservaTurno, Turno, Clase, cliente_asistio_turno

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