from app import db
from app.models.db_structure import Clase


class ClaseModel:

    @staticmethod
    def crear_clase(data):
        nueva_clase = Clase(
            dia=data["dia"],
            hora=data["hora"],
            disciplina=data["disciplina"].lower(),
            cupo=data["cupo"],
            habilitada=True,
        )
        db.session.add(nueva_clase)
        db.session.commit()
        return nueva_clase
    
    
    @staticmethod
    def buscar_clase_por_id(id_clase):
        return Clase.query.filter_by(id=id_clase).first()
    
    
    @staticmethod
    def habilitar_clase(clase):
        clase.habilitada = True
        db.session.commit()
        
        
    
