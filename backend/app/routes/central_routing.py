from flask import Blueprint, jsonify, request
from app.models.user_model import Item

# al agregar nuevos controladores, sólo hay que
# importarlos a este archivo con la misma sintaxis que arriba, en app/_init_.py levanta
# éste archivo primero y reconoce todas las rutas
main = Blueprint("main", __name__)


@main.route("/items", methods=["GET"])
def get_items():
    items = Item.get_all()
    return jsonify([item.to_dict() for item in items])


def all_routes(app):
    from app.routes.user_routes import user_bp
    from app.routes.clase_routes import clase_bp
    from app.routes.reserva_routes import reserva_bp

    app.register_blueprint(user_bp, url_prefix="/api")

    from app.routes.turno_routes import turno_bp

    app.register_blueprint(turno_bp, url_prefix="/api")

    from app.routes.actividad_routes import actividad_bp

    app.register_blueprint(actividad_bp, url_prefix="/api")
    app.register_blueprint(clase_bp, url_prefix="/api")
    app.register_blueprint(reserva_bp, url_prefix="/api")
    from app.routes.tarjeta_routes import tarjeta_bp
    app.register_blueprint(tarjeta_bp, url_prefix="/api")
    
