"""
Datos de prueba para escenarios 6 y 7 de reservar turno / abonar mensual.

Escenario 6 (mismo horario):
  - Cliente tiene reserva de basquet para mañana 18:00hs
  - Existe turno de voley para mañana 18:00hs
  - Al intentar reservar voley -> "ya posee una reserva de turno en el horario elegido"
  Probar: Buscar Turnos -> voley + dia mañana + 18:00 -> Reservar

Escenario 7 (suspendido en disciplina):
  - Cliente tiene suspensión de clase de futbol
  - Existe clase de futbol con turnos
  - Al intentar Abonar (mensual) -> "usted se encuentra suspendido en la disciplina elegida"
  Probar: Buscar Turnos -> futbol + dia + hora -> Abonar (mensual)

Login: cliente_yoga_pendiente@test.com / prueba123

Ejecutar desde backend/: python instance/load_scripts/setup_escenarios_reserva_prueba.py
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from datetime import date, timedelta
from decimal import Decimal

from app import create_app, db
from app.models.db_structure import (
    Usuario, Cliente, Clase, Turno, Tarjeta, ClienteTarjeta,
    Reserva, ReservaTurno, Abono, ClienteSuspendido
)

app = create_app()

DIAS = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]

with app.app_context():
    hoy = date.today()
    manana = hoy + timedelta(days=1)
    dia_manana = DIAS[manana.weekday()]
    
    print("Inicio")

    usuario = Usuario.query.filter_by(email="cliente_yoga_pendiente@test.com").first()
    if not usuario:
        print("ERROR: No se encontro cliente_yoga_pendiente@test.com")
        exit()

    # ── TARJETA (necesaria para reservar turno suelto) ────────────────────
    tarjeta_existente = ClienteTarjeta.query.filter_by(id_cliente=usuario.id).first()
    if not tarjeta_existente:
        tarjeta = Tarjeta(
            numero="4111111111111111", cvv="123",
            fecha_vencimiento="12/2030", titular="Yoga Prueba",
        )
        db.session.add(tarjeta)
        db.session.flush()
        db.session.add(ClienteTarjeta(id_cliente=usuario.id, id_tarjeta=tarjeta.id))
        print("Tarjeta creada para el cliente")
    else:
        print("Cliente ya tiene tarjeta")

    # ══════════════════════════════════════════════════════════════════════
    # ESCENARIO 6: mismo horario
    # ══════════════════════════════════════════════════════════════════════

    # Turno de basquet mañana 18:00 -> YA RESERVADO por el cliente
    clase_basquet = Clase(dia=dia_manana, hora="18:00", disciplina="basquet", cupo=10, habilitada=True)
    db.session.add(clase_basquet)
    db.session.flush()
    turno_basquet = Turno(fecha=manana, id_clase=clase_basquet.id, habilitado=True)
    db.session.add(turno_basquet)
    db.session.flush()

    reserva = Reserva(id_cliente=usuario.id, estado="Pendiente")
    db.session.add(reserva)
    db.session.flush()
    db.session.add(ReservaTurno(id_reserva=reserva.id, id_turno=turno_basquet.id))
    db.session.add(Abono(id_reserva=reserva.id, monto=Decimal("4250"), efectivo=False))

    # Turno de voley mañana 18:00 -> MISMO HORARIO, para intentar reservar
    clase_voley = Clase(dia=dia_manana, hora="18:00", disciplina="voley", cupo=10, habilitada=True)
    db.session.add(clase_voley)
    db.session.flush()
    turno_voley = Turno(fecha=manana, id_clase=clase_voley.id, habilitado=True)
    db.session.add(turno_voley)
    db.session.flush()

    print(f"\nEscenario 6:")
    print(f"  Basquet {dia_manana} {manana} 18:00hs -> YA RESERVADO")
    print(f"  Voley   {dia_manana} {manana} 18:00hs -> intentar reservar este")

    # ══════════════════════════════════════════════════════════════════════
    # ESCENARIO 7: suspendido en disciplina
    # ══════════════════════════════════════════════════════════════════════

    # Clase de futbol con suspensión
    clase_futbol_susp = Clase(dia="Viernes", hora="10:00", disciplina="futbol", cupo=10, habilitada=True)
    db.session.add(clase_futbol_susp)
    db.session.flush()
    db.session.add(ClienteSuspendido(
        id_cliente=usuario.id, id_clase=clase_futbol_susp.id, monto=Decimal("5000"),
    ))

    # Otra clase de futbol para intentar abonarse
    clase_futbol_abonar = Clase(dia=dia_manana, hora="20:00", disciplina="futbol", cupo=10, habilitada=True)
    db.session.add(clase_futbol_abonar)
    db.session.flush()

    # Turnos para que aparezcan en Buscar Turnos
    for i in range(4):
        fecha_turno = manana + timedelta(weeks=i)
        turno_f = Turno(fecha=fecha_turno, id_clase=clase_futbol_abonar.id, habilitado=True)
        db.session.add(turno_f)

    db.session.commit()

    print(f"\nEscenario 7:")
    print(f"  Suspension en futbol (clase id={clase_futbol_susp.id})")
    print(f"  Intentar abonar futbol {dia_manana} 20:00hs -> debe fallar")

    print(f"\nPasos de prueba:")
    print(f"  Esc 6: Buscar Turnos -> voley / {dia_manana} / 18:00 -> Reservar")
    print(f"  Esc 7: Buscar Turnos -> futbol / {dia_manana} / 20:00 -> Abonar (mensual)")
