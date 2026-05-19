from flask import Blueprint, request, jsonify, session
from app.models.user_model import UserModel
from app.services.email_services import send_password_reset_email
from app.models.tarjeta_model import TarjetaModel

user_bp = Blueprint("user_bp", __name__)  # defines user blueprint for flask


# /SIGNUP --> ruta de registro de usuario
@user_bp.route("/signup", methods=["POST"])
def signup():
    data = (
        request.get_json()
    )  # recupera en la variable data lo enviado en el post del front

    required_fields = ["email", "dni", "nombres", "apellido", "contrasena"]

    # --- check missing fields ---
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Campo faltante: {field}"}), 400

    email = data["email"]
    dni = data["dni"]
    password = data["contrasena"]

    # --- validaciones de los datos enviados ---

    # unique email
    if UserModel.get_user_by_email(email):
        return jsonify({"error": "El email se encuentra en uso, elija otro"}), 409

    # unique DNI
    if UserModel.get_user_by_dni(dni):
        return jsonify({"error": "El DNI ya se encuentra registrado"}), 409

    # DNI: exactly 8 digits
    if not (dni.isdigit() and len(dni) == 8):
        return jsonify({"error": "El DNI debe tener 8 dígitos"}), 400

    # password length
    if len(password) < 7:
        return jsonify({"error": "La contraseña debe tener mínimo 7 caracteres"}), 400

    # Llama al modelo para que ejecute el UPDATE de la bd
    user = UserModel.create_user(data)

    return jsonify({"message": "¡Usuario creado con éxito!", "user_id": user.id}), 201


# LOGIN
@user_bp.route("/login", methods=["POST"])
def login():
    datos = request.get_json()
    email_ingresado = datos.get("email")
    password_ingresado = datos.get("password")

    # Busqueda de usuario
    usuario = UserModel.obtener_email_usuario(email_ingresado)

    # usuario no encontrado
    if not usuario or not UserModel.verificar_contrasena(usuario, password_ingresado):
        return (
            jsonify(
                {
                    "mensaje": "No se ha podido iniciar sesión. Por favor, revise sus datos"
                }
            ),
            401,
        )

    # usuario encontrado
    session["usuario_id"] = usuario.id
    session["rol_id"] = usuario.rol_id

    return (
        jsonify({"message": "Inicio de sesión exitoso", "usuario": usuario.email}),
        200,
    )


# LOGOUT
@user_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"mensaje": "Sesión cerrada. ¡Hasta luego!"}), 200


# ----- LOGIN AUTHORISATION ROUTE
# evalúa si el usuario está logueado o no y recupera los datos de la session
@user_bp.route("/auth/status", methods=["GET"])
def auth_status():
    if "usuario_id" in session:
        usuario = UserModel.get_by_id(session["usuario_id"])
        return jsonify({
            "loggedIn": True,
            "user_id": session["usuario_id"],
            "rol_id": session["rol_id"],
            "email": usuario.email if usuario else None,
            "nombres": usuario.nombres if usuario else None,
        }), 200

    return jsonify({"loggedIn": False}), 200


# REGISTRO CLIENTE DESDE EMPLEADO
@user_bp.route("/registrar_cliente", methods=["POST"])
def registrar_cliente():
    new_user = request.get_json()

    response = signup()
    status_code = (
        response[1]
        if isinstance(response, tuple)
        else getattr(response, "status_code", 200)
    )

    email = new_user.get("email")
    if status_code in [200, 201]:
        try:
            token = UserModel.generate_reset_token(email)
            if token:
                send_password_reset_email(email, token)
        except Exception as e:
            print(f"Error al enviar el correo de bienvenida: {e}")
    return response


# PROFILE INFO
@user_bp.route("/profile", methods=["GET"])
def get_profile():

    user_id = session.get("usuario_id")

    if not user_id:
        return jsonify({"error": "No autenticado"}), 401

    user = UserModel.get_by_id(user_id)
    cards = TarjetaModel.get_by_user(user_id)

    return jsonify({"user": user.to_dict(), "cards": [c.to_dict() for c in cards]}), 200


# RESET PASSWORD
@user_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()

    token = data.get("token")
    nueva_contrasena = data.get("contrasena")

    if not token or not nueva_contrasena:
        return jsonify({"error": "Datos incompletos"}), 400

    if len(nueva_contrasena) < 7:
        return jsonify({"error": "La contraseña debe tener mínimo 7 caracteres"}), 400

    user, error = UserModel.reset_password(token, nueva_contrasena)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "Contraseña actualizada con éxito"}), 200


# GENERAR TOKEN PARA CAMBIO DE CONTRASEÑA (usuario logueado)
@user_bp.route("/generar-token-cambio", methods=["POST"])
def generar_token_cambio():
    user_id = session.get("usuario_id")
    if not user_id:
        return jsonify({"error": "No autenticado"}), 401

    usuario = UserModel.get_by_id(user_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    token = UserModel.generate_reset_token(usuario.email)
    return jsonify({"token": token}), 200


# GENERAR TOKEN POR EMAIL (usuario no logueado)
@user_bp.route("/generar-token-email", methods=["POST"])
def generar_token_email():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email requerido"}), 400

    usuario = UserModel.get_user_by_email(email)
    if not usuario:
        return jsonify({"error": "No existe una cuenta con ese email"}), 404

    token = UserModel.generate_reset_token(email)
    return jsonify({"token": token}), 200
