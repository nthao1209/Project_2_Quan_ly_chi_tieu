from flask import Blueprint, jsonify, request, render_template, session
from models import db, Category

category_bp= Blueprint('category', __name__)



@category_bp.route('/categories', methods=['GET'])
def get_categories():
    user_id=session.get('user_id')
    if user_id is None:
        return jsonify({"Error": "User not logged in"}), 401
    


    categories = Category.query.filter(
        (Category.user_id == user_id) | (Category.user_id.is_(None))
    ).all()

    data = [{
        'id': c.category_id,
        'name': c.name,
        'icon': c.icon,
        'type': c.type,
    } for c in categories]

    return jsonify(data), 200


@category_bp.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    user_id = session.get('user_id')

    if user_id is None:
        return jsonify({"Error": "User not logged in"}), 401
    
    name= data.get('name')
    icon= data.get('icon')
    type= data.get('type')

    if not name or not icon or not type or not user_id:
        return jsonify({"Error": "Missing required fields"}), 400
    
    existing = Category.query.filter_by(name=name, user_id=user_id).first()

    if existing:
        return jsonify({"Error": "Category already exists"}), 400
    
    new_category = Category(name=name, icon=icon, user_id=user_id, type=type)
    type = data.get('type', '').strip().capitalize()
    if type not in ['Chi tiêu', 'Thu nhập']:
       return jsonify({"Error": "Invalid category type"}), 400
    db.session.add(new_category)
    db.session.commit()
    
    return jsonify({
    "message": "Category created successfully",
    "category": {
        "id": new_category.category_id,
        "name": new_category.name,
        "icon": new_category.icon,
        "type": new_category.type
    }
}), 201

@category_bp.route('/categories-page')
def categories_page():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not logged in'}), 401
    
    expenses = Category.query.filter_by(user_id=user_id, type='Chi tiêu').all()
    income = Category.query.filter_by(user_id=user_id, type='Thu nhập').all()

    return render_template('category.html', expenses_categories=expenses, income_categories=income)

@category_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'message': 'Danh mục không tồn tại'}), 404

    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Xóa danh mục thành công', 'category_id': category_id})
