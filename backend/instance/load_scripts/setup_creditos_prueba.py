import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app import create_app, db
from app.models.db_structure import Usuario, Credito

app = create_app()

with app.app_context():
    usuario = Usuario.query.filter_by(email="cliente_yoga_pendiente@test.com").first()
    if not usuario:
        print("ERROR: No se encontró cliente_yoga_pendiente@test.com")
    else:
        db.session.add(Credito(disciplina="futbol", id_usuario=usuario.id))
        db.session.add(Credito(disciplina="futbol", id_usuario=usuario.id))
        db.session.add(Credito(disciplina="padel", id_usuario=usuario.id))
        db.session.commit()
        print(f"Creditos creados para {usuario.email}: 2x futbol, 1x padel")
