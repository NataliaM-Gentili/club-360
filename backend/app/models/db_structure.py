from app import db
from datetime import datetime

# --- USUARIO Y ROLES ---

class Rol(db.Model):
    __tablename__ = 'rol'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    fecha_alta = db.Column(db.Date, default=datetime.utcnow)
    rol_id = db.Column(db.Integer, db.ForeignKey('rol.id'))

class Administrador(db.Model):
    __tablename__ = 'administrador'
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), primary_key=True)

class Empleado(db.Model):
    __tablename__ = 'empleado'
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), primary_key=True)

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), primary_key=True)

# --- PAGO ---

class Tarjeta(db.Model):
    __tablename__ = 'tarjeta'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), nullable=False)
    cvv = db.Column(db.String(4), nullable=False)
    fecha_vencimiento = db.Column(db.String(7), nullable=False)
    titular = db.Column(db.String(150), nullable=False)

class ClienteTarjeta(db.Model):
    __tablename__ = 'ClienteTarjeta'
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente.id_usuario'), primary_key=True)
    id_tarjeta = db.Column(db.Integer, db.ForeignKey('tarjeta.id'), primary_key=True)
# Tabla intermedia Cliente_Tarjeta
#cliente_tarjeta = db.Table('cliente_tarjeta',
#    db.Column('id_usuario', db.Integer, db.ForeignKey('cliente.id_usuario'), primary_key=True),
#    db.Column('id_tarjeta', db.Integer, db.ForeignKey('tarjeta.id'), primary_key=True)
#)

# --- CLASES Y TURNOS ---

class Clase(db.Model):
    __tablename__ = 'clase'
    id = db.Column(db.Integer, primary_key=True)
    dia = db.Column(db.String(15), nullable=False)
    hora = db.Column(db.String(10), nullable=False) # SQLite no tiene tipo TIME nativo amigable
    disciplina = db.Column(db.String(100), nullable=False)
    entrenador = db.Column(db.String(100))
    cupo = db.Column(db.Integer, default=0)
    habilitada = db.Column(db.Boolean, default=True)

class Turno(db.Model):
    __tablename__ = 'turno'
    id = db.Column(db.Integer, primary_key=True)
    habilitado = db.Column(db.Boolean, nullable=True)
    fecha = db.Column(db.Date, nullable=False)
    id_clase = db.Column(db.Integer, db.ForeignKey('clase.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('id_clase', 'fecha', name='uq_clase_fecha'),)

# Tabla intermedia Cliente_asistio_turno
cliente_asistio_turno = db.Table('cliente_asistio_turno',
    db.Column('id_turno', db.Integer, db.ForeignKey('turno.id'), primary_key=True),
    db.Column('id_cliente', db.Integer, db.ForeignKey('cliente.id_usuario'), primary_key=True)
)

# --- RESERVAS ---

class Reserva(db.Model):
    __tablename__ = 'reserva'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente.id_usuario'), nullable=False)
    estado = db.Column(db.String(20), default='Pendiente')

class ReservaTurno(db.Model):
    __tablename__ = 'reserva_turno'
    id_reserva = db.Column(db.Integer, db.ForeignKey('reserva.id'), primary_key=True)
    id_turno = db.Column(db.Integer, db.ForeignKey('turno.id'), nullable=False)

class ReservaClase(db.Model):
    __tablename__ = 'reserva_clase'
    id_reserva = db.Column(db.Integer, db.ForeignKey('reserva.id'), primary_key=True)
    id_clase = db.Column(db.Integer, db.ForeignKey('clase.id'), nullable=False)

# --- ABONOS ---

class Abono(db.Model):
    __tablename__ = 'abono'
    id_reserva = db.Column(db.Integer, db.ForeignKey('reserva.id'), primary_key=True)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    efectivo = db.Column(db.Boolean, default=True)

class AbonoTarjeta(db.Model):
    __tablename__ = 'abono_tarjeta'
    id_abono = db.Column(db.Integer, db.ForeignKey('abono.id_reserva'), primary_key=True)
    id_tarjeta = db.Column(db.Integer, db.ForeignKey('tarjeta.id'), nullable=False)

class EmpleadoRegistraAbono(db.Model):
    __tablename__ = 'empleado_registra_abono'
    id_empleado = db.Column(db.Integer, db.ForeignKey('empleado.id_usuario'), primary_key=True)
    id_abono = db.Column(db.Integer, db.ForeignKey('abono.id_reserva'), primary_key=True)

# --- LISTA DE ESPERA ---

class TipoLista(db.Model):
    __tablename__ = 'tipo_lista'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)

class ListaEspera(db.Model):
    __tablename__ = 'lista_espera'
    id = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente.id_usuario'), nullable=False)
    tipo_lista_id = db.Column(db.Integer, db.ForeignKey('tipo_lista.id'), nullable=False)
    clase_id = db.Column(db.Integer, db.ForeignKey('clase.id'), nullable=True)
    turno_id = db.Column(db.Integer, db.ForeignKey('turno.id'), nullable=True)

    # Restricción CHECK de exclusividad
    __table_args__ = (
        db.CheckConstraint(
            '(clase_id IS NOT NULL AND turno_id IS NULL) OR (clase_id IS NULL AND turno_id IS NOT NULL)',
            name='check_exclusividad'
        ),
    )
