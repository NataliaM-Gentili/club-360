from flask import current_app, session
from flask_mail import Message
from app import mail  # instancia de Flask-Mail
import qrcode   
import io
import base64
from app.models.db_structure import Usuario

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