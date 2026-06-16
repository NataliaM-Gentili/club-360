"""
Script de datos de prueba para la tabla credito.
Ejecutar desde la raíz del proyecto backend:
    python seed_creditos.py

Crea un usuario cliente de prueba (si no existe) y le asigna créditos
en distintas disciplinas.
"""

from app import create_app, db
from app.models.db_structure import Usuario, Cliente, Credito
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():

    # --- 1. Usuario cliente de prueba ---
    email_prueba = "cliente_prueba@club360.com"
    usuario = Usuario.query.filter_by(email=email_prueba).first()

    if not usuario:
        usuario = Usuario(
            email=email_prueba,
            dni="99999999",
            nombres="Cliente",
            apellido="Prueba",
            contrasena=generate_password_hash("prueba123"),
            rol_id=1,  # cliente
        )
        db.session.add(usuario)
        db.session.flush()  # para obtener el id antes del commit

        cliente = Cliente(id_usuario=usuario.id)
        db.session.add(cliente)
        print(f"✅ Usuario creado: {email_prueba} (id={usuario.id})")
    else:
        print(f"ℹ️  Usuario ya existe: {email_prueba} (id={usuario.id})")

    # --- 2. Créditos de prueba ---
    creditos_a_insertar = [
        ("paddle", 3),
        ("voley", 2),
        ("futbol", 4),
        ("basquet", 1),
    ]

    for disciplina, cantidad in creditos_a_insertar:
        for _ in range(cantidad):
            db.session.add(
                Credito(
                    disciplina=disciplina,
                    id_usuario=usuario.id,
                    activo=True,
                )
            )
        print(f"   + {cantidad} crédito(s) de {disciplina}")

    db.session.commit()
    print("\n✅ Datos de prueba insertados correctamente.")
    print(f"   Email:      {email_prueba}")
    print(f"   Contraseña: prueba123")
