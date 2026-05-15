from app import db

class Item(db.Model):
    __tablename__ = "items"
    
    # mapea la estructura de la base de datos a variables de pyhton (no sólo tienen el nombre, sino las características de cada columna)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    # QUERY METHODS

    @classmethod
    def get_all(cls):
        return cls.query.all()
        
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }