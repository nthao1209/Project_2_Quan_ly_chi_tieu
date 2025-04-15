from flask import Blueprint, jsonify, request, session, render_template, redirect, flash, url_for
from datetime import datetime
from decimal import Decimal
from models import db, Transaction, Category

transaction_bp = Blueprint('transaction', __name__)

def extract_transaction_date(form):
    try:
        transaction_date = datetime.strptime(form['transaction_date'], '%Y-%m-%d')
    except ValueError:
        transaction_date = datetime.now()

    return {
        'user_id': int(session.get('user_id')),
        'account_id': int(form.get('account_id')),
        'category_id': int(form.get('category_id')),
        'amount': Decimal(form.get('amount')),
        'transaction_type': form.get('transaction_type'),
        'transaction_date': transaction_date,
        'note': form.get('note')
    }

@transaction_bp.route('/transactions', methods=['GET'])
def all_transactions():
    category_id = request.args.get('category_id')
    date_str = request.args.get('date')
    month = request.args.get('month')
    year = request.args.get('year')

    if category_id:
        transactions = Transaction.query.filter_by(category_id=category_id).all()
        category = Category.query.get(category_id)
    else:
        transactions = Transaction.query.all()
        category = None

    filtered_transactions = transactions

    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            filtered_transactions = [t for t in filtered_transactions if t.transaction_date.date() == target_date]
        except ValueError:
            flash('Ngày không hợp lệ.')

    if month:
        try:
            month = int(month)
            filtered_transactions = [t for t in filtered_transactions if t.transaction_date.month == month]
        except ValueError:
            flash('Tháng không hợp lệ.')

    if year:
        try:
            year = int(year)
            filtered_transactions = [t for t in filtered_transactions if t.transaction_date.year == year]
        except ValueError:
            flash('Năm không hợp lệ.')

    return render_template('transaction.html', transactions=filtered_transactions, category=category)


@transaction_bp.route('/transactions/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        try:
            data = extract_transaction_date(request.form)
            print(data)
            new_transaction = Transaction(**data)
            db.session.add(new_transaction)
            db.session.commit()
            flash('Ghi nhận thành công')
            return redirect(url_for('transaction.all_transactions', category_id=data['category_id']))
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            flash('Ghi nhận thất bại')
    return redirect(url_for('transaction.all_transactions'))

@transaction_bp.route('/transactions/edit/<int:transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)

    if request.method == 'POST':
        try:
            data = extract_transaction_date(request.form)
            for key, value in data.items():
                setattr(transaction, key, value)
            db.session.commit()
            flash('Cập nhật thành công')
            return redirect(url_for('transaction.all_transactions', category_id=data['category_id']))
        except Exception as e:
            db.session.rollback()
            flash('Cập nhật thất bại')
    return redirect(url_for('transaction.all_transactions'))

@transaction_bp.route('/transactions/delete/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    category_id = transaction.category_id
    try:
        db.session.delete(transaction)
        db.session.commit()
        flash('Xóa thành công')
    except Exception as e:
        db.session.rollback()
        flash('Xóa thất bại')
    return redirect(url_for('transaction.all_transactions', category_id=category_id))
