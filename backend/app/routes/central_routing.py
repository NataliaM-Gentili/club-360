from flask import Blueprint, jsonify, request
from app.models.user_model import Item
# al agregar nuevos controladores, sólo hay que 
# importarlos a este archivo con la misma sintaxis que arriba, en app/_init_.py levanta 
# éste archivo primero y reconoce todas las rutas
main = Blueprint('main', __name__)

@main.route('/items', methods=['GET'])
def get_items():
    items = Item.get_all()
    return jsonify([item.to_dict() for item in items])

def all_routes(app):
    from app.routes.user_routes import user_bp
    app.register_blueprint(user_bp, url_prefix="/api")

    from app.routes.tarjeta_routes import tarjeta_bp
    app.register_blueprint(tarjeta_bp, url_prefix="/api")
    
    