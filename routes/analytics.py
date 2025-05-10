from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import extract, func
from models import Transaction, Category, Budget  # Import thêm Budget nếu chưa
from . import db

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
def analytics_page():
    return render_template('analytics.html')

@analytics_bp.route('/api/analytics-data')
def analytics_data():
    month = int(request.args.get('month'))
    year = int(request.args.get('year'))
    data_type = request.args.get('type', default='expense') 

    data = []
    total = 0

    if data_type in ['expense', 'income']:
        # Truy vấn Transaction theo loại và thời gian
        results = db.session.query(
            Transaction.category_id,
            func.sum(Transaction.amount).label('total')
        ).filter(
            extract('month', Transaction.transaction_date) == month,
            extract('year', Transaction.transaction_date) == year,
            Transaction.transaction_type == data_type
        ).group_by(Transaction.category_id).all()

        for category_id, total_amount in results:
            category = Category.query.get(category_id)
            if category:
                data.append({
                    'category': category.name,
                    'icon': category.icon,
                    'total': float(total_amount)
                })
                total += float(total_amount)

    elif data_type == 'budget':
        # Truy vấn bảng Budget riêng
        results = db.session.query(
            Budget.category_id,
            func.sum(Budget.amount).label('total')
        ).filter(
            extract('month', Budget.budget_month) == month,
            extract('year', Budget.budget_month) == year
        ).group_by(Budget.category_id).all()

        for category_id, total_amount in results:
            category = Category.query.get(category_id)
            if category:
                data.append({
                    'category': category.name,
                    'icon': category.icon,
                    'total': float(total_amount)
                })
                total += float(total_amount)

    return jsonify({
        'data': data,
        'total': total
    })
