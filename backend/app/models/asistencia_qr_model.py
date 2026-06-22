from app import db
from app.models.db_structure import (
    Reserva,
    Turno,
    Clase,
    ReservaTurno,
    ReservaClase,
    cliente_asistio_turno,
)
from datetime import datetime, timedelta


class AsistenciaModel:

    @staticmethod
    def parsear_qr(texto_qr: str) -> dict | None:
        """
        Parsea el string del QR y retorna un dict con las claves,
        o None si el formato es inválido.
        Formato esperado: "id_cliente:7|id_turno:3|id_reserva:42"
        """
        try:
            partes = dict(p.split(":") for p in texto_qr.strip().split("|"))
            return {
                "id_cliente": int(partes["id_cliente"]),
                "id_turno": int(partes["id_turno"]),
                "id_reserva": int(partes["id_reserva"]),
            }
        except Exception:
            return None

    @staticmethod
    def registrar(texto_qr: str):
        """
        Valida y registra la asistencia a partir del texto crudo del QR.
        Retorna (ok: bool, mensaje: str, payload: dict | None)
        """
        MSG_QR_INVALIDO = "Lo sentimos, el qr escaneado es incorrecto, por favor, vuelva a intentarlo."
        MSG_EXPIRADO = "Error: El QR asignado registrado expiró."
        MSG_FUTURO = "Error: El turno aún no ha comenzado."
        MSG_TEMPRANO = "Error: La clase asignada aun no ha comenzado."
        MSG_SIN_PAGO = "Error: Usted no ha pagado la totalidad del turno."
        MSG_SIN_MENSUAL = "Error: Usted no ha pagado la mensualidad a dicha clase."
        MSG_YA_REGISTRADO = "Error: La asistencia ya fue registrada previamente."
        MSG_OK = "Registro de asistencia correcta"

        # ── 1. Parsear QR ────────────────────────────────────────────────────
        datos = AsistenciaModel.parsear_qr(texto_qr)
        if not datos:
            return False, MSG_QR_INVALIDO, None

        id_cliente = datos["id_cliente"]
        id_turno = datos["id_turno"]
        id_reserva = datos["id_reserva"]

        # ── 2. Reserva real y pertenece al cliente ───────────────────────────
        reserva = Reserva.query.filter_by(id=id_reserva, id_cliente=id_cliente).first()
        if not reserva:
            return False, MSG_QR_INVALIDO, None

        # ── 3. Turno y clase existen ─────────────────────────────────────────
        turno = Turno.query.get(id_turno)
        if not turno:
            return False, MSG_QR_INVALIDO, None

        clase = Clase.query.get(turno.id_clase)
        if not clase:
            return False, MSG_QR_INVALIDO, None

        # ── 4. Validación de fecha y hora ────────────────────────────────────
        ahora = datetime.now()
        hora_inicio = datetime.strptime(clase.hora, "%H:%M").time()
        inicio_dt = datetime.combine(turno.fecha, hora_inicio)
        inicio_permitido = inicio_dt - timedelta(hours=1)
        fin_dt = inicio_dt + timedelta(hours=1)

        if ahora < inicio_permitido:
            if ahora.date() < turno.fecha:
                return False, MSG_FUTURO, None
            return False, MSG_TEMPRANO, None

        if ahora > fin_dt:
            return False, MSG_EXPIRADO, None

        # ── 5. Verificar tipo de reserva ─────────────────────────────────────
        es_turno = (
            ReservaTurno.query.filter_by(
                id_reserva=id_reserva, id_turno=id_turno
            ).first()
            is not None
        )

        es_clase = (
            ReservaClase.query.filter_by(
                id_reserva=id_reserva, id_clase=turno.id_clase
            ).first()
            is not None
        )

        if not es_turno and not es_clase:
            return False, MSG_QR_INVALIDO, None

        # ── 6. Verificar pago ────────────────────────────────────────────────
        if reserva.estado != "Pago":
            if es_turno:
                return (
                    False,
                    MSG_SIN_PAGO,
                    {"accion": "completar_pago", "reserva_id": id_reserva},
                )
            if es_clase:
                return False, MSG_SIN_MENSUAL, None

        # ── 7. Ya registrado ─────────────────────────────────────────────────
        ya = db.session.execute(
            cliente_asistio_turno.select().where(
                cliente_asistio_turno.c.id_turno == id_turno,
                cliente_asistio_turno.c.id_cliente == id_cliente,
            )
        ).first()
        if ya:
            return False, MSG_YA_REGISTRADO, None

        # ── 8. Registrar ─────────────────────────────────────────────────────
        db.session.execute(
            cliente_asistio_turno.insert().values(
                id_turno=id_turno, id_cliente=id_cliente
            )
        )
        db.session.commit()
        return True, MSG_OK, None
