from app import db
from app.models.db_structure import Turno, Clase, cliente_asistio_turno
from sqlalchemy import func

class TurnoModel:
    @staticmethod
    def get_all_turnos_vigentes():
       # Consulta el turno, la clase y cuenta las asistencias
        # asociadas a cada ID de turno
        query = db.session.query(
            Turno, 
            Clase, 
            db.func.count(cliente_asistio_turno.c.id_cliente).label('ocupados')
        ).join(Clase, Turno.id_clase == Clase.id)\
         .outerjoin(cliente_asistio_turno, Turno.id == cliente_asistio_turno.c.id_turno)\
         .group_by(Turno.id, Clase.id)\
         .all()
        return query