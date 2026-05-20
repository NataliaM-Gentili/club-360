"""
Script para crear un usuario cliente de prueba con contraseña conocida.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app import create_app, db
from app.models.db_structure import Usuario, Cliente, Rol
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    email = "admin@gmail.com"

    # Verificar si ya existe
    if Usuario.query.filter_by(email=email).first():
        print(f"Ya existe un usuario con el email {email}")
    else:
        usuario = Usuario(
            email=email,
            dni="88883288",
            nombres="Carlos",
            apellido="Gomez",
            contrasena=generate_password_hash("prueba123"),
            rol_id=2,  # cliente
        )
        db.session.add(usuario)
        db.session.flush()

        cliente = Cliente(id_usuario=usuario.id)
        db.session.add(cliente)

        db.session.commit()
        print(f"Usuario creado exitosamente:")
        print(f"  Email:      {email}")
        print(f"  Contraseña: prueba123")
        print(f"  ID:         {usuario.id}")
        print(f"  Rol:        cliente (1)")
