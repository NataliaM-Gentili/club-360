from flask import Blueprint, request, jsonify, session
from app.models.clase_model import ClaseModel
from app.models.db_structure import Clase, Turno, Reserva, ReservaTurno, ReservaClase, AbonadoTurnoCancelado
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

@clase_bp.route("/crear_clase", methods=["POST"])
def crear_clase():
    if session.get("rol_id") != ROL_ADMINISTRADOR:
        return jsonify({"error": "No autorizado"}), 403

    data = request.get_json()
    required_fields = ["dia", "hora", "disciplina", "cupo"]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Campo faltante: {field}"}), 400

    hora_nueva = datetime.strptime(data["hora"], "%H:%M")
    clases_misma_disciplina = Clase.query.filter_by(
        disciplina=data["disciplina"].lower(), dia=data["dia"]
    ).all()

    for clase in clases_misma_disciplina:
        hora_existente = datetime.strptime(clase.hora, "%H:%M")
        diferencia = abs((hora_nueva - hora_existente).total_seconds()) / 60
        if diferencia < 60:
            return (
                jsonify({"error": "Ya existe una clase de esa disciplina en ese horario. Debe haber al menos 1 hora de diferencia"}),
                409,
            )

    clase = ClaseModel.crear_clase(data)

    dia_semana = DIAS_SEMANA[data["dia"]]
    hoy = date.today()
    fin = hoy + timedelta(days=120)

    dia_actual = hoy
    while dia_actual.weekday() != dia_semana:
        dia_actual += timedelta(days=1)

    while dia_actual <= fin:
        if dia_actual not in FERIADOS_2026:
            turno = Turno(habilitado=True, fecha=dia_actual, id_clase=clase.id)
            db.session.add(turno)
        dia_actual += timedelta(weeks=1)

    db.session.commit()

    return jsonify({"message": "¡Clase creada con éxito!", "clase_id": clase.id}), 201


@clase_bp.route("/habilitarClase", methods=["POST"])
def habilitar_clase():
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
    if session.get('rol_id') != ROL_ADMINISTRADOR:
        return jsonify({"Error": "Acceso denegado. Se requiere rol de administrador."}), 403
    
    data = request.get_json()
    id_clase = data.get('id_clase')
    
    clase = Clase.query.get(id_clase)
    if not clase:
        return jsonify({"message": "Clase no encontrada."}), 404
    
    if not clase.habilitada:
        return jsonify({"message": "La clase ya está deshabilitada."}), 400
    
    clase.habilitada = False
    hoy = date.today()
    turnos_futuros = Turno.query.filter(
        Turno.id_clase == id_clase, 
        Turno.fecha >= hoy,
        Turno.habilitado == True
    ).all()
    
    turnos_cancelados = 0
    turnos_mantenidos = 0

    for turno in turnos_futuros:
        tiene_inscriptos = db.session.query(ReservaTurno).join(Reserva).filter(
            ReservaTurno.id_turno == turno.id,
            Reserva.estado != 'Cancelada'
        ).first() is not None

        if not tiene_inscriptos:
            turno.habilitado = False
            turnos_cancelados += 1
        else:
            turnos_mantenidos += 1

    db.session.commit()
    
    return jsonify({
        "message": f"Se cancelaron {turnos_cancelados} turnos vacíos.",
        "habilitada": False
    }), 200
    
@clase_bp.route('/turnos_de_cliente_clase', methods=['GET'])
def buscar_turnos_de_cliente_clase():
    id_usuario = request.args.get("id_usuario")

    if not id_usuario:
        return jsonify({"error": "Parámetro faltante: id_usuario"}), 400

    try:
        id_usuario = int(id_usuario)
    except ValueError:
        return jsonify({"error": "id_usuario inválido"}), 400

    reservas = Reserva.query.filter_by(id_cliente=id_usuario).all()

    if not reservas:
        return jsonify({"turnos": []}), 200

    ids_reservas = [r.id for r in reservas]

    reservas_clase = ReservaClase.query.filter(
        ReservaClase.id_reserva.in_(ids_reservas)
    ).all()

    ids_clases = [rc.id_clase for rc in reservas_clase]
    turnos = Turno.query.filter(Turno.id_clase.in_(ids_clases)).all()

    resultado = []
    for turno in turnos:
        clase = Clase.query.get(turno.id_clase)
        if not clase:
            continue
            
        # Si el abonado canceló este turno específico, no lo mostramos en sus turnos pendientes
        if AbonadoTurnoCancelado.query.filter_by(id_cliente=id_usuario, id_turno=turno.id).first() is not None:
            continue

        resultado.append({
            "id_turno": turno.id,
            "fecha": turno.fecha.strftime("%d/%m/%Y"),
            "disciplina": clase.disciplina,
            "dia": clase.dia,
            "hora": clase.hora,
            "cupo": clase.cupo,
            "habilitado": turno.habilitado,
        })

    return jsonify({"turnos": resultado}), 200


@clase_bp.route("/listar_clases", methods=["GET"])
def listar_clases():
    if session.get("rol_id") != ROL_ADMINISTRADOR:
        return jsonify({"error": "No autorizado"}), 403

    clases = Clase.query.all()
    resultado = []
    hoy = date.today()
    
    for c in clases:
        # 1. Contar reservas de abono mensual completo
        total_mensuales = ReservaClase.query.join(Reserva).filter(
            ReservaClase.id_clase == c.id,
            Reserva.estado != 'Cancelada'
        ).count()
        
        # 2. Contar TODAS las reservas de turnos individuales a futuro
        total_sueltos = db.session.query(ReservaTurno).join(Reserva).join(Turno).filter(
            Turno.id_clase == c.id,
            Turno.fecha >= hoy,
            Reserva.estado != 'Cancelada'
        ).count()
        
        # 3. Le restamos a la clase global las excepciones que se hayan hecho a futuro
        excepciones_futuras = AbonadoTurnoCancelado.query.join(Turno).filter(
            Turno.id_clase == c.id,
            Turno.fecha >= hoy
        ).count()

        total_inscriptos = (total_mensuales - excepciones_futuras) + total_sueltos

        # Contamos cuántos turnos a futuro tiene activos esta clase
        turnos_futuros_count = Turno.query.filter(
            Turno.id_clase == c.id, 
            Turno.fecha >= hoy,
            Turno.habilitado == True
        ).count()
        
        # AJUSTE: Si no hay turnos, cupo y ocupados son 0
        cupo_total_futuro = c.cupo * turnos_futuros_count if turnos_futuros_count > 0 else 0
        ocupados_reales = total_inscriptos if turnos_futuros_count > 0 else 0

        resultado.append({
            "id": c.id,
            "disciplina": c.disciplina,
            "dia": c.dia,
            "hora": c.hora,
            "cupo_clase": c.cupo,          # Cupo asignado al crear la clase
            "inscriptos": ocupados_reales, # Cantidad de inscriptos
            "cupo_total": cupo_total_futuro, # Total capacidad de turnos activos
            "habilitada": c.habilitada
        })
    return jsonify({"clases": resultado}), 200