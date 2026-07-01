"""
Script de PRUEBA — Club 360
Para ajustar la ventana horaria solo modificar HORA_PRINCIPAL.
HORA_TEMPRANA debe ser al menos 2h después de HORA_PRINCIPAL.

Ejecutar desde backend/:
    python instance/load_scripts/script_demo_hoy.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from run import app
from app import db
from app.models.db_structure import (
    Usuario, Administrador, Empleado, Cliente,
    Clase, Turno, Reserva, ReservaTurno, ReservaClase,
    Abono, AbonoTarjeta, Tarjeta, ClienteTarjeta,
    ClienteSuspendido, OfrecimientoReserva, ListaEspera,
    AbonadoTurnoCancelado, EmpleadoRegistraAbono, Credito,
    cliente_asistio_turno,
)
from app.services.email_services import (
    enviar_comprobante_qr_turno,
    enviar_comprobantes_qr_clase,
    send_ofrecimiento_turno_mail,
)
from datetime import date, datetime, timedelta
from decimal import Decimal
from werkzeug.security import generate_password_hash

# =====================================================================
# CONFIGURACIÓN — solo tocar estas líneas para cambiar la ventana
# =====================================================================
HOY            = date(2026, 6, 30)  # Martes 30/6/2026
DIA            = "Martes"
HORA_PRINCIPAL = "22:00"   # ← ventana actual: 21:00–23:00
HORA_EXPIRADA  = "14:00"   # siempre expirada (mañana lejano pasado)
HORA_TEMPRANA  = "23:59"   # demasiado temprano (funciona hasta las 22:59)
# =====================================================================


def limpiar_bd():
    print("Limpiando base de datos...")
    db.session.execute(cliente_asistio_turno.delete())
    db.session.query(AbonadoTurnoCancelado).delete()
    db.session.query(EmpleadoRegistraAbono).delete()
    db.session.query(OfrecimientoReserva).delete()
    db.session.query(ListaEspera).delete()
    db.session.query(Credito).delete()
    db.session.query(ClienteSuspendido).delete()
    db.session.query(AbonoTarjeta).delete()
    db.session.query(Abono).delete()
    db.session.query(ReservaTurno).delete()
    db.session.query(ReservaClase).delete()
    db.session.query(Reserva).delete()
    db.session.query(Turno).delete()
    db.session.query(Clase).delete()
    db.session.query(ClienteTarjeta).delete()
    db.session.query(Tarjeta).delete()
    db.session.query(Cliente).delete()
    db.session.query(Empleado).delete()
    db.session.query(Administrador).delete()
    db.session.query(Usuario).delete()
    db.session.commit()


def poblar():
    password = generate_password_hash("prueba123")

    # =================================================================
    # 1. USUARIOS
    # =================================================================
    admin = Usuario(
        email="adminclub360@gmail.com", dni="10000001",
        nombres="Admin", apellido="Demo", contrasena=password, rol_id=2,
    )
    empleado = Usuario(
        email="recepcion360@gmail.com", dni="10000002",
        nombres="Enzo", apellido="Fernandez", contrasena=password, rol_id=3,
    )
    juan = Usuario(
        email="juanmanuelperezz468@gmail.com", dni="10000003",
        nombres="Juan Manuel", apellido="Perez", contrasena=password, rol_id=1,
    )
    tomas = Usuario(
        id=50,
        email="rivastoma0@gmail.com", dni="10000005",
        nombres="Tomas", apellido="Rivas", contrasena=password, rol_id=1,
    )
    sofi = Usuario(
        email="sofimendez@gmail.com", dni="10000006",
        nombres="Sofia", apellido="Mendez", contrasena=password, rol_id=1,
    )
    carlos = Usuario(
        email="carlosgomez@gmail.com", dni="10000007",
        nombres="Carlos", apellido="Gomez", contrasena=password, rol_id=1,
    )

    db.session.add_all([admin, empleado, juan, tomas, sofi, carlos])
    db.session.flush()

    db.session.add(Administrador(id_usuario=admin.id))
    db.session.add(Empleado(id_usuario=empleado.id))
    for u in [juan, tomas, sofi, carlos]:
        db.session.add(Cliente(id_usuario=u.id))
    db.session.flush()

    # =================================================================
    # 2. TARJETAS
    # =================================================================
    tarjeta_juan = Tarjeta(
        numero="4532000012341234", cvv="123",
        fecha_vencimiento="12/27", titular="JUAN MANUEL PEREZ",
    )
    tarjeta_tomas = Tarjeta(
        numero="5412750012349876", cvv="321",
        fecha_vencimiento="06/28", titular="TOMAS RIVAS",
    )
    db.session.add_all([tarjeta_juan, tarjeta_tomas])
    db.session.flush()
    db.session.add(ClienteTarjeta(id_cliente=juan.id, id_tarjeta=tarjeta_juan.id))
    db.session.add(ClienteTarjeta(id_cliente=tomas.id, id_tarjeta=tarjeta_tomas.id))

    # =================================================================
    # 3. CLASES
    # =================================================================

    # Principales — usan HORA_PRINCIPAL
    clase_futbol_p  = Clase(dia=DIA, hora=HORA_PRINCIPAL, disciplina="futbol",  cupo=10, habilitada=True)
    clase_padel_p   = Clase(dia=DIA, hora=HORA_PRINCIPAL, disciplina="paddle",  cupo=10, habilitada=True)
    clase_voley_p   = Clase(dia=DIA, hora=HORA_PRINCIPAL, disciplina="voley",   cupo=10, habilitada=True)
    clase_basquet_p = Clase(dia=DIA, hora=HORA_PRINCIPAL, disciplina="basquet", cupo=10, habilitada=True)

    # Expiradas — usan HORA_EXPIRADA
    clase_futbol_exp = Clase(dia=DIA, hora=HORA_EXPIRADA, disciplina="futbol", cupo=10, habilitada=True)
    clase_padel_exp  = Clase(dia=DIA, hora=HORA_EXPIRADA, disciplina="paddle", cupo=10, habilitada=True)

    # Demasiado temprano — usa HORA_TEMPRANA
    clase_futbol_temp = Clase(dia=DIA, hora=HORA_TEMPRANA, disciplina="futbol", cupo=10, habilitada=True)

    # Suspensiones (Lunes, horarios fijos)
    clase_voley_lun  = Clase(dia="Lunes", hora="21:00", disciplina="voley",  cupo=10, habilitada=True)
    clase_futbol_lun = Clase(dia="Lunes", hora="22:00", disciplina="futbol", cupo=10, habilitada=True)

    db.session.add_all([
        clase_futbol_p, clase_padel_p, clase_voley_p, clase_basquet_p,
        clase_futbol_exp, clase_padel_exp, clase_futbol_temp,
        clase_voley_lun, clase_futbol_lun,
    ])
    db.session.flush()

    # =================================================================
    # 4. TURNOS
    # =================================================================
    turno_futbol_p  = Turno(habilitado=True, fecha=HOY, id_clase=clase_futbol_p.id)
    turno_padel_p   = Turno(habilitado=True, fecha=HOY, id_clase=clase_padel_p.id)
    turno_voley_p   = Turno(habilitado=True, fecha=HOY, id_clase=clase_voley_p.id)
    turno_basquet_p = Turno(habilitado=True, fecha=HOY, id_clase=clase_basquet_p.id)
    turno_futbol_exp  = Turno(habilitado=True, fecha=HOY, id_clase=clase_futbol_exp.id)
    turno_padel_exp   = Turno(habilitado=True, fecha=HOY, id_clase=clase_padel_exp.id)
    turno_futbol_temp = Turno(habilitado=True, fecha=HOY, id_clase=clase_futbol_temp.id)
    turno_voley_futuro = Turno(habilitado=True, fecha=HOY + timedelta(days=7), id_clase=clase_voley_p.id)

    db.session.add_all([
        turno_futbol_p, turno_padel_p, turno_voley_p, turno_basquet_p,
        turno_futbol_exp, turno_padel_exp, turno_futbol_temp,
        turno_voley_futuro,
    ])
    db.session.flush()

    # =================================================================
    # 5. RESERVAS DE JUAN
    # =================================================================

    # A) Fútbol — Pago (asist manual esc1 ok + QR no abonado ok)
    res_futbol = Reserva(id_cliente=juan.id, estado="Pago")
    db.session.add(res_futbol); db.session.flush()
    db.session.add(ReservaTurno(id_reserva=res_futbol.id, id_turno=turno_futbol_p.id))
    db.session.add(Abono(id_reserva=res_futbol.id, monto=Decimal("9000"), efectivo=True))

    # B) Padel — ReservaClase Pago (QR abonado ok)
    res_padel = Reserva(id_cliente=juan.id, estado="Pago")
    db.session.add(res_padel); db.session.flush()
    db.session.add(ReservaClase(id_reserva=res_padel.id, id_clase=clase_padel_p.id))
    db.session.add(Abono(id_reserva=res_padel.id, monto=Decimal("12000"), efectivo=False))
    db.session.add(AbonoTarjeta(id_abono=res_padel.id, id_tarjeta=tarjeta_juan.id))

    # C) Voley — Pago (QR no abonado "ya registrada" — pre-cargada)
    res_voley = Reserva(id_cliente=juan.id, estado="Pago")
    db.session.add(res_voley); db.session.flush()
    db.session.add(ReservaTurno(id_reserva=res_voley.id, id_turno=turno_voley_p.id))
    db.session.add(Abono(id_reserva=res_voley.id, monto=Decimal("8000"), efectivo=True))

    # D) Fútbol expirado — Pago (QR expirado)
    res_futbol_exp = Reserva(id_cliente=juan.id, estado="Pago")
    db.session.add(res_futbol_exp); db.session.flush()
    db.session.add(ReservaTurno(id_reserva=res_futbol_exp.id, id_turno=turno_futbol_exp.id))
    db.session.add(Abono(id_reserva=res_futbol_exp.id, monto=Decimal("9000"), efectivo=True))

    # E) Fútbol temprano — Pago (QR demasiado temprano)
    res_futbol_temp = Reserva(id_cliente=juan.id, estado="Pago")
    db.session.add(res_futbol_temp); db.session.flush()
    db.session.add(ReservaTurno(id_reserva=res_futbol_temp.id, id_turno=turno_futbol_temp.id))
    db.session.add(Abono(id_reserva=res_futbol_temp.id, monto=Decimal("9000"), efectivo=True))

    # F) Padel expirado — Pago (asist manual esc4 fuera de horario)
    res_padel_exp = Reserva(id_cliente=juan.id, estado="Pago")
    db.session.add(res_padel_exp); db.session.flush()
    db.session.add(ReservaTurno(id_reserva=res_padel_exp.id, id_turno=turno_padel_exp.id))
    db.session.add(Abono(id_reserva=res_padel_exp.id, monto=Decimal("12000"), efectivo=True))

    # =================================================================
    # 6. RESERVA DE SOFI EN BASQUET
    # Aprobada (50%) → asist manual esc3 "sin pago" + QR esc6 "pago incompleto"
    # Juan NO está en basquet → botón habilitado → esc6 reservar "ya tiene horario"
    # =================================================================
    res_sofi_basquet = Reserva(id_cliente=sofi.id, estado="Aprobada")
    db.session.add(res_sofi_basquet); db.session.flush()
    db.session.add(ReservaTurno(id_reserva=res_sofi_basquet.id, id_turno=turno_basquet_p.id))
    db.session.add(Abono(id_reserva=res_sofi_basquet.id, monto=Decimal("4250"), efectivo=True))

    # =================================================================
    # 7. PRE-REGISTRO ASISTENCIA VOLEY (QR esc7 "ya registrada")
    # =================================================================
    db.session.execute(
        cliente_asistio_turno.insert().values(
            id_cliente=juan.id, id_turno=turno_voley_p.id
        )
    )

    # =================================================================
    # 8. SUSPENSIONES
    # =================================================================
    db.session.add(ClienteSuspendido(
        id_cliente=sofi.id, id_clase=clase_voley_lun.id, monto=Decimal("5000.00"),
    ))
    db.session.add(ClienteSuspendido(
        id_cliente=tomas.id, id_clase=clase_futbol_lun.id, monto=Decimal("5000.00"),
    ))
    db.session.add(ClienteSuspendido(
        id_cliente=tomas.id, id_clase=clase_voley_lun.id, monto=Decimal("5000.00"),
    ))
    db.session.add(ClienteSuspendido(
        id_cliente=tomas.id, id_turno=turno_basquet_p.id, monto=Decimal("5000.00"),
    ))

    # =================================================================
    # 9. OFRECIMIENTO
    # =================================================================
    res_ofrecimiento = Reserva(id_cliente=juan.id, estado="Pendiente")
    db.session.add(res_ofrecimiento); db.session.flush()
    db.session.add(ReservaTurno(id_reserva=res_ofrecimiento.id, id_turno=turno_voley_futuro.id))
    db.session.add(Abono(id_reserva=res_ofrecimiento.id, monto=Decimal("8000"), efectivo=True))

    ofrecimiento = OfrecimientoReserva(
        id_cliente=tomas.id,
        cliente_emisor=juan.id,
        id_reserva=res_ofrecimiento.id,
        estado="Pendiente",
        fecha_vencimiento=datetime(2026, 7, 10, 23, 59, 59),
    )
    db.session.add(ofrecimiento)
    db.session.commit()

    # =================================================================
    # 10. ENVIAR QR POR MAIL
    # =================================================================
    print("\nEnviando QRs...")

    qrs_turno = [
        ("QR Futbol ok (no abonado)",    res_futbol,    turno_futbol_p,   "futbol",  HORA_PRINCIPAL),
        ("QR Futbol expirado",           res_futbol_exp, turno_futbol_exp, "futbol",  HORA_EXPIRADA),
        ("QR Futbol temprano",           res_futbol_temp, turno_futbol_temp, "futbol", HORA_TEMPRANA),
        ("QR Voley (ya registrada)",     res_voley,     turno_voley_p,    "voley",   HORA_PRINCIPAL),
    ]
    for nombre, reserva, turno, disc, hora in qrs_turno:
        try:
            enviar_comprobante_qr_turno(juan.id, reserva.id, turno.id, disc, str(turno.fecha), hora)
            print(f"  {nombre} — enviado")
        except Exception as e:
            print(f"  {nombre} — error: {e}")

    try:
        enviar_comprobantes_qr_clase(juan.id, res_padel.id, "paddle", HORA_PRINCIPAL, [turno_padel_p])
        print("  QR Padel abonado ok — enviado")
    except Exception as e:
        print(f"  QR Padel abonado — error: {e}")

    try:
        enviar_comprobante_qr_turno(sofi.id, res_sofi_basquet.id, turno_basquet_p.id, "basquet", str(HOY), HORA_PRINCIPAL)
        print("  QR Basquet pago incompleto (sofi) — enviado")
    except Exception as e:
        print(f"  QR Basquet (sofi) — error: {e}")

    # =================================================================
    # 11. MAIL DE OFRECIMIENTO
    # =================================================================
    print("\nEnviando mail de ofrecimiento...")
    try:
        send_ofrecimiento_turno_mail(ofrecimiento, tomas.id, turno_voley_futuro.id, juan.id)
        print("  Mail de ofrecimiento — enviado")
    except Exception as e:
        print(f"  Error: {e}")

    # =================================================================
    # RESUMEN
    # =================================================================
    h = int(HORA_PRINCIPAL.split(":")[0])
    ventana = f"{h-1:02d}:00–{h+1:02d}:00"

    print(f"""
{'='*70}
  TEST — {DIA} {HOY} — ventana {ventana}  (HORA_PRINCIPAL={HORA_PRINCIPAL})
{'='*70}

  Password universal: prueba123

  OFRECIMIENTO:
    http://localhost:5173/ofrecer/aceptar/{ofrecimiento.id}/{tomas.id}

  PARTE 1 — CLIENTE
  ---------------------------------------------------------
  Login 1: juanmanuelperezz468@gmail.com
    - Perfil con tarjeta *1234
    - Actualizar tarjeta (6 escenarios)
    - Historial pagos
    - Reservar Basquet {HORA_PRINCIPAL} → ya tiene turno en ese horario (Fútbol)
    - Abonar  Basquet {HORA_PRINCIPAL} → ya posee abono en mismo día y horario (Padel)

  Login 2: sofimendez@gmail.com
    - Perfil sin tarjeta
    - Historial pagos (pago parcial basquet)
    - Anular susp: Voley Lunes 21:00 → sin tarjetas

  Login 3: rivastoma0@gmail.com
    - Aceptar ofrecimiento (link en mail juanmanuelperezz468) → suspendido
    - Reservar Basquet {HORA_PRINCIPAL} → suspendido por turno
    - Abonar  Voley    {HORA_PRINCIPAL} → suspendido en disciplina
    - Anular susp: Fútbol Lun 22:00   → exitoso
    - Anular susp: Voley  Lun 21:00   → error (hardcoded)

  PARTE 2 — EMPLEADO
  ---------------------------------------------------------
  Login: recepcion360@gmail.com

  Pago efectivo suspensión:
    esc1: sofi          → ok
    esc2: carlos        → sin deudas
    esc3: noexiste@...  → no existe

  Asistencia manual:
    esc1: juan  + Fútbol  {HORA_PRINCIPAL}  → ok
    esc2: juan  + Basquet {HORA_PRINCIPAL}  → no inscripto
    esc3: sofi  + Basquet {HORA_PRINCIPAL}  → sin pago
    esc4: juan  + Padel   {HORA_EXPIRADA}   → fuera de horario
    esc5: repetir esc1                      → ya registrada

  QR (escanear en orden):
    esc1: Fútbol {HORA_PRINCIPAL}  (juan, no abonado)  → ok
    esc2: Padel  {HORA_PRINCIPAL}  (juan, abonado)     → ok
    esc3: QR inválido propio                           → inválido
    esc4: Fútbol {HORA_EXPIRADA}   (juan)              → expirado
    esc5: Fútbol {HORA_TEMPRANA}   (juan)              → demasiado temprano
    esc6: Basquet {HORA_PRINCIPAL} (sofi)              → pago incompleto
    esc7: Voley  {HORA_PRINCIPAL}  (juan, ya reg.)     → ya registrada

  NOTA: HORA_TEMPRANA={HORA_TEMPRANA} es válida hasta las {h:02d}:59
{'='*70}
""")


def main():
    with app.app_context():
        limpiar_bd()
        poblar()
        print("BD lista.")


if __name__ == "__main__":
    main()
