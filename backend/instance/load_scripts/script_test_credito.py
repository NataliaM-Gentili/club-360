"""
Script de TEST — HU: Reservar turno con crédito
                     Listar turnos disponibles para reserva con crédito

Ejecutar desde backend/:
    python instance/load_scripts/script_test_credito.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from run import app
from app import db
from app.models.db_structure import (
    Usuario, Administrador, Empleado, Cliente,
    Clase, Turno, Reserva, ReservaTurno,
    Abono, ClienteSuspendido, Credito,
    cliente_asistio_turno,
)
from datetime import date, timedelta
from decimal import Decimal
from werkzeug.security import generate_password_hash


# =====================================================================
# CONFIGURACIÓN
# =====================================================================
HOY         = date(2026, 7, 1)
FECHA_TURNO = HOY + timedelta(days=6)   # 7/7/2026 — Martes, dentro del mes corriente
DIA_TURNO   = "Martes"
HORA_TURNO  = "20:00"
# =====================================================================


def limpiar_bd():
    print("Limpiando base de datos...")
    db.session.execute(cliente_asistio_turno.delete())
    db.session.query(ClienteSuspendido).delete()
    db.session.query(Credito).delete()
    db.session.query(Abono).delete()
    db.session.query(ReservaTurno).delete()
    db.session.query(Reserva).delete()
    db.session.query(Turno).delete()
    db.session.query(Clase).delete()
    db.session.query(Cliente).delete()
    db.session.query(Empleado).delete()
    db.session.query(Administrador).delete()
    db.session.query(Usuario).delete()
    db.session.commit()


def poblar():
    password = generate_password_hash("prueba123")

    # =================================================================
    # USUARIOS
    # =================================================================
    juan = Usuario(
        email="juanmanuelperezz468@gmail.com", dni="20000001",
        nombres="Juan Manuel", apellido="Perez", contrasena=password, rol_id=1,
    )
    suspendido_u = Usuario(
        email="suspendido@club.com", dni="20000002",
        nombres="Cliente", apellido="Suspendido", contrasena=password, rol_id=1,
    )
    otro = Usuario(
        email="otro@club.com", dni="20000003",
        nombres="Otro", apellido="Cliente", contrasena=password, rol_id=1,
    )
    db.session.add_all([juan, suspendido_u, otro])
    db.session.flush()
    for u in [juan, suspendido_u, otro]:
        db.session.add(Cliente(id_usuario=u.id))
    db.session.flush()

    # =================================================================
    # CLASES Y TURNOS
    # Todos en FECHA_TURNO (futuro) → pasan el filtro de 1 hora siempre
    # =================================================================

    # Futbol con cupo disponible → esc reserva 1 (exitosa) + listar esc 1
    clase_futbol = Clase(dia=DIA_TURNO, hora=HORA_TURNO, disciplina="futbol", cupo=10, habilitada=True)
    # Futbol lleno (cupo=1) → esc reserva 2 (cupo lleno)
    clase_futbol_llena = Clase(dia=DIA_TURNO, hora="21:00", disciplina="futbol", cupo=1, habilitada=True)
    # Futbol donde juan ya está inscripto → esc reserva 3 (ya inscripto)
    clase_futbol_inscripto = Clase(dia=DIA_TURNO, hora="19:00", disciplina="futbol", cupo=10, habilitada=True)
    # Sin clases de voley → listar esc 2 (listado vacío)
    
    clase_futbol_mie = Clase(dia="Miércoles", hora=HORA_TURNO, disciplina="futbol", cupo=10, habilitada=True)

    

    db.session.add_all([clase_futbol, clase_futbol_llena, clase_futbol_inscripto,clase_futbol_mie])
    db.session.flush()

    turno_exitoso   = Turno(habilitado=True, fecha=FECHA_TURNO, id_clase=clase_futbol.id)
    turno_lleno     = Turno(habilitado=True, fecha=FECHA_TURNO, id_clase=clase_futbol_llena.id)
    turno_inscripto = Turno(habilitado=True, fecha=FECHA_TURNO, id_clase=clase_futbol_inscripto.id)
    
    turno_exitoso_2  = Turno(habilitado=True, fecha=HOY + timedelta(days=13), id_clase=clase_futbol.id)          # 14/7
    turno_exitoso_3  = Turno(habilitado=True, fecha=HOY + timedelta(days=20), id_clase=clase_futbol.id)          # 21/7

    turno_mie = Turno(habilitado=True, fecha=HOY + timedelta(days=7), id_clase=clase_futbol_mie.id)  # 8/7/2026

    
    db.session.add_all([turno_exitoso, turno_lleno, turno_inscripto, turno_exitoso_2, turno_exitoso_3, turno_mie])
    db.session.flush()

    # =================================================================
    # RESERVAS
    # =================================================================

    # "otro" ocupa el único cupo de turno_lleno → esc2
    res_otro = Reserva(id_cliente=otro.id, estado="Pago")
    db.session.add(res_otro); db.session.flush()
    db.session.add(ReservaTurno(id_reserva=res_otro.id, id_turno=turno_lleno.id))
    db.session.add(Abono(id_reserva=res_otro.id, monto=Decimal("9000"), efectivo=True))

    # juan ya inscripto en turno_inscripto → esc3
    res_inscripto = Reserva(id_cliente=juan.id, estado="Pago")
    db.session.add(res_inscripto); db.session.flush()
    db.session.add(ReservaTurno(id_reserva=res_inscripto.id, id_turno=turno_inscripto.id))
    db.session.add(Abono(id_reserva=res_inscripto.id, monto=Decimal("9000"), efectivo=True))

    # =================================================================
    # CRÉDITOS
    # =================================================================

    # juan: futbol (para reservar) + voley (para listar turnos esc2 — sin turnos de voley)
    # juan: 1 crédito de futbol (se consume en esc1, luego esc5 queda sin crédito)
    db.session.add(Credito(id_usuario=juan.id, disciplina="futbol", activo=True))
    db.session.add(Credito(id_usuario=juan.id, disciplina="voley",  activo=True))


    # suspendido_u: tiene crédito de futbol pero está suspendido por turno → esc4
    db.session.add(Credito(id_usuario=suspendido_u.id, disciplina="futbol", activo=True))
    db.session.add(ClienteSuspendido(
        id_cliente=suspendido_u.id,
        id_turno=turno_exitoso.id,
        monto=Decimal("5000.00"),
    ))

    db.session.commit()

    # =================================================================
    # RESUMEN
    # =================================================================
    print(f"""
{'='*65}
  TEST CRÉDITO — turnos en {FECHA_TURNO} ({DIA_TURNO} {HORA_TURNO})
{'='*65}

  Password universal: prueba123

  LISTAR TURNOS PARA CRÉDITO
  --------------------------------------------------
  Login: juanmanuelperezz468@gmail.com → Mis Créditos
    esc1: crédito Futbol → "Solicitar clase con crédito"
          → muestra 3 turnos ({HORA_TURNO}, 21:00, 22:00)
    esc2: crédito Voley  → "Solicitar clase con crédito"
          → "No hay turnos disponibles para Voley"

  RESERVAR TURNO CON CRÉDITO
  --------------------------------------------------
  Login: juanmanuelperezz468@gmail.com → crédito Futbol → Solicitar
    esc2: Futbol 21:00  (cupo lleno)    → falla, crédito intacto
    esc3: Futbol 19:00         (ya inscripto)  → "Ya se encuentra inscripto en este turno"
    esc1: Futbol 20:00  (exitosa)       → ok, consume el crédito
    esc5: intentar reservar de nuevo    → "No posee créditos disponibles"


  Login: suspendido@club.com → crédito Futbol → Solicitar
    esc4: cualquier turno                      → "usted se encuentra suspendido"

{'='*65}
""")


def main():
    with app.app_context():
        limpiar_bd()
        poblar()
        print("BD lista para testear crédito.")


if __name__ == "__main__":
    main()
