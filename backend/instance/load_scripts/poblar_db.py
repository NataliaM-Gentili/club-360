import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND_DIR))

from run import app 
from app import db
from app.models.db_structure import (
    Usuario, Administrador, Cliente, Clase, Turno, Reserva, ReservaTurno, Abono
)
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

def poblar_bd_demo():
    with app.app_context():
        # 1. LIMPIEZA
        db.session.query(ReservaTurno).delete()
        db.session.query(Reserva).delete()
        db.session.query(Turno).delete()
        db.session.query(Clase).delete()
        db.session.query(Abono).delete()
        db.session.commit()

        # 2. USUARIOS
        password_demo = generate_password_hash("1234567")
        admin = Usuario.query.filter_by(email="admin@club.com").first()
        cliente_sol = Usuario.query.filter_by(email="grassigiannasol@gmail.com").first()
        
        # CLIENTES NATI
        cliente_aaa = Usuario.query.filter_by(email="aaacliente@gmail.com").first()
        cliente_bbb = Usuario.query.filter_by(email="bbbcliente@gmail.com").first()

        # (Si no existen, los creamos)
        if not admin:
            admin = Usuario(email="admin@club.com", dni="1", nombres="Sol", apellido="Admin", contrasena=password_demo, rol_id=2)
            db.session.add(admin)
            db.session.flush()
            db.session.add(Administrador(id_usuario=admin.id))
        
        if not cliente_sol:
            cliente_sol = Usuario(email="grassigiannasol@gmail.com", dni="5", nombres="Sol", apellido="Grassi", contrasena=password_demo, rol_id=1)
            db.session.add(cliente_sol)
            db.session.flush()
            db.session.add(Cliente(id_usuario=cliente_sol.id))
        
        if not cliente_aaa: 
            cliente_aaa = Usuario(email="aaacliente@gmail.com", dni="88888888", nombres="Augusto", apellido="Triple A", contrasena=password_demo, rol_id=1) 
            db.session.add(cliente_aaa) 
            db.session.flush() 
            db.session.add(Cliente(id_usuario=cliente_aaa.id)) 

        if not cliente_bbb: 
            cliente_bbb = Usuario(email="bbbcliente@gmail.com", dni="99999999", nombres="Bruno", apellido="Triple B", contrasena=password_demo, rol_id=1) 
            db.session.add(cliente_bbb) 
            db.session.flush() 
            db.session.add(Cliente(id_usuario=cliente_bbb.id))   

        db.session.commit()

        # 3. CREACIÓN DE CLASES
        hoy = date.today()
        clases = [
            Clase(dia="Jueves", hora="10:00", disciplina="futbol", cupo=10, habilitada=True), # Futbol Jueves
            Clase(dia="Viernes", hora="10:00", disciplina="futbol", cupo=10, habilitada=True), # Futbol Viernes
            Clase(dia="Viernes", hora="10:00", disciplina="voley", cupo=10, habilitada=True),   # Voley
            Clase(dia="Viernes", hora="10:00", disciplina="paddle", cupo=10, habilitada=True), # Paddle Viernes
            Clase(dia="Jueves", hora="10:00", disciplina="paddle", cupo=10, habilitada=True),  # Paddle Jueves
            Clase(dia="Miércoles", hora="10:00", disciplina="basquet", cupo=10, habilitada=False), # Basquet
            Clase(dia="Jueves", hora="20:00", disciplina="paddle", cupo=4, habilitada=True), # [6] 
            Clase(dia="Jueves", hora="21:00", disciplina="paddle", cupo=4, habilitada=True), # [7] 
            Clase(dia="Lunes", hora="20:00", disciplina="paddle", cupo=4, habilitada=True), # [8] 
            Clase(dia="Lunes", hora="21:00", disciplina="paddle", cupo=4, habilitada=True) # [9]
        ]
        db.session.add_all(clases)
        db.session.flush()

        # 4. CREACIÓN DE TURNOS
        def get_fecha(dia_nombre):
            dias_map = {"Lunes":0, "Martes":1, "Miércoles":2, "Jueves":3, "Viernes":4}
            return hoy + timedelta(days=(dias_map[dia_nombre] - hoy.weekday() + 7) % 7)

        turnos = [
            Turno(habilitado=True, fecha=get_fecha("Jueves"), id_clase=clases[0].id),
            Turno(habilitado=True, fecha=get_fecha("Viernes"), id_clase=clases[1].id),
            Turno(habilitado=True, fecha=get_fecha("Viernes"), id_clase=clases[2].id),
            Turno(habilitado=True, fecha=get_fecha("Viernes"), id_clase=clases[3].id), # Paddle Viernes 1
            Turno(habilitado=True, fecha=get_fecha("Viernes") + timedelta(days=7), id_clase=clases[3].id), # Paddle Viernes 2
            Turno(habilitado=True, fecha=get_fecha("Jueves"), id_clase=clases[4].id), # Paddle Jueves
            Turno(habilitado=False, fecha=get_fecha("Miércoles"), id_clase=clases[5].id), # Basquet
            Turno(habilitado=True, fecha=get_fecha("Jueves"), id_clase=clases[6].id), # Jueves 20:00 
            Turno(habilitado=True, fecha=get_fecha("Jueves"), id_clase=clases[7].id), # Jueves 21:00 
            Turno(habilitado=True, fecha=get_fecha("Lunes"), id_clase=clases[8].id), # Lunes 20:00 
            Turno(habilitado=True, fecha=get_fecha("Lunes"), id_clase=clases[9].id) # Lunes 21:00
        ]
        db.session.add_all(turnos)
        db.session.flush()

        # 5. RESERVAS
        def crear_reserva(id_turno):
            r = Reserva(id_cliente=cliente_sol.id, estado="Aprobada")
            db.session.add(r)
            db.session.flush()
            db.session.add(ReservaTurno(id_reserva=r.id, id_turno=id_turno))
            db.session.add(Abono(id_reserva=r.id, monto=6000.00, efectivo=False))

        crear_reserva(turnos[1].id) # Futbol Viernes
        crear_reserva(turnos[3].id) # Paddle Viernes 1
        crear_reserva(turnos[5].id) # Paddle Jueves

        db.session.commit()
        print("✅ Demo sincronizada: Paddle Viernes 10am ahora tiene un inscripto.")

if __name__ == "__main__":
    poblar_bd_demo()
