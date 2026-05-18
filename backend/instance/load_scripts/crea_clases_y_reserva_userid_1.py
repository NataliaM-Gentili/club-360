# CREA LA CLASE VOLEY LOS LUNES 16:00 EN MAYO

# CREA LA RESERVA PARA UN TURNO 25 DE MAYO PARA EL USUARIO ID 2 CON ABONO PENDIENTE Y PRECIO 2000

import sqlite3
from datetime import datetime, date, timedelta

DB_PATH = "../database.db"

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()

ID_CLIENTE = 1
MONTO = 2000.00

# ---------------------------------------------------
# 1. Crear clases de voley todos los lunes de mayo 2026
# ---------------------------------------------------

def get_mondays_may_2026():
    year = 2026
    month = 5

    first_day = date(year, month, 1)
    days = []

    for i in range(31):
        d = first_day + timedelta(days=i)
        if d.month != month:
            break
        if d.weekday() == 0:  # Monday
            days.append(d)

    return days


clase_ids = []

for d in get_mondays_may_2026():
    cur.execute("""
        INSERT INTO clase (dia, hora, disciplina, cupo, habilitada)
        VALUES (?, ?, ?, ?, ?)
    """, (
        d.strftime("%Y-%m-%d"),
        "16:00",
        "Voley",
        10,
        1
    ))

    clase_ids.append(cur.lastrowid)


# ---------------------------------------------------
# 2. Crear turno específico: 25 mayo 2026
# ---------------------------------------------------

target_date = "2026-05-25"

# buscar clase de ese día
cur.execute("""
    SELECT id FROM clase WHERE dia = ?
""", (target_date,))

clase_row = cur.fetchone()

if not clase_row:
    raise Exception("No se encontró clase para 25/05/2026")

id_clase = clase_row[0]

cur.execute("""
    INSERT INTO turno (fecha, id_clase)
    VALUES (?, ?)
""", (target_date, id_clase))

id_turno = cur.lastrowid


# ---------------------------------------------------
# 3. Crear reserva (usuario 1)
# ---------------------------------------------------

cur.execute("""
    INSERT INTO reserva (fecha, id_cliente, estado)
    VALUES (?, ?, ?)
""", (
    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ID_CLIENTE,
    "Pendiente"
))

id_reserva = cur.lastrowid


# ---------------------------------------------------
# 4. Vincular reserva con turno 
# ---------------------------------------------------

cur.execute("""
    INSERT INTO reserva_turno (id_reserva, id_turno)
    VALUES (?, ?)
""", (id_reserva, id_turno))

# ---------------------------------------------------
# 5. Crear abono (NO EFECTIVO)
# ---------------------------------------------------

cur.execute("""
    INSERT INTO abono (id_reserva, monto, efectivo)
    VALUES (?, ?, ?)
""", (
    id_reserva,
    MONTO,
    0
))


conn.commit()
conn.close()

print("OK: Clase + Turno + Reserva + Abono creados correctamente")
print(f"Reserva ID: {id_reserva}, Turno ID: {id_turno}, Clase ID: {id_clase}")
