from flask import Blueprint, jsonify
from Data.NodeDatabaseManagement import NodeDatabaseManagement
from Utilities.auth_utils import login_required

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('/categories', methods=['GET'])
@login_required
def list_categories():
    try:
        node_db = NodeDatabaseManagement()
        categories = node_db.list_categories()
        return jsonify({"categories": categories}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@categories_bp.route('/categories_with_files', methods=['GET'])
def list_categories_with_files():
    try:
        node_db = NodeDatabaseManagement()
        categories = node_db.list_categories_with_files()
        return jsonify({"categories": categories}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
