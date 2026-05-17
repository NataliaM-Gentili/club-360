import sqlite3

DB_PATH = "../database.db"

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = OFF")  # easier cleanup
cur = conn.cursor()

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
    "administrador",
    "empleado",
    "cliente",
    "usuario",
    "turno",
    "clase",
    "tarjeta",
    "items"
]

for table in tables_to_clear:
    cur.execute(f"DELETE FROM {table}")

# reset auto-increment counters (optional but recommended for tests)
cur.execute("DELETE FROM sqlite_sequence")

conn.commit()
conn.close()

print("Database reset completed (roles and tipo_lista preserved).")
