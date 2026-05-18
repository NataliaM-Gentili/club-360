from flask import Blueprint, request, jsonify, session
from app.models.clase_model import ClaseModel
from app.models.db_structure import Clase, Turno, Reserva, ReservaTurno
from datetime import datetime, date, timedelta
from app import db

clase_bp = Blueprint("clase_bp", __name__)

ROL_ADMINISTRADOR = 2

FERIADOS_2026 = {
    date(2026, 1, 1),  # Año Nuevo
    date(2026, 2, 16),  # Carnaval
    date(2026, 2, 17),  # Carnaval
    date(2026, 3, 24),  # Día de la Memoria
    date(2026, 4, 2),  # Malvinas
    date(2026, 4, 3),  # Viernes Santo
    date(2026, 5, 1),  # Día del Trabajador
    date(2026, 5, 25),  # Revolución de Mayo
    date(2026, 6, 15),  # Güemes
    date(2026, 6, 20),  # Belgrano
    date(2026, 7, 9),  # Independencia
    date(2026, 8, 17),  # San Martín
    date(2026, 10, 12),  # Día de la Raza
    date(2026, 11, 20),  # Soberanía Nacional
    date(2026, 12, 8),  # Inmaculada Concepción
    date(2026, 12, 25),  # Navidad
}

DIAS_SEMANA = {
    "Lunes": 0,
    "Martes": 1,
    "Miércoles": 2,
    "Jueves": 3,
    "Viernes": 4,
    "Sábado": 5,
}


# /CREAR_CLASE --> ruta para crear una clase
@clase_bp.route("/crear_clase", methods=["POST"])
def crear_clase():

    # --- verificación de rol ---
    if session.get("rol_id") != ROL_ADMINISTRADOR:
        return jsonify({"error": "No autorizado"}), 403

    data = request.get_json()

    required_fields = ["dia", "hora", "disciplina", "cupo"]

    # --- check missing fields ---
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Campo faltante: {field}"}), 400

    # --- verificar conflicto de horario ---
    hora_nueva = datetime.strptime(data["hora"], "%H:%M")
    clases_misma_disciplina = Clase.query.filter_by(
        disciplina=data["disciplina"].lower(), dia=data["dia"]
    ).all()

    for clase in clases_misma_disciplina:
        hora_existente = datetime.strptime(clase.hora, "%H:%M")
        diferencia = abs((hora_nueva - hora_existente).total_seconds()) / 60

        if diferencia < 60:
            return (
                jsonify(
                    {
                        "error": "Ya existe una clase de esa disciplina en ese horario. Debe haber al menos 1 hora de diferencia"
                    }
                ),
                409,
            )

    # Llama al modelo para que ejecute el INSERT en la bd
    clase = ClaseModel.crear_clase(data)

    # --- crear turnos para los proximos 4 meses ---
    dia_semana = DIAS_SEMANA[data["dia"]]
    hoy = date.today()
    fin = hoy + timedelta(days=120)  # 4 meses aprox

    # buscar el primer día que coincida con el día de la clase
    dia_actual = hoy
    while dia_actual.weekday() != dia_semana:
        dia_actual += timedelta(days=1)

    # crear un turno por semana hasta 4 meses
    while dia_actual <= fin:
        if dia_actual not in FERIADOS_2026:
            turno = Turno(habilitado=True, fecha=dia_actual, id_clase=clase.id)
            db.session.add(turno)
        dia_actual += timedelta(weeks=1)

    db.session.commit()

    return jsonify({"message": "¡Clase creada con éxito!", "clase_id": clase.id}), 201



@clase_bp.route("/habilitarClase", methods=["POST"])
def habilitar_clase():
    
    # Verificación de rol
    if session.get('rol_id') != 2:
        return jsonify({"Error": "Acceso denegado. Se requiere rol de administrador."}), 403
    
    data = request.get_json()
    
    id_clase = data['id_clase']
    
    clase = ClaseModel.buscar_clase_por_id(id_clase)
    
    if not clase:
        return jsonify({"message": "Clase no encontrada."}), 404
    
    if clase.habilitada:
        return jsonify({"message": "La clase ya está habilitada."}), 400
    
    ClaseModel.habilitar_clase(clase)
    
    hoy = date.today()
    turnos_deshabilitados = Turno.query.filter(
        Turno.id_clase == id_clase,
        Turno.fecha >= hoy,
        Turno.habilitado == False
    ).all()

    for turno in turnos_deshabilitados:
        turno.habilitado = True
        
    db.session.commit()
    
    return jsonify({"message": "Clase habilitada con éxito."}), 200

@clase_bp.route("/deshabilitarClase", methods=["POST"])
def deshabilitar_clase():
    
    # 1. Verificación de rol
    if session.get('rol_id') != ROL_ADMINISTRADOR:
        return jsonify({"Error": "Acceso denegado. Se requiere rol de administrador."}), 403
    
    data = request.get_json()
    id_clase = data.get('id_clase')
    
    clase = Clase.query.get(id_clase)
    
    if not clase:
        return jsonify({"message": "Clase no encontrada."}), 404
    
    if not clase.habilitada:
        return jsonify({"message": "La clase ya está deshabilitada."}), 400
    
    # 2. Apagamos la clase general
    clase.habilitada = False
    
    # 3. Buscamos todos los turnos de esta clase a partir de hoy
    hoy = date.today()
    turnos_futuros = Turno.query.filter(
        Turno.id_clase == id_clase, 
        Turno.fecha >= hoy,
        Turno.habilitado == True
    ).all()
    
    turnos_cancelados = 0
    turnos_mantenidos = 0

    for turno in turnos_futuros:
        # Chequeamos si ESTE turno en particular tiene reservas activas
        tiene_inscriptos = db.session.query(ReservaTurno).join(Reserva).filter(
            ReservaTurno.id_turno == turno.id,
            Reserva.estado != 'Cancelada'
        ).first() is not None

        if not tiene_inscriptos:
            # Si el turno está vacío, lo damos de baja
            turno.habilitado = False
            turnos_cancelados += 1
        else:
            # Si tiene alumnos, lo dejamos intacto
            turnos_mantenidos += 1

    # Guardamos los cambios en la base de datos
    db.session.commit()
    
    # Devolvemos un resumen de lo que pasó para que el Front lo sepa
    return jsonify({
        "message": f"Clase deshabilitada. Se bajaron {turnos_cancelados} turnos vacíos y quedaron {turnos_mantenidos} vivos con alumnos.",
        "habilitada": False
    }), 200