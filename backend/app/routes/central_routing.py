from flask import Blueprint, jsonify, request
from app.models.user_model import Item

main = Blueprint('main', __name__)

@main.route('/items', methods=['GET'])
def get_items():
    items = Item.get_all()
    return jsonify([item.to_dict() for item in items])