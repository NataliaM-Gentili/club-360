import sqlite3
from datetime import date

DB_PATH = "backend/instance/database.db"

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()

# Clase futbol - Miercoles 19:00
cur.execute("""
    INSERT INTO clase (dia, hora, disciplina, cupo, habilitada)
    VALUES (?, ?, ?, ?, ?)
""", ("Miercoles", "19:00", "futbol", 10, 1))
id_clase_futbol = cur.lastrowid
print(f"Clase futbol creada → id={id_clase_futbol}")

# Turnos restantes de mayo (miercoles 20 y 27)
for fecha in ["2026-05-20", "2026-05-27"]:
    cur.execute("""
        INSERT INTO turno (fecha, id_clase, habilitado)
        VALUES (?, ?, ?)
    """, (fecha, id_clase_futbol, 1))
    print(f"  Turno {fecha} id={cur.lastrowid}")

conn.commit()
conn.close()
print("✓ Listo")