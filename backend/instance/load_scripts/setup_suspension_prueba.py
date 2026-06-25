"""
Datos de prueba para testeo completo de "Registrar Pago en Efectivo".
Crea un mismo cliente con:
  - 1 Reserva pendiente de un turno suelto     → aparece como deuda de tipo "turno"
  - 1 ClienteSuspendido de una clase mensual   → aparece como deuda de tipo "suspensión"

Login empleado: empleado_prueba@club360.com / prueba123

Ejecutar desde backend/: python instance/load_scripts/setup_suspension_prueba.py
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from datetime import date, datetime, timedelta
from decimal import Decimal

from app import create_app, db
from app.models.db_structure import (
    Usuario, Cliente, Clase, Turno,
    Reserva, ReservaTurno, Abono, ClienteSuspendido
)
from werkzeug.security import generate_password_hash

app = create_app()

DIAS_SEMANA = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]

with app.app_context():
    hoy = date.today()
    dia_hoy = DIAS_SEMANA[hoy.weekday()]

    # ── CLIENTE DE PRUEBA ─────────────────────────────────────────────────
    email_cliente = "cliente_deudor@test.com"
    usuario = Usuario.query.filter_by(email=email_cliente).first()
    if not usuario:
        usuario = Usuario(
            email=email_cliente,
            dni="30000001",
            nombres="Deudor",
            apellido="Prueba",
            contrasena=generate_password_hash("prueba123"),
            rol_id=1,
        )
        db.session.add(usuario)
        db.session.flush()
        db.session.add(Cliente(id_usuario=usuario.id))
        print(f"Cliente creado: {email_cliente}")
    else:
        print(f"Cliente ya existia: {email_cliente}")

    # ── 1. RESERVA PENDIENTE DE TURNO SUELTO ─────────────────────────────
    hora_turno = (datetime.now() + timedelta(hours=2)).strftime("%H:%M")
    clase_turno = Clase(dia=dia_hoy, hora=hora_turno, disciplina="basquet", cupo=10, habilitada=True)
    db.session.add(clase_turno)
    db.session.flush()

    turno = Turno(fecha=hoy, id_clase=clase_turno.id, habilitado=True)
    db.session.add(turno)
    db.session.flush()

    reserva = Reserva(id_cliente=usuario.id, estado="Pendiente")
    db.session.add(reserva)
    db.session.flush()

    db.session.add(ReservaTurno(id_reserva=reserva.id, id_turno=turno.id))
    db.session.add(Abono(id_reserva=reserva.id, monto=Decimal("8500"), efectivo=True))
    print(f"Reserva turno creada: Basquet {hora_turno}hs, deuda=$8500")

    # ── 2. SUSPENSIÓN PENDIENTE DE CLASE MENSUAL ──────────────────────────
    clase_suspension = Clase(dia="Lunes", hora="19:00", disciplina="voley", cupo=10, habilitada=True)
    db.session.add(clase_suspension)
    db.session.flush()

    db.session.add(ClienteSuspendido(
        id_cliente=usuario.id,
        id_clase=clase_suspension.id,
        monto=Decimal("4500"),
    ))
    print(f"Suspensión creada: Voley Lunes 19:00hs, monto=$4500")

    db.session.commit()

    print(f"\nListo. Buscá deudas con email: {email_cliente}")
    print("Deberías ver dos items: una deuda de turno (Basquet) y una suspensión (Voley)")
