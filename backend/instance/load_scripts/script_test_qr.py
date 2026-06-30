"""
Script para testear: Registro de ingreso por QR (abonado y no abonado)
Escenarios:
  1. Clase suelta exitosa (ReservaTurno, Pago)
  2. Clase abonada exitosa (ReservaClase, Pago)
  3. QR inválido (manual - QR de otra plataforma)
  4. QR expirado (turno a las 08:00, se escanea después)
  5. Escaneo temprano (turno a las 15:00, se escanea antes)
  6. Falta de pago clase suelta (50% pagado)
  7. QR ya utilizado (escanear esc 1 dos veces)

Ejecutar desde backend/:
    python instance/load_scripts/script_test_qr.py
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
from app.services.email_services import enviar_comprobante_qr_turno, enviar_comprobantes_qr_clase
from datetime import date
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
    hoy = date.today()
    dia_semana_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    dia_hoy = dia_semana_es[hoy.weekday()]
    password = generate_password_hash("prueba123")

    # =====================================================================
    # 1. USUARIOS
    # =====================================================================
    empleado = Usuario(
        email="recepcion360@gmail.com", dni="10000002",
        nombres="Enzo", apellido="Fernandez", contrasena=password, rol_id=3,
    )
    cliente = Usuario(
        email="enzogelp483@gmail.com", dni="10000003",
        nombres="Enzo", apellido="Gelp", contrasena=password, rol_id=1,
    )

    db.session.add_all([empleado, cliente])
    db.session.flush()

    db.session.add(Empleado(id_usuario=empleado.id))
    db.session.add(Cliente(id_usuario=cliente.id))
    db.session.flush()

    # =====================================================================
    # 2. CLASES Y TURNOS
    # =====================================================================

    # Esc 1+7: Voley suelta exitosa (11:00 - ventana 10:00 a 12:00)
    clase_voley = Clase(
        dia=dia_hoy, hora="11:00", disciplina="voley", cupo=10, habilitada=True,
    )
    # Esc 2: Padel abonada exitosa (11:00 - ventana 10:00 a 12:00)
    clase_padel = Clase(
        dia=dia_hoy, hora="11:00", disciplina="paddle", cupo=10, habilitada=True,
    )
    # Esc 4: QR expirado (08:00 - ventana 07:00 a 09:00, a las 11:00 ya expiró)
    clase_futbol_exp = Clase(
        dia=dia_hoy, hora="08:00", disciplina="futbol", cupo=10, habilitada=True,
    )
    # Esc 5: Escaneo temprano (15:00 - ventana 14:00 a 16:00, a las 11:00 es muy temprano)
    clase_futbol_temp = Clase(
        dia=dia_hoy, hora="15:00", disciplina="futbol", cupo=10, habilitada=True,
    )
    # Esc 6: Falta de pago (11:00 - dentro de ventana, muestra error de pago)
    clase_basquet = Clase(
        dia=dia_hoy, hora="11:00", disciplina="basquet", cupo=10, habilitada=True,
    )

    db.session.add_all([clase_voley, clase_padel, clase_futbol_exp, clase_futbol_temp, clase_basquet])
    db.session.flush()

    turno_voley = Turno(habilitado=True, fecha=hoy, id_clase=clase_voley.id)
    turno_padel = Turno(habilitado=True, fecha=hoy, id_clase=clase_padel.id)
    turno_futbol_exp = Turno(habilitado=True, fecha=hoy, id_clase=clase_futbol_exp.id)
    turno_futbol_temp = Turno(habilitado=True, fecha=hoy, id_clase=clase_futbol_temp.id)
    turno_basquet = Turno(habilitado=True, fecha=hoy, id_clase=clase_basquet.id)

    db.session.add_all([turno_voley, turno_padel, turno_futbol_exp, turno_futbol_temp, turno_basquet])
    db.session.flush()

    # =====================================================================
    # 3. RESERVAS
    # =====================================================================

    # Esc 1+7: Voley turno suelto, 100% pago
    res_voley = Reserva(id_cliente=cliente.id, estado="Pago")
    db.session.add(res_voley)
    db.session.flush()
    db.session.add(ReservaTurno(id_reserva=res_voley.id, id_turno=turno_voley.id))
    db.session.add(Abono(id_reserva=res_voley.id, monto=Decimal("8000"), efectivo=True))

    # Esc 2: Padel clase abonada, 100% pago
    res_padel = Reserva(id_cliente=cliente.id, estado="Pago")
    db.session.add(res_padel)
    db.session.flush()
    db.session.add(ReservaClase(id_reserva=res_padel.id, id_clase=clase_padel.id))
    db.session.add(Abono(id_reserva=res_padel.id, monto=Decimal("12000"), efectivo=True))

    # Esc 4: Futbol expirado, 100% pago (turno a las 08:00)
    res_futbol_exp = Reserva(id_cliente=cliente.id, estado="Pago")
    db.session.add(res_futbol_exp)
    db.session.flush()
    db.session.add(ReservaTurno(id_reserva=res_futbol_exp.id, id_turno=turno_futbol_exp.id))
    db.session.add(Abono(id_reserva=res_futbol_exp.id, monto=Decimal("9000"), efectivo=True))

    # Esc 5: Futbol temprano, 100% pago (turno a las 15:00)
    res_futbol_temp = Reserva(id_cliente=cliente.id, estado="Pago")
    db.session.add(res_futbol_temp)
    db.session.flush()
    db.session.add(ReservaTurno(id_reserva=res_futbol_temp.id, id_turno=turno_futbol_temp.id))
    db.session.add(Abono(id_reserva=res_futbol_temp.id, monto=Decimal("9000"), efectivo=True))

    # Esc 6: Basquet turno suelto, solo 50% pagado
    res_basquet = Reserva(id_cliente=cliente.id, estado="Aprobada")
    db.session.add(res_basquet)
    db.session.flush()
    db.session.add(ReservaTurno(id_reserva=res_basquet.id, id_turno=turno_basquet.id))
    db.session.add(Abono(id_reserva=res_basquet.id, monto=Decimal("4250"), efectivo=True))

    db.session.commit()

    # =====================================================================
    # 4. ENVIAR QR POR MAIL
    # =====================================================================
    print("")
    print("Enviando QRs a enzogelp483@gmail.com...")

    # QR turno suelto (voley, futbol exp, futbol temp, basquet)
    turnos_qr = [
        ("Esc 1+7 Voley 11:00", res_voley, turno_voley, "voley"),
        ("Esc 4 Futbol expirado 08:00", res_futbol_exp, turno_futbol_exp, "futbol"),
        ("Esc 5 Futbol temprano 15:00", res_futbol_temp, turno_futbol_temp, "futbol"),
        ("Esc 6 Basquet sin pago 11:00", res_basquet, turno_basquet, "basquet"),
    ]

    for nombre, reserva, turno, disciplina in turnos_qr:
        try:
            enviar_comprobante_qr_turno(
                id_cliente=cliente.id,
                id_reserva=reserva.id,
                id_turno=turno.id,
                disciplina=disciplina,
                fecha=str(hoy),
                hora=nombre,
            )
            print(f"  {nombre} - enviado")
        except Exception as e:
            print(f"  {nombre} - error: {e}")

    # QR abonado (padel)
    try:
        enviar_comprobantes_qr_clase(
            id_cliente=cliente.id,
            id_reserva=res_padel.id,
            disciplina="paddle",
            hora="11:00",
            turnos=[turno_padel],
        )
        print("  Esc 2 Padel abonado 11:00 - enviado")
    except Exception as e:
        print(f"  Esc 2 Padel abonado - error: {e}")

    # =====================================================================
    # RESUMEN
    # =====================================================================
    print("")
    print("=" * 60)
    print(f"  TEST QR - {hoy} ({dia_hoy}) - testear entre 10:00 y 12:00")
    print("=" * 60)
    print("")
    print("  Password: prueba123")
    print("  Empleado: recepcion360@gmail.com")
    print("  Cliente:  enzogelp483@gmail.com")
    print("")
    print("  QR DATA:")
    print(f"    Esc 1+7 Voley suelta (Pago):       id_cliente:{cliente.id}|id_turno:{turno_voley.id}|id_reserva:{res_voley.id}")
    print(f"    Esc 2   Padel abonado (Pago):       id_cliente:{cliente.id}|id_turno:{turno_padel.id}|id_reserva:{res_padel.id}")
    print(f"    Esc 4   Futbol expirado (08:00):    id_cliente:{cliente.id}|id_turno:{turno_futbol_exp.id}|id_reserva:{res_futbol_exp.id}")
    print(f"    Esc 5   Futbol temprano (15:00):    id_cliente:{cliente.id}|id_turno:{turno_futbol_temp.id}|id_reserva:{res_futbol_temp.id}")
    print(f"    Esc 6   Basquet sin pago (50%):     id_cliente:{cliente.id}|id_turno:{turno_basquet.id}|id_reserva:{res_basquet.id}")
    print("")
    print("  ESCENARIOS:")
    print("    1. Escanear QR Voley 11:00       -> Registro de asistencia correcta")
    print("    2. Escanear QR Padel 11:00       -> Registro de asistencia correcta")
    print("    3. Escanear QR otra app          -> Lo sentimos, el qr escaneado es incorrecto...")
    print("    4. Escanear QR Futbol 08:00      -> Error: El QR asignado registrado expiró")
    print("    5. Escanear QR Futbol 15:00      -> Error: La clase asignada aun no ha comenzado")
    print("    6. Escanear QR Basquet 11:00     -> Error: Usted no ha pagado la totalidad del turno")
    print("    7. Escanear QR Voley de nuevo    -> Error: La asistencia ya fue registrada previamente")
    print("")
    print("  QRs enviados por mail a enzogelp483@gmail.com")
    print("=" * 60)


def main():
    with app.app_context():
        limpiar_bd()
        poblar()
        print("BD lista para testear QR.")


if __name__ == "__main__":
    main()
