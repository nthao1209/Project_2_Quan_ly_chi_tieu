from flask import Blueprint, render_template, request, jsonify, flash, session
from models import db, User, Category, Budget
from datetime import datetime

budget_bp = Blueprint('budget', __name__)

# Hàm hiển thị danh sách budgets (HTML)
@budget_bp.route('/budgets')
def list_budget():
    budgets = Budget.query.all()
    categories=Category.query.all()
    return render_template('budget.html', budgets=budgets,categories=categories)

# Hàm xử lý thêm/cập nhật budget từ dữ liệu
def create_or_update_budget(data, budget=None):
    raw_amount = data.get('limit_amount')

    if not raw_amount:
        raise ValueError("Số tiền không được để trống.")

    if isinstance(raw_amount, str):
        raw_amount = raw_amount.replace(',', '').replace(' ', '')

    limit_amount = float(raw_amount)

    start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
    end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()

    if start_date > end_date:
        raise ValueError("Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc.")

    if budget:
        budget.limit_amount = limit_amount
        budget.start_date = start_date
        budget.end_date = end_date
        return budget
    else:
        user_id = session.get('user_id')
        category_id = data.get('category_id')
        if not user_id or not category_id:
            raise ValueError("Thiếu user_id hoặc category_id trong session.")
        return Budget(
            user_id=user_id,
            category_id=category_id,
            limit_amount=limit_amount,
            start_date=start_date,
            end_date=end_date,
        )

# API: Thêm ngân sách
@budget_bp.route('/budgets/add', methods=['POST'])
def add_budget():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dữ liệu không hợp lệ hoặc không có dữ liệu JSON"}), 400

    try:
        if not session.get('user_id'):
            return jsonify({"error": "Chưa đăng nhập"}), 401

        new_budget = create_or_update_budget(data)
        db.session.add(new_budget)
        db.session.commit()
        return jsonify({'message': 'Đã thêm ngân sách', 'budget_id': new_budget.budget_id}), 201

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# API: Cập nhật ngân sách
@budget_bp.route('/budgets/update/<int:budget_id>', methods=['PUT'])
def update_budget(budget_id):
    existing_budget = Budget.query.get(budget_id)
    if not existing_budget:
        return jsonify({'error': 'Không tìm thấy'}), 404

    data = request.get_json()
    try:
        updated_budget = create_or_update_budget(data, existing_budget)
        db.session.commit()
        return jsonify({'message': 'Đã cập nhật'})
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# API: Xóa ngân sách
@budget_bp.route('/budgets/delete/<int:budget_id>', methods=['DELETE'])
def delete_budget(budget_id):
    budget = Budget.query.get(budget_id)
    if not budget:
        return jsonify({'error': 'Không tìm thấy'}), 404

    db.session.delete(budget)
    db.session.commit()
    return jsonify({'message': f'Đã xóa {budget_id}'})
