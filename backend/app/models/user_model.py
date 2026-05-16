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
        
from app import db

# recupera la estructura de la bd mapeada a objetos
from app.models.db_structure import Usuario, Cliente

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class UserModel:

    @staticmethod # recupera el primer usuario cuyo email coincida con el pasado por parámetro
    def get_user_by_email(email):
        return Usuario.query.filter_by(email=email).first()

    # recupera el usuario por id
    @staticmethod
    def get_by_id(user_id):
        return Usuario.query.get(user_id)


    @staticmethod # sube a la bd el nuevo usuario a la tabla usuario y su id a la tabla cliente
    def create_user(data):
        hashed_password = generate_password_hash(data["contrasena"])

        new_user = Usuario(
            email=data["email"],
            dni=data["dni"],
            nombres=data["nombres"],
            apellido=data["apellido"],
            contrasena=hashed_password,
            fecha_alta=datetime.utcnow(),
            rol_id=1  # cliente
        )

        db.session.add(new_user)
        db.session.flush()  
        # flush to get the generated ID without committing yet

        # create entry in cliente table
        new_cliente = Cliente(id_usuario=new_user.id)
        db.session.add(new_cliente)

        db.session.commit()

        return new_user

    
    @staticmethod
    def obtener_email_usuario(email):
        # Busca en la tabla Usuario por email
        return Usuario.query.filter_by(email=email).first()

    @staticmethod
    def verificar_contrasena(usuario_obj, password_plana):
        # Compara la contraseña del form con el hash de la base de datos
        return check_password_hash(usuario_obj.contrasena, password_plana)