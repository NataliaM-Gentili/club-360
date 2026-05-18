import sqlite3
from datetime import datetime, date, timedelta

DB_PATH = "../database.db"

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()

ID_CLIENTE = 1

# ---------------------------------------------------
# FUNCIONES DE CALENDARIO
# ---------------------------------------------------

def get_mondays_may_2026():
    days = []
    for i in range(31):
        d = date(2026, 5, 1) + timedelta(days=i)
        if d.month != 5:
            break
        if d.weekday() == 0:
            days.append(d)
    return days


def get_wednesdays_may_2026():
    days = []
    for i in range(31):
        d = date(2026, 5, 1) + timedelta(days=i)
        if d.month != 5:
            break
        if d.weekday() == 2:
            days.append(d)
    return days


# ===================================================
# 1. CLASES (UNA POR DISCIPLINA)
# ===================================================

cur.execute("""
INSERT INTO clase (dia, hora, disciplina, cupo, habilitada)
VALUES (?, ?, ?, ?, ?)
""", ("2026-05-01", "16:00", "Voley", 10, 1))

id_clase_voley = cur.lastrowid


cur.execute("""
INSERT INTO clase (dia, hora, disciplina, cupo, habilitada)
VALUES (?, ?, ?, ?, ?)
""", ("2026-05-01", "18:00", "Padel", 10, 1))

id_clase_padel = cur.lastrowid


# ===================================================
# 2. TURNOS VOLEY (LUNES)
# ===================================================

voley_turnos = []

for d in get_mondays_may_2026():
    cur.execute("""
        INSERT INTO turno (fecha, id_clase)
        VALUES (?, ?)
    """, (d.strftime("%Y-%m-%d"), id_clase_voley))

    voley_turnos.append(cur.lastrowid)


# ===================================================
# 3. TURNOS PADEL (MIÉRCOLES)
# ===================================================

padel_turnos = []

for d in get_wednesdays_may_2026():
    cur.execute("""
        INSERT INTO turno (fecha, id_clase)
        VALUES (?, ?)
    """, (d.strftime("%Y-%m-%d"), id_clase_padel))

    padel_turnos.append(cur.lastrowid)


# ===================================================
# 4. RESERVA VOLEY (TURNO ESPECÍFICO 25/05)
# ===================================================

target_date = "2026-05-25"

cur.execute("""
SELECT id FROM turno WHERE fecha = ? AND id_clase = ?
""", (target_date, id_clase_voley))

id_turno_voley = cur.fetchone()[0]

cur.execute("""
INSERT INTO reserva (fecha, id_cliente, estado)
VALUES (?, ?, ?)
""", (datetime.now(), ID_CLIENTE, "Pendiente"))

reserva_voley_turno = cur.lastrowid

cur.execute("""
INSERT INTO reserva_turno (id_reserva, id_turno)
VALUES (?, ?)
""", (reserva_voley_turno, id_turno_voley))

cur.execute("""
INSERT INTO abono (id_reserva, monto, efectivo)
VALUES (?, ?, ?)
""", (reserva_voley_turno, 2000, 0))

# ===================================================
# 6. RESERVA PADEL MENSUAL
# ===================================================

precio_hora = 100
monto_padel = precio_hora * len(padel_turnos)

cur.execute("""
INSERT INTO reserva (fecha, id_cliente, estado)
VALUES (?, ?, ?)
""", (datetime.now(), ID_CLIENTE, "Pendiente"))

reserva_padel = cur.lastrowid

cur.execute("""
INSERT INTO reserva_clase (id_reserva, id_clase)
VALUES (?, ?)
""", (reserva_padel, id_clase_padel))

cur.execute("""
INSERT INTO abono (id_reserva, monto, efectivo)
VALUES (?, ?, ?)
""", (reserva_padel, monto_padel, 0))


conn.commit()
conn.close()
