import sqlite3

DB_PATH = "../database.db"

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()

USER_ID = 1

cards = [
    {
        "numero": "4111111111111111",
        "cvv": "123",
        "fecha_vencimiento": "2028-12-01",
        "titular": "User One"
    },
    {
        "numero": "5555555555554444",
        "cvv": "456",
        "fecha_vencimiento": "2027-06-01",
        "titular": "User One"
    }
]

for card in cards:
    # insert card
    cur.execute("""
        INSERT INTO tarjeta (numero, cvv, fecha_vencimiento, titular)
        VALUES (?, ?, ?, ?)
    """, (
        card["numero"],
        card["cvv"],
        card["fecha_vencimiento"],
        card["titular"]
    ))

    card_id = cur.lastrowid

    # link to user
    cur.execute("""
        INSERT INTO cliente_tarjeta (id_usuario, id_tarjeta)
        VALUES (?, ?)
    """, (USER_ID, card_id))

conn.commit()
conn.close()

print("2 cards inserted for user_id = 1")
