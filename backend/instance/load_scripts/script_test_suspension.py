import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from datetime import date, timedelta
from decimal import Decimal
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models.db_structure import (
    Usuario, Cliente, Rol, Clase, Turno, ClienteSuspendido
)

HOY          = date(2026, 7, 1)
FECHA_TURNO  = HOY + timedelta(days=3)   # 4/7
DIA          = "Sábado"
HORA         = "18:00"

app = create_app()

with app.app_context():
    try:
        rol_cliente = Rol.query.filter_by(nombre="cliente").first()
        password = generate_password_hash("test1234")

        # ── Usuario ─────────────────────────────────────────────────
        user = Usuario(
            nombres="Carlos",
            apellido="Suspendido",
            email="carlosusp@test.com",
            dni="99999999",
            contrasena=password,
            rol_id=rol_cliente.id,
        )
        db.session.add(user); db.session.flush()
        db.session.add(Cliente(id_usuario=user.id)); db.session.flush()

        # ── Clases y turno ──────────────────────────────────────────
        clase_futbol = Clase(dia=DIA, hora=HORA, disciplina="futbol", cupo=10, habilitada=True)
        clase_padel  = Clase(dia=DIA, hora=HORA, disciplina="paddle", cupo=10, habilitada=True)
        db.session.add_all([clase_futbol, clase_padel]); db.session.flush()

        turno_futbol = Turno(habilitado=True, fecha=FECHA_TURNO, id_clase=clase_futbol.id)
        db.session.add(turno_futbol); db.session.flush()

        # ── Suspensiones ────────────────────────────────────────────
        db.session.add(ClienteSuspendido(
            id_cliente=user.id,
            id_turno=turno_futbol.id,
            monto=Decimal("4500"),
        ))
        db.session.add(ClienteSuspendido(
            id_cliente=user.id,
            id_clase=clase_padel.id,
            monto=Decimal("6000"),
        ))

        db.session.commit()
        print("=== script_test_suspension.py cargado ===")
        print(f"Usuario: carlosusp@test.com / test1234")
        print(f"Esc1: Reservar turno suelto Fútbol {FECHA_TURNO} → suspendido por turno")
        print(f"Esc2: Abonar mensual Padel → suspendido en la disciplina")

    except Exception as e:
        db.session.rollback()
        raise
