from flask import current_app
from flask_mail import Message
from app import mail  # instancia de Flask-Mail
import qrcode 
import io
import base64
from app.models.db_structure import Usuario



EMAIL_PRUEBAS = "juanmanuelperezz468@gmail.com"


def send_password_reset_email(email, token):
    reset_url = f"http://localhost:5173/reset-password?token={token}"

    msg = Message(
        subject="Activá tu cuenta",
        # SI quieren probar con un email que no este hardcodeado, pongan esto recipients=[email]
        recipients=["juanmanuelperezz468@gmail.com"],
        body=f"Hola!, hacé clic en el siguiente link para establecer tu contraseña. No tardes en unirte, te esperamos con ansias! {reset_url}",
    )

    mail.send(msg)
    return {
        "message": "El mail para el reestablecimiento de contraseña ha sido enviado a juanmanuelperezz468@gmail.com"
    }, 201

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


