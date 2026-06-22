from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from app import db
from datetime import datetime, timezone

# --- USUARIO Y ROLES ---


class Rol(db.Model):
    __tablename__ = "rol"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)


class Usuario(db.Model):
    __tablename__ = "usuario"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    fecha_alta = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    rol_id = db.Column(db.Integer, db.ForeignKey("rol.id"))
    token = db.Column(db.String(256))

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "dni": self.dni,
            "nombres": self.nombres,
            "apellido": self.apellido,
            "fecha_alta": self.fecha_alta.isoformat() if self.fecha_alta else None,
            "rol_id": self.rol_id,
        }


class Administrador(db.Model):
    __tablename__ = "administrador"
    id_usuario = db.Column(
        db.Integer, db.ForeignKey("usuario.id", ondelete="CASCADE"), primary_key=True
    )


class Empleado(db.Model):
    __tablename__ = "empleado"
    id_usuario = db.Column(
        db.Integer, db.ForeignKey("usuario.id", ondelete="CASCADE"), primary_key=True
    )


class Cliente(db.Model):
    __tablename__ = "cliente"
    id_usuario = db.Column(
        db.Integer, db.ForeignKey("usuario.id", ondelete="CASCADE"), primary_key=True
    )


# --- PAGO ---


class Tarjeta(db.Model):
    __tablename__ = "tarjeta"
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), nullable=False)
    cvv = db.Column(db.String(4), nullable=False)
    fecha_vencimiento = db.Column(db.String(7), nullable=False)
    titular = db.Column(db.String(150), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "numero": self.numero,
            "fecha_vencimiento": self.fecha_vencimiento,
            "titular": self.titular,
        }


class ClienteTarjeta(db.Model):
    __tablename__ = "cliente_tarjeta"

    id_cliente = db.Column(
        "id_usuario", db.Integer, db.ForeignKey("cliente.id_usuario"), primary_key=True
    )

    id_tarjeta = db.Column(db.Integer, db.ForeignKey("tarjeta.id"), primary_key=True)


# Tabla intermedia Cliente_Tarjeta
# cliente_tarjeta = db.Table('cliente_tarjeta',
#    db.Column('id_usuario', db.Integer, db.ForeignKey('cliente.id_usuario'), primary_key=True),
#    db.Column('id_tarjeta', db.Integer, db.ForeignKey('tarjeta.id'), primary_key=True)
# )

# --- CLASES Y TURNOS ---


class Clase(db.Model):
    __tablename__ = "clase"
    id = db.Column(db.Integer, primary_key=True)
    dia = db.Column(db.String(15), nullable=False)
    hora = db.Column(
        db.String(10), nullable=False
    )  # SQLite no tiene tipo TIME nativo amigable
    disciplina = db.Column(db.String(100), nullable=False)
    cupo = db.Column(db.Integer, default=0)
    habilitada = db.Column(db.Boolean, default=True)


class Turno(db.Model):
    __tablename__ = "turno"
    id = db.Column(db.Integer, primary_key=True)
    habilitado = db.Column(db.Boolean, nullable=True)
    fecha = db.Column(db.Date, nullable=False)
    id_clase = db.Column(db.Integer, db.ForeignKey("clase.id"), nullable=False)
    __table_args__ = (db.UniqueConstraint("id_clase", "fecha", name="uq_clase_fecha"),)


# Tabla intermedia Cliente_asistio_turno
cliente_asistio_turno = db.Table(
    "cliente_asistio_turno",
    db.Column("id_turno", db.Integer, db.ForeignKey("turno.id"), primary_key=True),
    db.Column(
        "id_cliente", db.Integer, db.ForeignKey("cliente.id_usuario"), primary_key=True
    ),
)

# --- RESERVAS ---


class Reserva(db.Model):
    __tablename__ = "reserva"
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    id_cliente = db.Column(
        db.Integer, db.ForeignKey("cliente.id_usuario"), nullable=True
    )
    estado = db.Column(db.String(20), default="Pendiente")


class ReservaTurno(db.Model):
    __tablename__ = "reserva_turno"
    id_reserva = db.Column(db.Integer, db.ForeignKey("reserva.id"), primary_key=True)
    id_turno = db.Column(db.Integer, db.ForeignKey("turno.id"), nullable=False)


class ReservaClase(db.Model):
    __tablename__ = "reserva_clase"
    id_reserva = db.Column(db.Integer, db.ForeignKey("reserva.id"), primary_key=True)
    id_clase = db.Column(db.Integer, db.ForeignKey("clase.id"), nullable=False)


# --- ABONOS ---


class Abono(db.Model):
    __tablename__ = "abono"
    id_reserva = db.Column(db.Integer, db.ForeignKey("reserva.id"), primary_key=True)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    efectivo = db.Column(db.Boolean, default=True)


class AbonoTarjeta(db.Model):
    __tablename__ = "abono_tarjeta"
    id_abono = db.Column(
        db.Integer, db.ForeignKey("abono.id_reserva"), primary_key=True
    )
    id_tarjeta = db.Column(db.Integer, db.ForeignKey("tarjeta.id"), nullable=False)


class EmpleadoRegistraAbono(db.Model):
    __tablename__ = "empleado_registra_abono"
    id_empleado = db.Column(
        db.Integer, db.ForeignKey("empleado.id_usuario"), primary_key=True
    )
    id_abono = db.Column(
        db.Integer, db.ForeignKey("abono.id_reserva"), primary_key=True
    )


# --- CREDITOS ---
class Credito(db.Model):
    __tablename__ = "credito"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    disciplina = db.Column(db.String(100), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    id_turno = db.Column(db.Integer, db.ForeignKey("turno.id"), nullable=True)
    


# --- LISTA DE ESPERA ---


class TipoLista(db.Model):
    __tablename__ = "tipo_lista"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)


class ListaEspera(db.Model):
    __tablename__ = "lista_espera"
    id = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(
        db.Integer, db.ForeignKey("cliente.id_usuario"), nullable=False
    )
    tipo_lista_id = db.Column(
        db.Integer, db.ForeignKey("tipo_lista.id"), nullable=False
    )
    clase_id = db.Column(db.Integer, db.ForeignKey("clase.id"), nullable=True)
    turno_id = db.Column(db.Integer, db.ForeignKey("turno.id"), nullable=True)
    fecha_inscripcion = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Restricción CHECK de exclusividad
    __table_args__ = (
        db.CheckConstraint(
            "(clase_id IS NOT NULL AND turno_id IS NULL) OR (clase_id IS NULL AND turno_id IS NOT NULL)",
            name="check_exclusividad",
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "id_cliente": self.id_cliente,
            "tipo_lista_id": self.tipo_lista_id,
            "clase_id": self.clase_id,
            "turno_id": self.turno_id,
        }


def insertar_roles_y_listas(*args, **kwargs):
    # Verificamos si ya existen para no duplicar en futuras ejecuciones
    if Rol.query.count() == 0:
        roles = [
            Rol(id=1, nombre="cliente"),
            Rol(id=2, nombre="Administrador"),
            Rol(id=3, nombre="Empleado"),
        ]
        db.session.bulk_save_objects(roles)

    if TipoLista.query.count() == 0:
        listas = [
            TipoLista(id=1, nombre="General"),
            TipoLista(id=2, nombre="Abonados"),
            TipoLista(id=3, nombre="No abonados"),
        ]
        db.session.bulk_save_objects(listas)

    db.session.commit()


# Esto se ejecuta automáticamente DESPUÉS de que db.create_all() hace su trabajo
event.listen(db.metadata, "after_create", insertar_roles_y_listas)


##---------------
from datetime import datetime


class OfrecimientoReserva(db.Model):
    __tablename__ = "ofrecimiento_reserva"

    id = db.Column(db.Integer, primary_key=True)

    id_cliente = db.Column(
        db.Integer, db.ForeignKey("cliente.id_usuario"), nullable=False
    )

    cliente_emisor = db.Column(
        db.Integer,
        db.ForeignKey("cliente.id_usuario"),
        nullable=False
    )

    id_reserva = db.Column(
        db.Integer,
        db.ForeignKey("reserva.id"),
        nullable=False
    )

    fecha_envio = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    fecha_vencimiento = db.Column(db.DateTime, nullable=False)

    estado = db.Column(db.String(20), nullable=False, default="Pendiente")

    cliente = db.relationship(
        "Cliente",
        foreign_keys=[id_cliente]
    )

    emisor = db.relationship(
        "Cliente",
        foreign_keys=[cliente_emisor]
    )

    reserva = db.relationship("Reserva")

    __table_args__ = (
        db.CheckConstraint(
            """
            estado IN (
                'Pendiente',
                'Aceptado',
                'Rechazado',
                'Vencido'
            )
            """,
            name="check_estado",
        ),
    )


class ClienteSuspendido(db.Model):
    __tablename__ = "cliente_suspendido"
    id = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey("cliente.id_usuario"), nullable=False)
    id_turno = db.Column(db.Integer, db.ForeignKey("turno.id"), nullable=True)
    id_clase = db.Column(db.Integer, db.ForeignKey("clase.id"), nullable=True)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    __table_args__ = (
        db.CheckConstraint(
            "(id_clase IS NOT NULL AND id_turno IS NULL) OR (id_clase IS NULL AND id_turno IS NOT NULL)",
            name="check_exclusividad_suspension",
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "id_cliente": self.id_cliente,
            "id_turno": self.id_turno,
            "id_clase": self.id_clase,
            "monto": float(self.monto)
        }


