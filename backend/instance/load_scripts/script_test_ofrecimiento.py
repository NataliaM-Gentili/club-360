"""
Script para probar SOLO: Aceptar turno liberado como cliente suspendido
Ejecutar desde backend/:
    python instance/load_scripts/script_test_ofrecimiento.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from run import app
from app import db
from app.models.db_structure import (
    Usuario, Empleado, Cliente,
    Clase, Turno, Reserva, ReservaTurno,
    Abono, ClienteSuspendido, OfrecimientoReserva,
    AbonadoTurnoCancelado, EmpleadoRegistraAbono, Credito,
    ListaEspera, AbonoTarjeta, ReservaClase, Tarjeta, ClienteTarjeta,
    Administrador, cliente_asistio_turno,
)
from app.services.email_services import send_ofrecimiento_turno_mail
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
    hoy = date(2026, 6, 29)
    password = generate_password_hash("prueba123")

    # Dos usuarios: uno que libera el turno, otro que lo recibe (suspendido)
    emisor = Usuario(
        email="juanmanuelperezz468@gmail.com", dni="10000001",
        nombres="Juan Manuel", apellido="Perez", contrasena=password, rol_id=1,
    )
    suspendido = Usuario(
        id=50,
        email="rivastoma0@gmail.com", dni="10000002",
        nombres="Tomas", apellido="Rivas", contrasena=password, rol_id=1,
    )

    db.session.add_all([emisor, suspendido])
    db.session.flush()
    db.session.add(Cliente(id_usuario=emisor.id))
    db.session.add(Cliente(id_usuario=suspendido.id))
    db.session.flush()

    print(f"  ID emisor (juan): {emisor.id}")
    print(f"  ID suspendido (tomas): {suspendido.id}")

    # Clase y turno futuro para el ofrecimiento
    clase_voley = Clase(dia="Lunes", hora="17:00", disciplina="voley", cupo=10, habilitada=True)
    db.session.add(clase_voley)
    db.session.flush()

    turno_futuro = Turno(habilitado=True, fecha=hoy + timedelta(days=7), id_clase=clase_voley.id)
    # Turno extra para la suspensión por turno
    turno_susp = Turno(habilitado=True, fecha=hoy, id_clase=clase_voley.id)
    db.session.add_all([turno_futuro, turno_susp])
    db.session.flush()

    # Reserva "reciclada" (simula turno liberado)
    reserva = Reserva(id_cliente=emisor.id, estado="Pendiente")
    db.session.add(reserva)
    db.session.flush()
    db.session.add(ReservaTurno(id_reserva=reserva.id, id_turno=turno_futuro.id))
    db.session.add(Abono(id_reserva=reserva.id, monto=Decimal("8000"), efectivo=True))

    # Suspensión de tomas por TURNO (id_turno IS NOT NULL)
    suspension = ClienteSuspendido(
        id_cliente=suspendido.id, id_turno=turno_susp.id, monto=Decimal("5000.00"),
    )
    db.session.add(suspension)

    # Ofrecimiento para tomas
    ofrecimiento = OfrecimientoReserva(
        id_cliente=suspendido.id,
        cliente_emisor=emisor.id,
        id_reserva=reserva.id,
        estado="Pendiente",
        fecha_vencimiento=datetime(2026, 7, 15, 23, 59, 59),
    )
    db.session.add(ofrecimiento)
    db.session.commit()

    # Verificar datos
    susp_check = ClienteSuspendido.query.filter(
        ClienteSuspendido.id_cliente == 50,
        ClienteSuspendido.id_turno.isnot(None)
    ).first()
    print(f"  Suspension encontrada: {susp_check is not None}")
    if susp_check:
        print(f"    id_cliente={susp_check.id_cliente}, id_turno={susp_check.id_turno}")

    # Enviar mail
    print("")
    print("Enviando mail de ofrecimiento...")
    try:
        send_ofrecimiento_turno_mail(ofrecimiento, suspendido.id, turno_futuro.id, emisor.id)
        print("  Mail enviado (llega a juanmanuelperezz468@gmail.com)")
    except Exception as e:
        print(f"  Error: {e}")

    print("")
    print("=" * 60)
    print("  TEST OFRECIMIENTO - Cliente suspendido")
    print("=" * 60)
    print("")
    print(f"  Link: http://localhost:5173/ofrecer/aceptar/{ofrecimiento.id}/{suspendido.id}")
    print("")
    print("  PASOS:")
    print("  1. Abrir el link de arriba en el navegador")
    print("  2. Deberia mostrar: 'Se encuentra suspendido para turnos sueltos'")
    print("  3. Redirige al login")
    print("")
    print(f"  DEBUG:")
    print(f"    ofrecimiento.id = {ofrecimiento.id}")
    print(f"    id_cliente_elegido = {suspendido.id} (debe ser 50)")
    print(f"    suspension.id_turno = {susp_check.id_turno if susp_check else 'NO ENCONTRADA'}")
    print("")
    print("=" * 60)


def main():
    with app.app_context():
        limpiar_bd()
        poblar()
        print("BD lista.")


if __name__ == "__main__":
    main()
