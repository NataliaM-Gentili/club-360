from flask import Blueprint, jsonify, session, request
from app.models.turno_model import TurnoModel
from app.models.db_structure import ReservaTurno, Turno, Clase
from datetime import date

turno_bp = Blueprint("turno_bp", __name__)


@turno_bp.route("/visualizar_turnos", methods=["GET"])
def get_turnos_admin():
    if session.get("rol_id") != 2:
        return (
            jsonify({"error": "Acceso denegado. Se requiere rol de administrador"}),
            403,
        )

    turnos_data = TurnoModel.get_all_turnos_vigentes()

    if not turnos_data:
        return jsonify({"mensaje": "No hay turnos disponibles para mostrar"}), 200

    resultado = []
    for turno, clase, ocupados in turnos_data:
        resultado.append(
            {
                "id_turno": turno.id,
                "actividad": clase.disciplina,
                "dia": clase.dia,
                "horario": clase.hora,
                "cupo_ocupado": ocupados,
                "cupo_total": clase.cupo,
                "fecha_turno": turno.fecha.strftime("%Y-%m-%d"),
                "opciones": ["cancelar turno", "cancelar clase"],
            }
        )

    return jsonify(resultado), 200


# /BUSCAR_TURNOS --> lista turnos del mes corriente filtrados por disciplina, dia y hora
@turno_bp.route("/buscar_turnos", methods=["GET"])
def buscar_turnos():
    disciplina = request.args.get("disciplina")
    dia = request.args.get("dia")
    hora = request.args.get("hora")

    for nombre, valor in {"disciplina": disciplina, "dia": dia, "hora": hora}.items():
        if not valor:
            return jsonify({"error": f"Parámetro faltante: {nombre}"}), 400

    clase = Clase.query.filter_by(
        disciplina=disciplina.lower(), dia=dia, hora=hora
    ).first()

    if not clase:
        return jsonify({"turnos": []}), 200

    hoy = date.today()
    #EN CASO DE QUERER FILTRAR TODO EL MES -> primer_dia_mes = date(hoy.year, hoy.month, 1)
    if hoy.month == 12:
        ultimo_dia_mes = date(hoy.year + 1, 1, 1)
    else:
        ultimo_dia_mes = date(hoy.year, hoy.month + 1, 1)

    rol_usuario = session.get("rol_id")
    es_admin_o_empleado = rol_usuario in [2, 3]

    query = Turno.query.filter(
        Turno.id_clase == clase.id,
        Turno.fecha >= hoy,
        Turno.fecha < ultimo_dia_mes,
    )

    # si es cleinte,filtro para ocultar los deshabilitados
    if not es_admin_o_empleado:
        query = query.filter(Turno.habilitado == True)

    turnos = query.order_by(Turno.fecha).all()

    resultado = []
    for t in turnos:
        ocupados = ReservaTurno.query.filter_by(id_turno=t.id).count()
        resultado.append(
            {
                "id": t.id,
                "fecha": t.fecha.strftime("%d/%m/%Y"),
                "disciplina": clase.disciplina,
                "dia": clase.dia,
                "hora": clase.hora,
                "cupo": clase.cupo,
                "ocupados": ocupados,
                "id_clase": clase.id,
                "habilitada": clase.habilitada,
            }
        )

    return jsonify({"turnos": resultado}), 200


@turno_bp.route('/turnos_de_cliente', methods=['GET'])
def buscar_turnos_de_cliente():
    id_usuario = request.args.get("id_usuario")

    if not id_usuario:
        return jsonify({"error": "Parámetro faltante: id_usuario"}), 400

    try:
        id_usuario = int(id_usuario)
    except ValueError:
        return jsonify({"error": "id_usuario inválido"}), 400

    reservas = ReservaTurno.query.filter_by(id_usuario=id_usuario).all()

    if not reservas:
        return jsonify({"turnos": []}), 200

    resultado = []
    for reserva in reservas:
        turno = Turno.query.get(reserva.id_turno)
        if not turno:
            continue

        clase = Clase.query.get(turno.id_clase)
        if not clase:
            continue

        resultado.append(
            {
                "id_reserva": reserva.id,
                "id_turno": turno.id,
                "fecha": turno.fecha.strftime("%d/%m/%Y"),
                "disciplina": clase.disciplina,
                "dia": clase.dia,
                "hora": clase.hora,
                "cupo": clase.cupo,
                "habilitado": turno.habilitado,
            }
        )

    return jsonify({"turnos": resultado}), 200

