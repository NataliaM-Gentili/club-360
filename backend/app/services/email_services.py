from flask import current_app, session
from flask_mail import Message
from app import mail  # instancia de Flask-Mail
import qrcode   
import io
import base64
from app.models.db_structure import Usuario, Clase, Cliente, ReservaTurno, ReservaClase, Turno, Reserva, OfrecimientoReserva

EMAIL_PRUEBAS = "juanmanuelperezz468@gmail.com"


def send_password_reset_email(email, token):
    reset_url = f"http://localhost:5173/reset-password?token={token}"

    html = f"""
    <div style="background-color:#f0f0f0;font-family:Helvetica Neue,Helvetica,Arial,sans-serif;color:#333;padding:40px 16px;min-height:100vh">
      <div style="max-width:520px;margin:0 auto;border-radius:24px;overflow:hidden;box-shadow:0 4px 32px rgba(0,0,0,0.09)">
        <div style="background-color:#598849;padding:40px 40px 32px;color:#fafafa">
          <div style="font-size:13px;font-weight:700;letter-spacing:2px;text-transform:uppercase;opacity:0.85;margin-bottom:28px">Club 360</div>
          <h1 style="font-size:26px;font-weight:700;margin:0 0 6px">Restablecer contraseña</h1>
          <p style="font-size:14px;font-weight:300;opacity:0.85;margin:0"></p>
        </div>
        <div style="background-color:#fafafa;padding:32px 40px">
          <p style="font-size:15px;color:#333;margin-bottom:28px;line-height:1.65">
            Hola!,<br/>
            Recibimos una solicitud para restablecer la clave de tu cuenta en Club 360.
            Si fuiste vos, hacé clic en el botón de abajo para continuar.
          </p>
          
          <div style="text-align:center;margin-bottom:28px">
            <a href="{reset_url}" style="display:inline-block;background-color:#598849;color:#fafafa;text-decoration:none;font-size:15px;font-weight:600;padding:14px 36px;border-radius:20px">
              Restablecer contraseña
            </a>
          </div>
         
          <p style="font-size:13px;color:rgba(0,0,0,0.45);line-height:1.65">
            <strong style="color:rgba(0,0,0,0.65)">¿No solicitaste esto?</strong> Podés ignorar este correo con seguridad.
            Tu contraseña no cambiará a menos que hagas clic en el enlace de arriba.
          </p>
        </div>
        <div style="background-color:#fafafa;border-top:1px solid rgba(0,0,0,0.07);padding:24px 40px;text-align:center">
          <p style="font-size:12px;color:rgba(0,0,0,0.35);line-height:1.7;margin:0">© 2026 Club 360.</p>
        </div>
      </div>
    </div>
    """

    msg = Message(
        subject="Restablecer contraseña - Club 360",
        recipients=[email],
        html=html,  # ← acá el cambio clave
    )

    mail.send(msg)
    return {"message": "El mail fue enviado correctamente"}, 201

def generar_qr_bytes(datos: str) -> bytes:
    """Genera un QR a partir de un string y lo retorna como bytes PNG."""
    img = qrcode.make(datos)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.read()


def _obtener_email_cliente(id_cliente: int) -> str:
    """
    Retorna el email del cliente. Si no se encuentra, usa el email de pruebas.
    """
    usuario = Usuario.query.get(id_cliente)
    if usuario and usuario.email:
        return usuario.email
    return EMAIL_PRUEBAS


def send_admin_waitlist_warning(turno, interesados_count=10):
    """
    Envía un aviso al administrador cuando la lista de espera de un turno alcanza 10 interesados.
    """
    try:
        clase = Clase.query.get(turno.id_clase)
        disciplina = clase.disciplina.capitalize() if clase else "N/A"
        hora = clase.hora if clase else "N/A"
        fecha = turno.fecha.strftime("%d/%m/%Y") if turno.fecha else "N/A"
        detalles_turno = f"Turno ID: {turno.id} | Disciplina: {disciplina} | Fecha: {fecha} | Hora: {hora}"

        html = f"""
        <div style=\"background-color:#f7faf7;font-family:Helvetica Neue,Helvetica,Arial,sans-serif;color:#1f2937;padding:40px 16px;min-height:100vh\">
          <div style=\"max-width:600px;margin:0 auto;border-radius:24px;overflow:hidden;box-shadow:0 8px 30px rgba(0,0,0,0.12)\">
            <div style=\"background:linear-gradient(135deg,#386a2a 0%,#598849 100%);padding:38px 40px;color:#f8fafc\">
              <div style=\"font-size:13px;font-weight:700;letter-spacing:2px;text-transform:uppercase;opacity:0.85;margin-bottom:24px\">Club 360 - Administración</div>
              <h1 style=\"font-size:28px;font-weight:800;margin:0 0 8px\">Alerta de lista de espera</h1>
              <p style=\"font-size:16px;opacity:0.92;line-height:1.7;margin:0\">La lista de espera del turno ha alcanzado <strong>10 interesados</strong>.</p>
            </div>
            <div style=\"background-color:#ffffff;padding:32px 40px;line-height:1.7;color:#334155\">
              <p style=\"font-size:15px;margin:0 0 20px\">Estimado administrador,</p>
              <p style=\"font-size:15px;margin:0 0 20px\">El turno detallado a continuación ha superado el umbral de <strong>10 interesados</strong> en la lista de espera.</p>
              <div style=\"background:#f0fdf4;border:1px solid #d1fae5;border-radius:16px;padding:22px;margin:24px 0\">
                <p style=\"margin:0 0 10px;font-size:15px;color:#0f5132\"><strong>Detalles del turno</strong></p>
                <p style=\"margin:4px 0;font-size:14px;color:#334155\"><strong>Disciplina:</strong> {disciplina}</p>
                <p style=\"margin:4px 0;font-size:14px;color:#334155\"><strong>Fecha:</strong> {fecha}</p>
                <p style=\"margin:4px 0;font-size:14px;color:#334155\"><strong>Hora:</strong> {hora}</p>
                <p style=\"margin:4px 0;font-size:14px;color:#334155\"><strong>Cupo:</strong> {clase.cupo if clase else 'N/A'}</p>
              </div>
              <p style=\"font-size:14px;color:#475569;margin:0\">Este correo se envía automáticamente para avisar que la demanda del turno ha superado el umbral definido.</p>
            </div>
            <div style=\"background-color:#f8fafc;border-top:1px solid rgba(15,23,42,0.08);padding:24px 40px;text-align:center\">
              <p style=\"font-size:12px;color:#475569;line-height:1.7;margin:0\">© 2026 Club 360. Administrador - Lista de espera</p>
            </div>
          </div>
        </div>
        """

        msg = Message(
            subject="Alerta: lista de espera con 10 interesados - Club 360",
            recipients=[EMAIL_PRUEBAS],
            html=html,
        )
        mail.send(msg)
        return True

    except Exception as e:
        print(f"[email_services] Error al enviar alerta de lista de espera: {e}")
        return False


# NO ABONADO
def enviar_comprobante_qr_turno(id_cliente, id_reserva, id_turno, disciplina, fecha, hora):
    """
    Genera un QR con los datos del turno y lo adjunta al email del cliente.
    El QR contiene: id_cliente, id_turno, id_reserva.
    """
    try:
        email_destino = _obtener_email_cliente(id_cliente)

        datos_qr = f"id_cliente:{id_cliente}|id_turno:{id_turno}|id_reserva:{id_reserva}"
        qr_bytes = generar_qr_bytes(datos_qr)

        msg = Message(
            subject="Comprobante de reserva - Club 360",
            recipients=[email_destino],
            body=(
                f"¡Tu turno fue reservado con éxito!\n\n"
                f"Disciplina: {disciplina.capitalize()}\n"
                f"Fecha: {fecha}\n"
                f"Hora: {hora}\n\n"
                f"Presentá el QR adjunto al ingresar al club.\n\n"
                f"Club 360"
            ),
        )
        msg.attach(
            filename=f"qr_reserva_{id_reserva}.png",
            content_type="image/png",
            data=qr_bytes,
        )
        mail.send(msg)

    except Exception as e:
        print(f"[email_services] Error al enviar QR turno: {e}")




# ABONADO
def enviar_comprobantes_qr_clase(id_cliente, id_reserva, disciplina, hora, turnos):
    """
    Genera un QR por cada turno restante del mes y los adjunta todos en un único email.
    Cada QR contiene: id_cliente, id_turno, id_reserva.
    """
    try:
        email_destino = _obtener_email_cliente(id_cliente)

        msg = Message(
            subject="Comprobante de abono mensual - Club 360",
            recipients=[email_destino],
            body=(
                f"¡Tu abono mensual fue registrado con éxito!\n\n"
                f"Disciplina: {disciplina.capitalize()}\n"
                f"Hora: {hora}\n\n"
                f"Encontrás adjuntos los QRs correspondientes a cada turno del mes.\n"
                f"Presentá el QR del día al ingresar al club.\n\n"
                f"Club 360"
            ),
        )

        for turno in turnos:
            datos_qr = f"id_cliente:{id_cliente}|id_turno:{turno.id}|id_reserva:{id_reserva}"
            qr_bytes = generar_qr_bytes(datos_qr)
            fecha_str = turno.fecha.strftime("%d-%m-%Y")
            msg.attach(
                filename=f"qr_{disciplina}_{fecha_str}.png",
                content_type="image/png",
                data=qr_bytes,
            )

        mail.send(msg)

    except Exception as e:
        print(f"[email_services] Error al enviar QRs clase: {e}")



def send_cancellation_email(email_destino, nombre, disciplina, fecha, hora, monto):
    """
    Envía un correo notificando la cancelación de un turno y la devolución del dinero (si aplica).
    """
    try:
        asunto = f"Cancelación de turno de {disciplina.capitalize()} - Club 360"

        # Mensaje base
        mensaje_devolucion = ""
        if monto and float(monto) > 0:
            mensaje_devolucion = f"""
            <div style="background-color:#e6f4ea;border-left:4px solid #598849;padding:16px;margin:24px 0;border-radius:4px">
                <p style="margin:0;font-size:14px;color:#1a432b;font-weight:600">
                    ℹ️ Información sobre tu pago
                </p>
                <p style="margin:8px 0 0;font-size:14px;color:#2d5e3c;line-height:1.5">
                    Como ya habías abonado el turno, se realizará la devolución automática de <strong>${float(monto):.2f}</strong>. 
                    El dinero se verá reflejado en la cuenta con la que hiciste el pago dentro de las próximas <strong>72 horas hábiles</strong>.
                </p>
            </div>
            """

        html = f"""
        <div style="background-color:#f0f0f0;font-family:Helvetica Neue,Helvetica,Arial,sans-serif;color:#333;padding:40px 16px;min-height:100vh">
        <div style="max-width:520px;margin:0 auto;border-radius:24px;overflow:hidden;box-shadow:0 4px 32px rgba(0,0,0,0.09)">
            
            <div style="background-color:#598849;padding:40px 40px 32px;color:#fafafa">
            <div style="font-size:13px;font-weight:700;letter-spacing:2px;text-transform:uppercase;opacity:0.85;margin-bottom:28px">Club 360</div>
            <h1 style="font-size:26px;font-weight:700;margin:0 0 6px">Turno Cancelado</h1>
            </div>
            
            <div style="background-color:#fafafa;padding:32px 40px">
            <p style="font-size:16px;color:#333;margin-bottom:20px;line-height:1.65">
                Hola <strong>{nombre}</strong>,  </p>
            
            <p style="font-size:15px;color:#333;margin-bottom:24px;line-height:1.65">
                Lamentamos informarte que por motivos de organización de la administración, tu turno programado ha sido <strong>cancelado</strong>.
            </p>
              
              <div style="background-color:#ffffff;border:1px solid #e0e0e0;border-radius:12px;padding:20px;margin-bottom:24px">
                <p style="margin:0 0 8px;font-size:14px;color:#666"><strong>Disciplina:</strong> {disciplina.capitalize()}</p>
                <p style="margin:0 0 8px;font-size:14px;color:#666"><strong>Fecha:</strong> {fecha}</p>
                <p style="margin:0;font-size:14px;color:#666"><strong>Hora:</strong> {hora}</p>
              </div>

              {mensaje_devolucion}
              
              <p style="font-size:15px;color:#333;margin-top:28px;line-height:1.65">
                Te pedimos disculpas por los inconvenientes ocasionados.<br/>
                Saludos cordiales,<br/>
                <strong>Equipo Club 360</strong>
              </p>
            </div>
            
            <div style="background-color:#fafafa;border-top:1px solid rgba(0,0,0,0.07);padding:24px 40px;text-align:center">
              <p style="font-size:12px;color:rgba(0,0,0,0.35);line-height:1.7;margin:0">© 2026 Club 360. Todos los derechos reservados.</p>
            </div>
          </div>
        </div>
        """

        msg = Message(
            subject=asunto,
            recipients=[email_destino],
            html=html
        )

        mail.send(msg)
        print(f"[email_services] ✅ Email de cancelación enviado a: {email_destino}")
        
    except Exception as e:
        print(f"[email_services] ❌ Error al enviar email de cancelación a {email_destino}: {e}")

from flask_mail import Message
from flask import current_app

def send_ofrecimiento_turno_mail(ofrecimiento, id_cliente_elegido, id_turno, cliente_emisor):

    cliente = Cliente.query.get(ofrecimiento.id_cliente)
    usuario = Usuario.query.get(cliente.id_usuario)

    reserva_turno = ReservaTurno.query.filter_by(
        id_reserva=ofrecimiento.id_reserva
    ).first()

    if not reserva_turno:
        raise ValueError(
            f"La reserva {ofrecimiento.id_reserva} no posee un turno asociado"
        )

    turno = Turno.query.get(reserva_turno.id_turno)

    if not turno:
        raise ValueError(
            f"No existe el turno {reserva_turno.id_turno}"
        )

    clase = Clase.query.get(turno.id_clase)

    frontend_url = current_app.config["FRONTEND_URL"]

    aceptar_url = (
        f"{frontend_url}ofrecer/aceptar/{ofrecimiento.id}/{id_cliente_elegido}"
    )

    rechazar_url = (
        f"{frontend_url}ofrecer/rechazar/{ofrecimiento.id}/{id_turno}/{cliente_emisor}"
    )

    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="
        margin:0;
        padding:0;
        background:#f4f4f4;
        font-family:Arial, Helvetica, sans-serif;
    ">

        <div style="
            max-width:650px;
            margin:30px auto;
            background:white;
            border-radius:12px;
            overflow:hidden;
            box-shadow:0 2px 10px rgba(0,0,0,0.1);
        ">

            <div style="
                background:#1e3a8a;
                color:white;
                padding:25px;
                text-align:center;
            ">
                <h1 style="margin:0;">
                    Club 360
                </h1>
            </div>

            <div style="padding:30px;">

                <h2 style="color:#1e3a8a;">
                    ¡Hay una vacante disponible para vos!
                </h2>

                <p>
                    Hola <strong>{usuario.nombres}</strong>,
                </p>

                <p>
                    Se liberó un turno y, por tu inscripción en la lista de espera,
                    tenés prioridad para reservarlo.
                </p>

                <div style="
                    background:#f8fafc;
                    border-left:5px solid #1e3a8a;
                    padding:20px;
                    margin:25px 0;
                ">

                    <h3 style="margin-top:0;">
                        Detalle del turno
                    </h3>

                    <p>
                        <strong>Disciplina:</strong>
                        {clase.disciplina}
                    </p>

                    <p>
                        <strong>Fecha:</strong>
                        {turno.fecha.strftime('%d/%m/%Y')}
                    </p>

                    <p>
                        <strong>Día:</strong>
                        {clase.dia}
                    </p>

                    <p>
                        <strong>Horario:</strong>
                        {clase.hora}
                    </p>

                </div>

                <p>
                    Tenés tiempo hasta el
                    <strong>
                        {ofrecimiento.fecha_vencimiento.strftime('%d/%m/%Y')}
                    </strong>
                    para responder.
                </p>

                <div style="
                    text-align:center;
                    margin:35px 0;
                ">

                    <a href="{aceptar_url}"
                       style="
                           background:#16a34a;
                           color:white;
                           text-decoration:none;
                           padding:14px 28px;
                           border-radius:6px;
                           margin-right:10px;
                           display:inline-block;
                           font-weight:bold;
                       ">
                        Aceptar
                    </a>

                    <a href="{rechazar_url}"
                       style="
                           background:#dc2626;
                           color:white;
                           text-decoration:none;
                           padding:14px 28px;
                           border-radius:6px;
                           display:inline-block;
                           font-weight:bold;
                       ">
                        Rechazar
                    </a>

                </div>

            </div>

        </div>

    </body>
    </html>
    """

    msg = Message(
        subject="Club 360 - Vacante disponible",
        recipients=[EMAIL_PRUEBAS] # siempre se envía a juanmanuelperezz
    )

    msg.html = html

    mail.send(msg)