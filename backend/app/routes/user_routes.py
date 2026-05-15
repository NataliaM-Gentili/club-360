from flask import Blueprint, request, jsonify, session
from app.models.user_model import UserModel

user_bp = Blueprint('user_bp', __name__) # defines user blueprint for flask

# /SIGNUP --> ruta de registro de usuario
@user_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json() # recupera en la variable data lo enviado en el post del front

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

    # DNI: exactly 8 digits
    if not (dni.isdigit() and len(dni) == 8):
        return jsonify({"error": "El DNI debe tener 8 dígitos"}), 400

    # password length
    if len(password) < 7:
        return jsonify({"error": "La contraseña debe tener mínimo 7 caracteres"}), 400

    # Llama al modelo para que ejecute el UPDATE de la bd
    user = UserModel.create_user(data)

    return jsonify({
        "message": "¡Usuario creado con éxito!",
        "user_id": user.id
    }), 201


@user_bp.route('/login', methods=['POST'])
def login():
    datos = request.get_json()
    email_ingresado = datos.get('email')
    password_ingresado = datos.get('password')

    #Busqueda de usuario 
    usuario = UserModel.obtener_email_usuario(email_ingresado)

    #usuario no encontrado
    if not usuario or not UserModel.verificar_contrasena(usuario, password_ingresado):
        return jsonify({"mensaje": "No se ha podido iniciar sesión. Por favor, revise sus datos"}), 401
    
    #usuario encontrado
    session['usuario_id'] = usuario.id
    session['rol_id'] = usuario.rol_id
    return jsonify({"message": "Inicio de sesión exitoso", "usuario": usuario.email}), 200
    

# ----- LOGIN AUTHORISATION ROUTE
# evalúa si el usuario está logueado o no y recupera los datos de la session
@user_bp.route('/auth/status', methods=['GET'])
def auth_status():
    if 'usuario_id' in session:
        return jsonify({
            "loggedIn": True,
            "user_id": session['usuario_id'],
            "rol_id": session['rol_id']
        }), 200

    return jsonify({"loggedIn": False}), 200
