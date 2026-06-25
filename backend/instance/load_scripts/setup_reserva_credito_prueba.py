"""
Datos de prueba para "Reservar turno con crédito".
Crea:
  - Turnos de FUTBOL disponibles (para escenario 1: reserva exitosa)
  - Turno de PADEL con cupo lleno (para escenario 2: cupo máximo)
  - Suspensión de turno suelto (para escenario 3: cliente suspendido)

Testear en orden:
  1. Primero futbol (éxito) y padel (cupo lleno)
  2. Luego descomentar la sección de suspensión y re-ejecutar para escenario 3

Login: cliente_yoga_pendiente@test.com / prueba123

Ejecutar desde backend/: python instance/load_scripts/setup_reserva_credito_prueba.py
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from datetime import date, timedelta
from decimal import Decimal

from app import create_app, db
from app.models.db_structure import (
    Usuario, Cliente, Clase, Turno,
    Reserva, ReservaTurno, Abono, ClienteSuspendido
)
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    hoy = date.today()
    manana = hoy + timedelta(days=1)
    pasado = hoy + timedelta(days=2)

    DIAS = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
    dia_manana = DIAS[manana.weekday()]
    dia_pasado = DIAS[pasado.weekday()]

    usuario = Usuario.query.filter_by(email="cliente_yoga_pendiente@test.com").first()
    if not usuario:
        print("ERROR: No se encontro cliente_yoga_pendiente@test.com")
        exit()

    # ── 1. TURNOS DE FUTBOL DISPONIBLES (escenario 1) ─────────────────────
    clase_futbol = Clase(dia=dia_manana, hora="18:00", disciplina="futbol", cupo=10, habilitada=True)
    db.session.add(clase_futbol)
    db.session.flush()

    turno_futbol_1 = Turno(fecha=manana, id_clase=clase_futbol.id, habilitado=True)
    db.session.add(turno_futbol_1)
    db.session.flush()

    clase_futbol_2 = Clase(dia=dia_pasado, hora="20:00", disciplina="futbol", cupo=10, habilitada=True)
    db.session.add(clase_futbol_2)
    db.session.flush()

    turno_futbol_2 = Turno(fecha=pasado, id_clase=clase_futbol_2.id, habilitado=True)
    db.session.add(turno_futbol_2)
    db.session.flush()

    print(f"Turnos futbol creados:")
    print(f"  id={turno_futbol_1.id} | {dia_manana} {manana} 18:00hs | cupo=10")
    print(f"  id={turno_futbol_2.id} | {dia_pasado} {pasado} 20:00hs | cupo=10")

    # ── 2. TURNO DE PADEL CON CUPO LLENO (escenario 2) ────────────────────
    clase_padel = Clase(dia=dia_manana, hora="19:00", disciplina="padel", cupo=1, habilitada=True)
    db.session.add(clase_padel)
    db.session.flush()

    turno_padel = Turno(fecha=manana, id_clase=clase_padel.id, habilitado=True)
    db.session.add(turno_padel)
    db.session.flush()

    # Cliente dummy que ocupa el unico cupo
    email_dummy = "dummy_cupo@test.com"
    dummy = Usuario.query.filter_by(email=email_dummy).first()
    if not dummy:
        dummy = Usuario(
            email=email_dummy, dni="50000001", nombres="Dummy",
            apellido="Cupo", contrasena=generate_password_hash("prueba123"), rol_id=1,
        )
        db.session.add(dummy)
        db.session.flush()
        db.session.add(Cliente(id_usuario=dummy.id))

    reserva_dummy = Reserva(id_cliente=dummy.id, estado="Pago")
    db.session.add(reserva_dummy)
    db.session.flush()
    db.session.add(ReservaTurno(id_reserva=reserva_dummy.id, id_turno=turno_padel.id))
    db.session.add(Abono(id_reserva=reserva_dummy.id, monto=Decimal("12000"), efectivo=False))

    print(f"\nTurno padel LLENO creado:")
    print(f"  id={turno_padel.id} | {dia_manana} {manana} 19:00hs | cupo=1 (ocupado por dummy)")

    # ── 3. SUSPENSION DE TURNO SUELTO (escenario 3) ───────────────────────
    # DESCOMENTA estas lineas DESPUES de testear escenarios 1 y 2:
    #
    clase_susp= Clase(dia="Viernes", hora="10:00", disciplina="voley", cupo=10, habilitada=True)
    db.session.add(clase_susp)
    db.session.flush()
    turno_susp = Turno(fecha=hoy, id_clase=clase_susp.id, habilitado=True)
    db.session.add(turno_susp)
    db.session.flush()
    db.session.add(ClienteSuspendido(
    id_cliente=usuario.id, id_turno=turno_susp.id, monto=Decimal("5000"),
     ))
    print(f"\nSuspension creada para {usuario.email} (turno suelto id={turno_susp.id})")

    db.session.commit()

    print(f"\nLogin: cliente_yoga_pendiente@test.com / prueba123")
    print(f"\nEscenario 1: Mis Creditos -> Futbol -> seleccionar turno -> Reservar con credito -> exito")
    print(f"Escenario 2: Mis Creditos -> Padel -> seleccionar turno padel {manana} 19:00hs -> cupo lleno")
    print(f"Escenario 3: Descomentar seccion 3 del script, re-ejecutar, intentar reservar -> suspendido")
