from flask import Blueprint, request, jsonify, abort
from models.category import Category
from extensions import db
import common.status_codes as status
from common.logging_config import helper_setup_logging

logger = helper_setup_logging()

categories_bp = Blueprint('categories', __name__)


# --- Category Routes ---
@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([{'id': category.id, 'name': category.name} for category in categories])

@categories_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    category = Category.query.get_or_404(category_id)
    return jsonify({'id': category.id, 'name': category.name})

@categories_bp.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    category = Category(name=data['name'])
    db.session.add(category)
    db.session.commit()
    return jsonify({'id': category.id, 'name': category.name}), 201

@categories_bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.get_json()
    category.name = data['name']
    db.session.commit()
    return jsonify({'id': category.id, 'name': category.name})

@categories_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return '', 204

