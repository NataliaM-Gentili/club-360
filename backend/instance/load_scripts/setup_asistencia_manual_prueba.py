"""
Datos de prueba para "Pasar asistencia manual".

Crea:
  - 1 empleado para loguearse (rol 3)
  - 1 turno de HOY DENTRO de la ventana horaria permitida (±1h desde ahora)
  - 1 turno de HOY FUERA de la ventana horaria permitida (+3h desde ahora)
  - 3 clientes:
      * cliente_pago@test.com       -> inscripto + 100% pago   -> Escenario 1 (éxito)
      * cliente_sin_turno@test.com  -> sin ninguna inscripción -> Escenario 2
      * cliente_pendiente@test.com  -> inscripto sin pago      -> Escenario 3
  - cliente_pago@test.com también queda inscripto + pago en el turno FUERA
    de horario -> Escenario 4

Ejecutar desde backend/:  python instance/load_scripts/setup_asistencia_manual_prueba.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from datetime import date, datetime, timedelta
from decimal import Decimal

from app import create_app, db
from app.models.db_structure import (
    Usuario, Cliente, Empleado, Clase, Turno,
    Reserva, ReservaTurno, ReservaClase,Abono
)
from werkzeug.security import generate_password_hash

DIAS_SEMANA = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]

app = create_app()

with app.app_context():
    hoy = date.today()
    ahora = datetime.now()
    dia_hoy = DIAS_SEMANA[hoy.weekday()]

    # ── 1. EMPLEADO PARA LOGUEARSE ───────────────────────────────────────
    email_empleado = "empleado_prueba@club360.com"
    empleado_usuario = Usuario.query.filter_by(email=email_empleado).first()
    if not empleado_usuario:
        empleado_usuario = Usuario(
            email=email_empleado,
            dni="10000001",
            nombres="Empleado",
            apellido="Prueba",
            contrasena=generate_password_hash("prueba123"),
            rol_id=3,
        )
        db.session.add(empleado_usuario)
        db.session.flush()
        db.session.add(Empleado(id_usuario=empleado_usuario.id))
        print(f"Empleado creado: {email_empleado} / prueba123")
    else:
        print(f"Empleado ya existia: {email_empleado}")

    # ── 2. TURNO DE HOY DENTRO DEL HORARIO PERMITIDO ─────────────────────
    hora_dentro = ahora.strftime("%H:%M")

    clase_dentro = Clase(dia=dia_hoy, hora=hora_dentro, disciplina="futbol", cupo=10, habilitada=True)
    db.session.add(clase_dentro)
    db.session.flush()

    turno_dentro = Turno(fecha=hoy, id_clase=clase_dentro.id, habilitado=True)
    db.session.add(turno_dentro)
    db.session.flush()
    print(f"Turno DENTRO de horario -> id={turno_dentro.id} | {dia_hoy} {hora_dentro}hs | fecha={hoy}")

    # ── 3. TURNO DE HOY FUERA DEL HORARIO PERMITIDO ──────────────────────
    hora_fuera = (ahora + timedelta(hours=3)).strftime("%H:%M")

    clase_fuera = Clase(dia=dia_hoy, hora=hora_fuera, disciplina="paddle", cupo=10, habilitada=True)
    db.session.add(clase_fuera)
    db.session.flush()

    turno_fuera = Turno(fecha=hoy, id_clase=clase_fuera.id, habilitado=True)
    db.session.add(turno_fuera)
    db.session.flush()
    print(f"Turno FUERA de horario -> id={turno_fuera.id} | {dia_hoy} {hora_fuera}hs | fecha={hoy}")

    # ── 4. CLIENTES DE PRUEBA ─────────────────────────────────────────────
    def crear_cliente(email, dni, nombres):
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario:
            print(f"Cliente ya existia: {email}")
            return usuario
        usuario = Usuario(
            email=email,
            dni=dni,
            nombres=nombres,
            apellido="Prueba",
            contrasena=generate_password_hash("prueba123"),
            rol_id=1,
        )
        db.session.add(usuario)
        db.session.flush()
        db.session.add(Cliente(id_usuario=usuario.id))
        print(f"Cliente creado: {email} / prueba123")
        return usuario

    def crear_reserva(id_cliente, id_turno, estado, monto=5000):
        reserva = Reserva(id_cliente=id_cliente, estado=estado)
        db.session.add(reserva)
        db.session.flush()
        db.session.add(ReservaTurno(id_reserva=reserva.id, id_turno=id_turno))
        db.session.add(Abono(id_reserva=reserva.id, monto=Decimal(str(monto)), efectivo=True))
        return reserva

    # Escenario 1: inscripto + 100% pago, dentro de horario -> EXITO
    cliente_pago = crear_cliente("cliente_pago@test.com", "20000001", "Pago")
    crear_reserva(cliente_pago.id, turno_dentro.id, estado="Pago")
    # tambien inscripto + pago en el turno FUERA de horario -> Escenario 4
    crear_reserva(cliente_pago.id, turno_fuera.id, estado="Pago")

    # Escenario 2: no inscripto a ningun turno
    crear_cliente("cliente_sin_turno@test.com", "20000002", "SinTurno")

    # Escenario 3: inscripto pero sin pago completo
    cliente_pendiente = crear_cliente("cliente_pendiente@test.com", "20000003", "Pendiente")
    crear_reserva(cliente_pendiente.id, turno_dentro.id, estado="Pendiente")
    
        # Escenario extra: cliente con ABONO MENSUAL (ReservaClase) a la clase del turno DENTRO
    def crear_reserva_clase(id_cliente, id_clase, estado, monto=18000):
        reserva = Reserva(id_cliente=id_cliente, estado=estado)
        db.session.add(reserva)
        db.session.flush()
        db.session.add(ReservaClase(id_reserva=reserva.id, id_clase=id_clase))
        db.session.add(Abono(id_reserva=reserva.id, monto=Decimal(str(monto)), efectivo=True))
        return reserva

    cliente_abonado = crear_cliente("cliente_abonado@test.com", "20000004", "Abonado")
    crear_reserva_clase(cliente_abonado.id, clase_dentro.id, estado="Pago")


    db.session.commit()

    print("\nListo. Datos para probar:")
    print(f"\nLogin empleado:  {email_empleado} / prueba123")
    print(f"\nTurno DENTRO de horario (id={turno_dentro.id}, {dia_hoy} {hora_dentro}hs) -> usar en escenarios 1 y 3")
    print(f"Turno FUERA de horario  (id={turno_fuera.id}, {dia_hoy} {hora_fuera}hs) -> usar en escenario 4")
    print("\nEscenario 1 (exito):         cliente_pago@test.com      + turno DENTRO")
    print("Escenario 2 (no inscripto):  cliente_sin_turno@test.com + turno DENTRO")
    print("Escenario 3 (sin pago):      cliente_pendiente@test.com + turno DENTRO")
    print("Escenario 4 (fuera horario): cliente_pago@test.com      + turno FUERA")
    print("Escenario 5 (abono mensual): cliente_abonado@test.com   + turno DENTRO")
