from flask import Blueprint, jsonify, request, session, render_template, redirect, flash, url_for
from datetime import datetime
from decimal import Decimal
from models import db, Transaction, Category, Account, Budget


transaction_bp = Blueprint('transaction', __name__)

def extract_transaction_date(form):
    try:
        transaction_date = datetime.strptime(form['transaction_date'], '%Y-%m-%d')
    except ValueError:
        transaction_date = datetime.now()
   
    raw_account_id = form.get('account_id')
    if raw_account_id:
        account_id= int(raw_account_id)
    else:
        user_id= session.get('user_id')
        default_account = Account.query.filter_by(user_id=user_id, is_default=True).first()
        if not default_account:
            raise ValueError('Không tìm thấy tài khoản mặc định.')
        account_id = default_account.account_id

    transaction_type_map = {
    'Thu nhập': 'income',
    'Chi tiêu': 'expense',
    }

    raw_type = form.get('transaction_type')
    transaction_type = transaction_type_map.get(raw_type)
    if not transaction_type:
      raise ValueError('Loại giao dịch không hợp lệ.')
   
    return {
        'user_id': session.get('user_id'),
        'account_id': account_id,
        'category_id': int(form.get('category_id')),
        'amount': Decimal(form.get('amount')),
        'transaction_type':transaction_type,
        'transaction_date': transaction_date,
        'note': form.get('note')
    }

def calculate_budget(user_id, category_id):
    budget = Budget.query.filter_by(user_id=user_id, category_id=category_id).first()
    if budget:
        budget_query = Transaction.query.filter_by(
            user_id=user_id,
            category_id=category_id
        )
        if budget.start_date:
            budget_query = budget_query.filter(Transaction.transaction_date >= budget.start_date)
        if budget.end_date:
            budget_query = budget_query.filter(Transaction.transaction_date <= budget.end_date)
    return budget

@transaction_bp.route('/transactions', methods=['GET'])
def all_transactions():
    category_id = request.args.get('category_id')
    date_str = request.args.get('date')
    month = request.args.get('month')
    year = request.args.get('year')
    account_id = request.args.get('account_id')
    
    user_id = session.get('user_id')
    accounts = Account.query.filter_by(user_id=user_id).all()
    
    # Kiểm tra category_id và lấy category nếu có
    category = None
    if category_id:
        category = Category.query.get(category_id)
    
    # Khởi tạo query và lọc theo user_id
    query = Transaction.query.filter_by(user_id=user_id)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if account_id:
        query = query.filter_by(account_id=account_id)

    filtered_transactions = query.all()

    # Lọc theo tháng và năm nếu có
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

    # Tính ngân sách nếu có
    budget = None
    percentage = 0
    total_expense = 0

    if category_id:
        budget = calculate_budget(user_id=user_id, category_id=category_id)
        if budget:
            budget_query = Transaction.query.filter_by(
                user_id=user_id,
                category_id=category_id
            )
            transactions = budget_query.all()
            if transactions:
                total_expense = sum(t.amount for t in budget_query.all())
                print("Transactions for budget:", budget_query.all())
                if budget.limit_amount > 0:
                    percentage = round(float(total_expense / budget.limit_amount * 100), 2)
    
    total_expense = sum(t.amount for t in filtered_transactions)
    
    total_amount = total_expense if total_expense is not None else 0

    return render_template('transaction.html',
                           transactions=filtered_transactions,
                           category=category,
                           accounts=accounts,
                           total_expense=total_expense,
                           budget=budget,
                           total_amount=total_amount, 
                           percentage=percentage)


@transaction_bp.route('/transactions/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        try:
            data = extract_transaction_date(request.form)
            print(data)
            new_transaction = Transaction(**data)
            db.session.add(new_transaction)
            db.session.commit()
            calculate_budget(data['user_id'], data['category_id'])  # cập nhật ngân sách
            flash('Ghi nhận thành công')
            return redirect(url_for('transaction.all_transactions', category_id=data['category_id']))
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            flash('Ghi nhận thất bại')
    return redirect(url_for('transaction.all_transactions', category_id=request.form.get('category_id')))


@transaction_bp.route('/transactions/edit/<int:transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)

    if request.method == 'POST':
        try:
            data = extract_transaction_date(request.form)
            for key, value in data.items():
                setattr(transaction, key, value)
            db.session.commit()
            calculate_budget(transaction.user_id, transaction.category_id)  # cập nhật ngân sách
            flash('Cập nhật thành công')
            return redirect(url_for('transaction.all_transactions', category_id=data['category_id']))
        except Exception as e:
            db.session.rollback()
            flash('Cập nhật thất bại')
        return redirect(url_for('transaction.all_transactions', category_id=data['category_id']))


@transaction_bp.route('/transactions/delete/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    category_id = transaction.category_id
    try:
        db.session.delete(transaction)
        db.session.commit()
        calculate_budget(transaction.user_id, category_id)  # cập nhật ngân sách
        flash('Xóa thành công')
    except Exception as e:
        db.session.rollback()
        flash('Xóa thất bại')
    return redirect(url_for('transaction.all_transactions', category_id=category_id))

