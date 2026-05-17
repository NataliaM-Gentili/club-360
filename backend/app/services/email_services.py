from flask import current_app
from flask_mail import Message
from app import mail  # instancia de Flask-Mail


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
