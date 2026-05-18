# LIMPIA BD PERO PRESERVA USUARIOS, ROLES Y TIPO_LISTA

import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "database.db"
)

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = OFF")
cur = conn.cursor()

# ----------------------------
# TABLAS QUE SE PUEDEN BORRAR
# (todo lo transaccional)
# ----------------------------
tables_to_clear = [
    "empleado_registra_abono",
    "abono_tarjeta",
    "abono",
    "reserva_clase",
    "reserva_turno",
    "reserva",
    "lista_espera",
    "cliente_asistio_turno",
    "cliente_tarjeta",
    "turno",
    "clase",
    "tarjeta",
    "items"
]

for t in tables_to_clear:
    cur.execute(f"DELETE FROM {t}")

conn.commit()
conn.close()

print("Database cleared successfully (users + roles preserved)")
