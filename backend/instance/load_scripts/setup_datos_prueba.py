"""
Script de datos de prueba para testear reservar_turno y abonar_mensual.
Crea clases, turnos y tarjeta para Carlos (id=4).

"""

import sqlite3
from datetime import date, timedelta

DB_PATH = "instance/database.db"

FERIADOS = {
    date(2026, 5, 1),
    date(2026, 5, 25),
}

ID_CARLOS = 4

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()


# ── helpers de calendario ──────────────────────────────────────────────────────

def get_dias_mes(anio, mes, weekday):
    """Retorna todas las fechas del mes con el día de semana dado (0=lunes...6=domingo)."""
    days = []
    d = date(anio, mes, 1)
    while d.month == mes:
        if d.weekday() == weekday:
            days.append(d)
        d += timedelta(days=1)
    return days


# ── 1. CLASES ──────────────────────────────────────────────────────────────────
# dia = nombre del día para que buscar_turnos() funcione correctamente

cur.execute("""
    INSERT INTO clase (dia, hora, disciplina, cupo, habilitada)
    VALUES (?, ?, ?, ?, ?)
""", ("Lunes", "16:00", "voley", 10, 1))
id_clase_voley = cur.lastrowid
print(f"Clase voley creada  → id={id_clase_voley}")

cur.execute("""
    INSERT INTO clase (dia, hora, disciplina, cupo, habilitada)
    VALUES (?, ?, ?, ?, ?)
""", ("Miercoles", "18:00", "padel", 10, 1))
id_clase_padel = cur.lastrowid
print(f"Clase padel creada  → id={id_clase_padel}")


# ── 2. TURNOS VOLEY (lunes de mayo 2026, sin feriados) ────────────────────────

lunes_mayo = get_dias_mes(2026, 5, 0)  # 0 = lunes
for d in lunes_mayo:
    habilitado = 0 if d in FERIADOS else 1
    cur.execute("""
        INSERT INTO turno (fecha, id_clase, habilitado)
        VALUES (?, ?, ?)
    """, (d.strftime("%Y-%m-%d"), id_clase_voley, habilitado))
    print(f"  Turno voley {d}  habilitado={habilitado}  id={cur.lastrowid}")


# ── 3. TURNOS PADEL (miércoles de mayo 2026, sin feriados) ────────────────────

miercoles_mayo = get_dias_mes(2026, 5, 2)  # 2 = miércoles
for d in miercoles_mayo:
    habilitado = 0 if d in FERIADOS else 1
    cur.execute("""
        INSERT INTO turno (fecha, id_clase, habilitado)
        VALUES (?, ?, ?)
    """, (d.strftime("%Y-%m-%d"), id_clase_padel, habilitado))
    print(f"  Turno padel {d}  habilitado={habilitado}  id={cur.lastrowid}")


# ── 4. TARJETA y asociación a Carlos (id=4) ───────────────────────────────────

cur.execute("""
    INSERT INTO tarjeta (numero, cvv, fecha_vencimiento, titular)
    VALUES (?, ?, ?, ?)
""", ("4111111111111111", "123", "12/2028", "Carlos Gomez"))
id_tarjeta = cur.lastrowid
print(f"\nTarjeta creada  → id={id_tarjeta}")

cur.execute("""
    INSERT INTO cliente_tarjeta (id_usuario, id_tarjeta)
    VALUES (?, ?)
""", (ID_CARLOS, id_tarjeta))
print(f"Tarjeta {id_tarjeta} asociada a Carlos (id={ID_CARLOS})")


conn.commit()
conn.close()
print("\n✓ Datos de prueba cargados correctamente.")
