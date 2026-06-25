"""
Testeo de la función automatizada suspender_abonados_pendientes().
Crea: cliente con ReservaClase Pendiente + turnos del mes actual para esa clase.
Llama la función directamente sin esperar al día 11.

Ejecutar desde backend/: python instance/load_scripts/test_suspension_automatica.py
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from datetime import date, timedelta
from decimal import Decimal

from app import create_app, db
from app.models.db_structure import (
    Usuario, Cliente, Clase, Turno,
    Reserva, ReservaClase, Abono, ClienteSuspendido
)
from werkzeug.security import generate_password_hash
from app.services.suspension_service import suspender_abonados_pendientes

app = create_app()

with app.app_context():
    hoy = date.today()

    # ── CLASE DE PRUEBA ───────────────────────────────────────────────────
    clase = Clase(dia="Lunes", hora="18:00", disciplina="yoga", cupo=10, habilitada=True)
    db.session.add(clase)
    db.session.flush()

    # ── TURNOS DEL MES ACTUAL (lunes de junio) ────────────────────────────
    # Buscamos todos los lunes del mes actual
    primer_dia = hoy.replace(day=1)
    if hoy.month == 12:
        ultimo_dia = hoy.replace(day=31)
    else:
        ultimo_dia = hoy.replace(month=hoy.month + 1, day=1) - timedelta(days=1)

    # Primer lunes del mes
    dias_hasta_lunes = (7 - primer_dia.weekday()) % 7
    primer_lunes = primer_dia + timedelta(days=dias_hasta_lunes)

    lunes_del_mes = []
    d = primer_lunes
    while d <= ultimo_dia:
        turno = Turno(fecha=d, id_clase=clase.id, habilitado=True)
        db.session.add(turno)
        lunes_del_mes.append(d)
        d += timedelta(weeks=1)

    db.session.flush()

    turnos_1_al_10 = [d for d in lunes_del_mes if d.day <= 10]
    print(f"Clase: Yoga Lunes 18:00hs (id={clase.id})")
    print(f"Turnos del mes: {[str(d) for d in lunes_del_mes]}")
    print(f"Turnos del 1 al 10: {[str(d) for d in turnos_1_al_10]}")

    # ── CLIENTE CON RESERVA CLASE PENDIENTE ───────────────────────────────
    email = "cliente_yoga_pendiente@test.com"
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        usuario = Usuario(
            email=email,
            dni="40000001",
            nombres="Yoga",
            apellido="Prueba",
            contrasena=generate_password_hash("prueba123"),
            rol_id=1,
        )
        db.session.add(usuario)
        db.session.flush()
        db.session.add(Cliente(id_usuario=usuario.id))

    monto_abono = Decimal("18000")
    reserva = Reserva(id_cliente=usuario.id, estado="Pendiente")
    db.session.add(reserva)
    db.session.flush()
    db.session.add(ReservaClase(id_reserva=reserva.id, id_clase=clase.id))
    db.session.add(Abono(id_reserva=reserva.id, monto=monto_abono, efectivo=True))
    db.session.commit()

    print(f"\nCliente: {email}")
    print(f"ReservaClase creada (estado=Pendiente, abono=${monto_abono})")

    # ── EJECUTAR FUNCIÓN AUTOMATIZADA ─────────────────────────────────────
    print("\nEjecutando suspender_abonados_pendientes()...")
    suspender_abonados_pendientes()

    # ── VERIFICAR RESULTADO ───────────────────────────────────────────────
    susp = ClienteSuspendido.query.filter_by(
        id_cliente=usuario.id,
        id_clase=clase.id,
    ).first()

    if susp:
        n_total = len(lunes_del_mes)
        n_1_10 = len(turnos_1_al_10)
        precio_x_turno = monto_abono / n_total
        monto_esperado = (precio_x_turno * n_1_10 * Decimal("1.05")).quantize(Decimal("0.01"))
        print(f"\nSuspension creada correctamente:")
        print(f"  Turnos del mes: {n_total} | Turnos del 1 al 10: {n_1_10}")
        print(f"  Precio por turno: ${precio_x_turno:.2f}")
        print(f"  Monto suspension (con 5% recargo): ${susp.monto}")
        print(f"  Monto esperado: ${monto_esperado}")
        print(f"  {'OK' if susp.monto == monto_esperado else 'DIFERENCIA DETECTADA'}")
    else:
        print("\nERROR: No se creó la suspensión.")
