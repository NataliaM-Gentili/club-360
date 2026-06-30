"""
Script de PRUEBA - 29/6/2026 18:00hs
Probar entre 17:00 y 19:00.

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
    hoy = date(2026, 6, 29)  # Lunes 29/6/2026
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
    lgomez = Usuario(
        email="lgomez.deuda@gmail.com", dni="10000004",
        nombres="Laura", apellido="Gomez", contrasena=password, rol_id=1,
    )
    tomas = Usuario(
        id=50,
        email="rivastoma0@gmail.com", dni="10000005",
        nombres="Tomas", apellido="Rivas", contrasena=password, rol_id=1,
    )
    sofi = Usuario(
        email="sofi.mendez.ok@gmail.com", dni="10000006",
        nombres="Sofia", apellido="Mendez", contrasena=password, rol_id=1,
    )

    db.session.add_all([admin, empleado, juan, lgomez, tomas, sofi])
    db.session.flush()

    db.session.add(Administrador(id_usuario=admin.id))
    db.session.add(Empleado(id_usuario=empleado.id))
    for u in [juan, lgomez, tomas, sofi]:
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

    # --- Turnos a las 18:00 (ventana 17:00-19:00) ---
    clase_futbol_18 = Clase(dia="Lunes", hora="18:00", disciplina="futbol", cupo=10, habilitada=True)
    clase_padel_18 = Clase(dia="Lunes", hora="18:00", disciplina="paddle", cupo=10, habilitada=True)
    clase_voley_18 = Clase(dia="Lunes", hora="18:00", disciplina="voley", cupo=10, habilitada=True)
    clase_basquet_18 = Clase(dia="Lunes", hora="18:00", disciplina="basquet", cupo=10, habilitada=True)

    # --- QR expirado (10:00) y temprano (23:00) ---
    clase_futbol_10 = Clase(dia="Lunes", hora="10:00", disciplina="futbol", cupo=10, habilitada=True)
    clase_futbol_23 = Clase(dia="Lunes", hora="23:00", disciplina="futbol", cupo=10, habilitada=True)

    # --- QR pago incompleto (segunda basquet) ---
    clase_basquet_18b = Clase(dia="Lunes", hora="18:00", disciplina="basquet", cupo=10, habilitada=True)

    # --- Asist manual fuera de horario ---
    clase_padel_10 = Clase(dia="Lunes", hora="10:00", disciplina="paddle", cupo=10, habilitada=True)

    # --- Clases para suspensiones ---
    clase_voley_lun = Clase(dia="Lunes", hora="19:00", disciplina="voley", cupo=10, habilitada=True)
    clase_futbol_lun = Clase(dia="Lunes", hora="22:00", disciplina="futbol", cupo=10, habilitada=True)

    db.session.add_all([
        clase_futbol_18, clase_padel_18, clase_voley_18, clase_basquet_18,
        clase_futbol_10, clase_futbol_23, clase_basquet_18b, clase_padel_10,
        clase_voley_lun, clase_futbol_lun,
    ])
    db.session.flush()

    # =================================================================
    # 4. TURNOS
    # =================================================================
    turno_futbol_18 = Turno(habilitado=True, fecha=hoy, id_clase=clase_futbol_18.id)
    turno_padel_18 = Turno(habilitado=True, fecha=hoy, id_clase=clase_padel_18.id)
    turno_voley_18 = Turno(habilitado=True, fecha=hoy, id_clase=clase_voley_18.id)
    turno_basquet_18 = Turno(habilitado=True, fecha=hoy, id_clase=clase_basquet_18.id)
    turno_futbol_10 = Turno(habilitado=True, fecha=hoy, id_clase=clase_futbol_10.id)
    turno_futbol_23 = Turno(habilitado=True, fecha=hoy, id_clase=clase_futbol_23.id)
    turno_basquet_b = Turno(habilitado=True, fecha=hoy, id_clase=clase_basquet_18b.id)
    turno_padel_10 = Turno(habilitado=True, fecha=hoy, id_clase=clase_padel_10.id)

    turno_voley_futuro = Turno(habilitado=True, fecha=hoy + timedelta(days=7), id_clase=clase_voley_18.id)

    db.session.add_all([
        turno_futbol_18, turno_padel_18, turno_voley_18, turno_basquet_18,
        turno_futbol_10, turno_futbol_23, turno_basquet_b, turno_padel_10,
        turno_voley_futuro,
    ])
    db.session.flush()

    # =================================================================
    # 5. RESERVAS DE JUAN
    # =================================================================

    # A) Fútbol 18:00 - Pago (asist manual esc 1+5)
    res_futbol = Reserva(id_cliente=juan.id, estado="Pago")
    db.session.add(res_futbol)
    db.session.flush()
    db.session.add(ReservaTurno(id_reserva=res_futbol.id, id_turno=turno_futbol_18.id))
    db.session.add(Abono(id_reserva=res_futbol.id, monto=Decimal("9000"), efectivo=True))

    # B) Padel 18:00 - ReservaClase Pago (QR abonado)
    res_padel = Reserva(id_cliente=juan.id, estado="Pago")
    db.session.add(res_padel)
    db.session.flush()
    db.session.add(ReservaClase(id_reserva=res_padel.id, id_clase=clase_padel_18.id))
    db.session.add(Abono(id_reserva=res_padel.id, monto=Decimal("12000"), efectivo=False))
    db.session.add(AbonoTarjeta(id_abono=res_padel.id, id_tarjeta=tarjeta_juan.id))

    # C) Voley 18:00 - Pago (QR no abonado)
    res_voley = Reserva(id_cliente=juan.id, estado="Pago")
    db.session.add(res_voley)
    db.session.flush()
    db.session.add(ReservaTurno(id_reserva=res_voley.id, id_turno=turno_voley_18.id))
    db.session.add(Abono(id_reserva=res_voley.id, monto=Decimal("8000"), efectivo=True))

    # D) Fútbol 10:00 - Pago (QR expirado + asist manual fuera horario)
    res_futbol_10 = Reserva(id_cliente=juan.id, estado="Pago")
    db.session.add(res_futbol_10)
    db.session.flush()
    db.session.add(ReservaTurno(id_reserva=res_futbol_10.id, id_turno=turno_futbol_10.id))
    db.session.add(Abono(id_reserva=res_futbol_10.id, monto=Decimal("9000"), efectivo=True))

    # E) Fútbol 23:00 - Pago (QR temprano)
    res_futbol_23 = Reserva(id_cliente=juan.id, estado="Pago")
    db.session.add(res_futbol_23)
    db.session.flush()
    db.session.add(ReservaTurno(id_reserva=res_futbol_23.id, id_turno=turno_futbol_23.id))
    db.session.add(Abono(id_reserva=res_futbol_23.id, monto=Decimal("9000"), efectivo=True))

    # F) Basquet B 18:00 - Aprobada 50% (QR pago incompleto)
    res_basquet_inc = Reserva(id_cliente=juan.id, estado="Aprobada")
    db.session.add(res_basquet_inc)
    db.session.flush()
    db.session.add(ReservaTurno(id_reserva=res_basquet_inc.id, id_turno=turno_basquet_b.id))
    db.session.add(Abono(id_reserva=res_basquet_inc.id, monto=Decimal("4250"), efectivo=True))

    # =================================================================
    # 6. RESERVAS DE SOFI (asist manual esc 3)
    # =================================================================
    res_sofi_basquet = Reserva(id_cliente=sofi.id, estado="Aprobada")
    db.session.add(res_sofi_basquet)
    db.session.flush()
    db.session.add(ReservaTurno(id_reserva=res_sofi_basquet.id, id_turno=turno_basquet_18.id))
    db.session.add(Abono(id_reserva=res_sofi_basquet.id, monto=Decimal("4250"), efectivo=True))

    # Juan inscripto en Padel 10:00 Pago (asist manual esc 4 fuera horario)
    res_padel_10 = Reserva(id_cliente=juan.id, estado="Pago")
    db.session.add(res_padel_10)
    db.session.flush()
    db.session.add(ReservaTurno(id_reserva=res_padel_10.id, id_turno=turno_padel_10.id))
    db.session.add(Abono(id_reserva=res_padel_10.id, monto=Decimal("12000"), efectivo=True))

    # =================================================================
    # 7. SUSPENSIONES
    # =================================================================
    susp_lgomez = ClienteSuspendido(
        id_cliente=lgomez.id, id_clase=clase_voley_lun.id, monto=Decimal("5000.00"),
    )
    susp_tomas_futbol = ClienteSuspendido(
        id_cliente=tomas.id, id_clase=clase_futbol_lun.id, monto=Decimal("5000.00"),
    )
    susp_tomas_voley = ClienteSuspendido(
        id_cliente=tomas.id, id_clase=clase_voley_lun.id, monto=Decimal("5000.00"),
    )
    susp_tomas_turno = ClienteSuspendido(
        id_cliente=tomas.id, id_turno=turno_basquet_18.id, monto=Decimal("5000.00"),
    )

    db.session.add_all([susp_lgomez, susp_tomas_futbol, susp_tomas_voley, susp_tomas_turno])

    # =================================================================
    # 8. OFRECIMIENTO DE TURNO LIBERADO
    # =================================================================
    res_ofrecimiento = Reserva(id_cliente=juan.id, estado="Pendiente")
    db.session.add(res_ofrecimiento)
    db.session.flush()
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
    # 9. ENVIAR QR POR MAIL
    # =================================================================
    print("")
    print("Enviando QRs...")

    qrs_turno = [
        ("QR Voley 18:00 (Pago)", res_voley, turno_voley_18, "voley", "18:00"),
        ("QR Futbol 10:00 (expirado)", res_futbol_10, turno_futbol_10, "futbol", "10:00"),
        ("QR Futbol 23:00 (temprano)", res_futbol_23, turno_futbol_23, "futbol", "23:00"),
        ("QR Basquet 18:00 (pago incompleto)", res_basquet_inc, turno_basquet_b, "basquet", "18:00"),
    ]
    for nombre, reserva, turno, disc, hora in qrs_turno:
        try:
            enviar_comprobante_qr_turno(juan.id, reserva.id, turno.id, disc, str(hoy), hora)
            print(f"  {nombre} - enviado")
        except Exception as e:
            print(f"  {nombre} - error: {e}")

    try:
        enviar_comprobantes_qr_clase(juan.id, res_padel.id, "paddle", "18:00", [turno_padel_18])
        print("  QR Padel 18:00 (abonado) - enviado")
    except Exception as e:
        print(f"  QR Padel 18:00 - error: {e}")

    # =================================================================
    # 10. ENVIAR MAIL DE OFRECIMIENTO
    # =================================================================
    print("")
    print("Enviando mail de ofrecimiento...")
    try:
        send_ofrecimiento_turno_mail(ofrecimiento, tomas.id, turno_voley_futuro.id, juan.id)
        print("  Mail de ofrecimiento enviado")
    except Exception as e:
        print(f"  Error: {e}")

    # =================================================================
    # RESUMEN
    # =================================================================
    print("")
    print("=" * 70)
    print("  TEST COMPLETO - Lunes 29/6/2026 - probar entre 17:00 y 19:00")
    print("=" * 70)
    print("")
    print("  Password universal: prueba123")
    print("")
    print("  OFRECIMIENTO:")
    print(f"    Link: http://localhost:5173/ofrecer/aceptar/{ofrecimiento.id}/{tomas.id}")
    print("")
    print("  FLUJO:")
    print("")
    print("  Login 1: juanmanuelperezz468@gmail.com")
    print("    - Perfil con tarjeta")
    print("    - Actualizar tarjeta (6 esc)")
    print("    - Historial pagos (3 pagos)")
    print("    - Reservar Basquet 18:00 -> ya tiene reserva en horario")
    print("")
    print("  Login 2: sofi.mendez.ok@gmail.com")
    print("    - Perfil sin tarjeta")
    print("    - Historial vacio")
    print("")
    print("  Login 3: rivastoma0@gmail.com")
    print("    - Aceptar ofrecimiento (mail/link) -> suspendido")
    print("    - Reservar turno -> suspendido por turno")
    print("    - Abonar voley -> suspendido en disciplina")
    print("    - Anular susp: Futbol Lun 22:00 -> exitoso")
    print("    - Anular susp: Voley Lun 19:00 -> error")
    print("")
    print("  Login 4: lgomez.deuda@gmail.com")
    print("    - Anular susp -> sin tarjetas")
    print("")
    print("  Login 5: recepcion360@gmail.com (empleado)")
    print("    - Pago efect: lgomez (ok), sofi (sin deudas), noexiste (no existe)")
    print("    - Asist manual: juan+Futbol18 (ok), juan+Basquet18 (no inscr),")
    print("      sofi+Basquet18 (sin pago), juan+Padel10 (fuera hora), repetir (ya reg)")
    print("    - QR: Voley (ok), Padel (abonado ok), basura (invalido),")
    print("      Futbol10 (expirado), Futbol23 (temprano), Basquet (sin pago),")
    print("      Voley de nuevo (ya registrada)")
    print("")
    print("=" * 70)


def main():
    with app.app_context():
        limpiar_bd()
        poblar()
        print("BD lista para probar.")


if __name__ == "__main__":
    main()
