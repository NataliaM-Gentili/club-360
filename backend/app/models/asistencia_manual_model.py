from app import db
from app.models.db_structure import (
    Reserva,
    Turno,
    Clase,
    Usuario,
    ReservaTurno,
    ReservaClase,
    cliente_asistio_turno,
)
from datetime import datetime, timedelta


class AsistenciaManualModel:

    @staticmethod
    def registrar_manual(email: str, id_turno: int):
        """
        Registra la asistencia de un cliente a un turno de forma manual,
        a partir de su email. Retorna (ok: bool, mensaje: str).
        """
        MSG_TURNO_NO_ENCONTRADO = "El turno indicado no existe."
        MSG_NO_INSCRIPTO = (
            "El cliente no se encuentra entre los inscriptos a dicho turno"
        )
        MSG_SIN_PAGO = "No se ha podido registrar la asistencia, el cliente debe regularizar su situación de pago"
        MSG_FUERA_HORARIO = "No se ha podido registrar la asistencia, el horario está fuera del permitido"
        MSG_YA_REGISTRADO = "La asistencia de este cliente para este turno ya fue registrada previamente"
        MSG_OK = "Registro de asistencia correcta"

        usuario = Usuario.query.filter_by(email=email).first()
        if not usuario:
            return False, MSG_NO_INSCRIPTO

        turno = Turno.query.get(id_turno)
        if not turno:
            return False, MSG_TURNO_NO_ENCONTRADO

        clase = Clase.query.get(turno.id_clase)
        if not clase:
            return False, MSG_TURNO_NO_ENCONTRADO

        id_cliente = usuario.id

        # ── Verificar inscripción (turno individual o abono mensual) ────────
        reserva = (
            db.session.query(Reserva)
            .join(ReservaTurno, ReservaTurno.id_reserva == Reserva.id)
            .filter(
                ReservaTurno.id_turno == id_turno,
                Reserva.id_cliente == id_cliente,
                Reserva.estado != "Cancelada",
            )
            .first()
        )

        if not reserva:
            reserva = (
                db.session.query(Reserva)
                .join(ReservaClase, ReservaClase.id_reserva == Reserva.id)
                .filter(
                    ReservaClase.id_clase == turno.id_clase,
                    Reserva.id_cliente == id_cliente,
                    Reserva.estado != "Cancelada",
                )
                .first()
            )

        if not reserva:
            return False, MSG_NO_INSCRIPTO

        # ── Verificar pago ────────────────────────────────────────────────
        if reserva.estado != "Pago":
            return False, MSG_SIN_PAGO

        # ── Verificar horario permitido (desde 1h antes hasta el fin del turno) ──
        ahora = datetime.now()
        hora_inicio = datetime.strptime(clase.hora, "%H:%M").time()
        inicio_dt = datetime.combine(turno.fecha, hora_inicio)
        inicio_permitido = inicio_dt - timedelta(hours=1)
        fin_dt = inicio_dt + timedelta(hours=1)

        if ahora < inicio_permitido or ahora > fin_dt:
            return False, MSG_FUERA_HORARIO

        # ── Verificar si ya fue registrada ───────────────────────────────
        ya = db.session.execute(
            cliente_asistio_turno.select().where(
                cliente_asistio_turno.c.id_turno == id_turno,
                cliente_asistio_turno.c.id_cliente == id_cliente,
            )
        ).first()
        if ya:
            return False, MSG_YA_REGISTRADO

        # ── Registrar ─────────────────────────────────────────────────────
        db.session.execute(
            cliente_asistio_turno.insert().values(
                id_turno=id_turno, id_cliente=id_cliente
            )
        )
        db.session.commit()
        return True, MSG_OK
