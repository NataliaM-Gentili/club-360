from datetime import date, timedelta
from decimal import Decimal
from app import db
from app.models.db_structure import Reserva, ReservaClase, Abono, ClienteSuspendido, Turno

def suspender_abonados_pendientes():
    hoy = date.today()
    primer_dia = hoy.replace(day=1)
    dia_10 = hoy.replace(day=10)

    # Último día del mes
    if hoy.month == 12:
        primer_dia_sig_mes = date(hoy.year + 1, 1, 1)
    else:
        primer_dia_sig_mes = date(hoy.year, hoy.month + 1, 1)
    ultimo_dia = primer_dia_sig_mes - timedelta(days=1)

    pendientes = (
        db.session.query(Reserva, ReservaClase, Abono)
        .join(ReservaClase, ReservaClase.id_reserva == Reserva.id)
        .join(Abono, Abono.id_reserva == Reserva.id)
        .filter(Reserva.estado == "Pendiente")
        .all()
    )

    count = 0
    for reserva, reserva_clase, abono in pendientes:
        ya_suspendido = ClienteSuspendido.query.filter_by(
            id_cliente=reserva.id_cliente,
            id_clase=reserva_clase.id_clase,
        ).first()

        if not ya_suspendido:
            total_turnos_mes = Turno.query.filter(
                Turno.id_clase == reserva_clase.id_clase,
                Turno.fecha >= primer_dia,
                Turno.fecha <= ultimo_dia,
            ).count()

            turnos_1_al_10 = Turno.query.filter(
                Turno.id_clase == reserva_clase.id_clase,
                Turno.fecha >= primer_dia,
                Turno.fecha <= dia_10,
            ).count()

            if total_turnos_mes > 0 and turnos_1_al_10 > 0:
                precio_por_turno = Decimal(str(abono.monto)) / total_turnos_mes
                monto = (precio_por_turno * turnos_1_al_10 * Decimal("1.05")).quantize(Decimal("0.01"))
            else:
                monto = Decimal(str(abono.monto))

            db.session.add(ClienteSuspendido(
                id_cliente=reserva.id_cliente,
                id_clase=reserva_clase.id_clase,
                monto=monto,
            ))
            count += 1

    db.session.commit()
    print(f"[Suspensión automática] {count} cliente(s) suspendido(s).")
