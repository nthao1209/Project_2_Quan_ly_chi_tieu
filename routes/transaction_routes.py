from flask import Blueprint, jsonify, request, session, render_template, redirect, flash, url_for
from datetime import datetime
from decimal import Decimal
from models import db, Transaction, Category, Account, Budget
from calendar import monthrange

transaction_bp = Blueprint('transaction', __name__)

vi_to_type = {
    'Chi tiêu': 'expense',
    'Thu nhập': 'income'
}

def get_month_range(year, month):
    if month < 1 or month > 12:
        raise ValueError("Tháng không hợp lệ. Vui lòng nhập tháng từ 1 đến 12.")
    if year < 1:
        raise ValueError("Năm không hợp lệ. Vui lòng nhập năm dương lịch.")
    start_date = datetime(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = datetime(year, month, last_day, 23, 59, 59)
    return start_date, end_date

def get_budget_for_month(user_id, category_id, month, year):
    if not user_id or not category_id:
        raise ValueError('Người dùng hoặc danh mục không hợp lệ.')
    try:
        start_date, end_date = get_month_range(year, month)
        budget = Budget.query.filter(
            Budget.user_id == user_id,
            Budget.category_id == category_id,
            Budget.start_date <= end_date,
            Budget.end_date >= start_date
        ).first()

        return budget
    except ValueError as e:
        raise ValueError(f"Lỗi xác định ngân sách: {str(e)}")

def extract_transaction_date(form):
    user_id = session.get('user_id')
    if not user_id:
        raise ValueError('Người dùng không hợp lệ.')
    
    date_str = form.get('transaction_date')
    transaction_date = None

    # Kiểm tra và parse ngày giao dịch
    if date_str:
        date_str = date_str.strip()
        try:
            transaction_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            try:
                transaction_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                try:
                    transaction_date = datetime.strptime(date_str, '%Y-%m-%d')
                    transaction_date = transaction_date.replace(
                        hour=datetime.now().hour,
                        minute=datetime.now().minute,
                        second=datetime.now().second
                    )
                except ValueError:
                    raise ValueError('Ngày giao dịch không hợp lệ.')
    else:
        transaction_date = datetime.now()

    # Kiểm tra category
    category_id = int(form.get('category_id'))
    category = Category.query.filter_by(category_id=category_id, user_id=user_id).first()
    if not category:
        raise ValueError('Danh mục không hợp lệ hoặc không thuộc về bạn.')

    # Kiểm tra account
    raw_account_id = form.get('account_id')
    if raw_account_id:
        account = Account.query.filter_by(account_id=raw_account_id, user_id=user_id).first()
        if not account:
            raise ValueError('Tài khoản không hợp lệ.')
        account_id = account.account_id
    else:
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
        'user_id': user_id,
        'account_id': account_id,
        'category_id': category_id,
        'amount': Decimal(form.get('amount')),
        'transaction_type': transaction_type,
        'transaction_date': transaction_date,
        'note': form.get('note')
    }

def calculate_budget(user_id, category_id, transaction_date):
    if not user_id or not category_id or not isinstance(transaction_date, datetime):
        raise ValueError("Dữ liệu đầu vào không hợp lệ")
    
    budget = Budget.query.filter(
        Budget.user_id == user_id,
        Budget.category_id == category_id,
        Budget.start_date <= transaction_date,
        Budget.end_date >= transaction_date
    ).first()

    if not budget:
        return None
    
    total_amount = db.session.query(
        db.func.coalesce(db.func.sum(Transaction.amount), 0)
    ).filter(
        Transaction.user_id == user_id,
        Transaction.category_id == category_id,
        Transaction.transaction_type == 'expense',
        Transaction.transaction_date >= budget.start_date,
        Transaction.transaction_date <= budget.end_date
    ).scalar()

    return {
        'budget': budget,
        'amount_spent': total_amount,
        'remaining': budget.limit_amount - total_amount,
        'percentage': float(total_amount) / float(budget.limit_amount) * 100
    }

@transaction_bp.route('/transactions', methods=['GET'])
def all_transactions():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login.login'))

    # Lấy các tham số từ request
    category_id = request.args.get('category_id')
    month = request.args.get('month')
    year = request.args.get('year')
    account_id = request.args.get('account_id')
    transaction_type = request.args.get('transaction_type')

    # Query cơ bản
    query = Transaction.query.filter_by(user_id=user_id)
    accounts = Account.query.filter_by(user_id=user_id).all()
    category = None

    # Filter theo category
    if category_id:
        category = Category.query.filter_by(category_id=category_id, user_id=user_id).first()
        if category:
            transaction_type = vi_to_type.get(category.type, 'expense') if not transaction_type else transaction_type
            query = query.filter_by(category_id=category_id)
        
    if transaction_type not in ['expense', 'income']:
        transaction_type = 'expense'

    # Filter theo account
    if account_id and account_id != 'all':
        account = Account.query.filter_by(account_id=account_id, user_id=user_id).first()
        if account:
            query = query.filter_by(account_id=account_id)

    # Filter theo tháng/năm
    if month:
        try:
            month = int(month)
            query = query.filter(db.extract('month', Transaction.transaction_date) == month)
        except ValueError:
            flash('Tháng không hợp lệ.')

    if year:
        try:
            year = int(year)
            query = query.filter(db.extract('year', Transaction.transaction_date) == year)
        except ValueError:
            flash('Năm không hợp lệ.')

    filtered_transactions = query.all()
    total_count = len(filtered_transactions)
    total_amount = sum(t.amount for t in filtered_transactions) or 0

    # Tính toán budget
    budget_info = None
    if category_id:
        now = datetime.now()
        transaction_date = filtered_transactions[0].transaction_date if filtered_transactions else datetime(year or now.year, month or now.month, 15)
        budget_info = calculate_budget(user_id=user_id, category_id=category_id, transaction_date=transaction_date)

    remaining_budget = budget_info['remaining'] if budget_info else 0
    percentage = budget_info['percentage'] if budget_info else 0
    budget = budget_info['budget'] if budget_info else None

    if request.headers.get('Accept') == 'application/json':
        return jsonify({
            'total_count': total_count,
            'total_amount': total_amount,
            'remaining_budget': remaining_budget,
            'percentage': percentage,
            'budget': {
                'limit_amount': budget.limit_amount if budget else 0
            } if budget else None,
            'transactions': [{
                'transaction_id': t.transaction_id,
                'transaction_date': t.transaction_date.strftime('%Y-%m-%dT%H:%M:%S'),
                'amount': str(t.amount),
                'note': t.note or ''
            } for t in filtered_transactions]
        })
    
    return render_template('transaction.html',
                           transactions=filtered_transactions,
                           category=category,
                           accounts=accounts,
                           current_account_id=account_id,
                           budget=budget,
                           total_amount=total_amount,
                           remaining_budget=remaining_budget,
                           total_count=total_count,
                           percentage=percentage,
                           transaction_type=transaction_type)

@transaction_bp.route('/transactions/add', methods=['GET', 'POST'])
def add_transaction():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login.login'))
    
    if request.method == 'POST':
        try:
            data = extract_transaction_date(request.form)
            
            # Thêm kiểm tra bổ sung
            category = Category.query.filter_by(
                category_id=data['category_id'], 
                user_id=user_id
            ).first()
            if not category:
                raise ValueError('Danh mục không hợp lệ')
                
            account = Account.query.filter_by(
                account_id=data['account_id'], 
                user_id=user_id
            ).first()
            if not account:
                raise ValueError('Tài khoản không hợp lệ')
            
            if data['transaction_type'] == 'income':
                account.balance += data['amount']
            elif data['transaction_type'] == 'expense':
                account.balance -= data['amount']

            new_transaction = Transaction(**data)
            db.session.add(new_transaction)
            db.session.commit()
            
            # Cập nhật ngân sách
            budget_info = calculate_budget(data['user_id'], data['category_id'], data['transaction_date'])

            if request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'success': True,
                    'message': 'Ghi nhận thành công',
                    'transaction': {
                        'transaction_id': new_transaction.transaction_id,
                        'category_id': new_transaction.category_id,
                        'category_name': category.name,
                        'account_id': new_transaction.account_id,
                        'account_name': account.account_name,
                        'amount': str(new_transaction.amount),
                        'type': new_transaction.transaction_type,
                        'transaction_date': new_transaction.transaction_date.strftime('%Y-%m-%d'),
                        'note': new_transaction.note or ''
                    },
                    'budget': {
                        'remaining': budget_info['remaining'] if budget_info else 0,
                        'percentage': budget_info['percentage'] if budget_info else 0
                    }
                })

            flash('Ghi nhận thành công')
            return redirect(url_for('home.home'))
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            if request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 400
            flash('Ghi nhận thất bại: ' + str(e))
            return redirect(url_for('home.home'))
    
    return redirect(url_for('home.home'))

@transaction_bp.route('/transactions/delete/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login.login'))

    transaction = Transaction.query.filter_by(transaction_id=transaction_id, user_id=user_id).first()
    if not transaction:
        flash('Giao dịch không tồn tại hoặc bạn không có quyền xóa')
        return redirect(url_for('home.home'))

    category_id = transaction.category_id
    try:
        db.session.delete(transaction)
        db.session.commit()
        calculate_budget(user_id, category_id, transaction.transaction_date)
        flash('Xóa thành công')
    except Exception as e:
        db.session.rollback()
        flash('Xóa thất bại: ' + str(e))
    return redirect(url_for('transaction.all_transactions', category_id=category_id))

@transaction_bp.route('/transactions/add_form', methods=['GET'])
def add_transaction_form():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login.login'))

    accounts = Account.query.filter_by(user_id=user_id).all()
    categories = Category.query.filter_by(user_id=user_id).all()
    return render_template('transaction_form.html', accounts=accounts, categories=categories)

@transaction_bp.route('/transactions/recent', methods=['GET'])
def recent_transactions():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    month = request.args.get('month')
    year = request.args.get('year')
    
    query = Transaction.query.filter_by(user_id=user_id)
    if month:
        try:
            month = int(month)
            query = query.filter(db.extract('month', Transaction.transaction_date) == month)
        except ValueError:
            return jsonify({'error': 'Invalid month'}), 400
    if year:
        try:
            year = int(year)
            query = query.filter(db.extract('year', Transaction.transaction_date) == year)
        except ValueError:
            return jsonify({'error': 'Invalid year'}), 400
    
    transactions = query.join(Category, Transaction.category_id == Category.category_id)\
                       .join(Account, Transaction.account_id == Account.account_id)\
                       .order_by(Transaction.transaction_date.desc())\
                       .limit(50).all()
    
    return jsonify([{
        'transaction_id': t.transaction_id,
        'category_id': t.category_id,
        'category_name': t.category.name,
        'icon': t.category.icon,
        'account_id': t.account_id,
        'account_name': t.account.account_name,
        'amount': str(t.amount),
        'type': t.transaction_type,
        'transaction_date': t.transaction_date.strftime('%d-%m-%Y'),
        'transaction_time': t.transaction_date.strftime('%H:%M:%S'),
        'note': t.note or ''
    } for t in transactions])

@transaction_bp.route('/transactions/edit/<int:transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Vui lòng đăng nhập để chỉnh sửa giao dịch')
        return redirect(url_for('login.login'))

    transaction = Transaction.query.filter_by(transaction_id=transaction_id, user_id=user_id).first()
    if not transaction:
        flash('Giao dịch không tồn tại hoặc bạn không có quyền chỉnh sửa')
        return redirect(url_for('home.home'))

    categories = Category.query.filter_by(user_id=user_id).all()
    accounts = Account.query.filter_by(user_id=user_id).all()

    if request.method == 'POST':
        try:
            data = extract_transaction_date(request.form)
            
            # Kiểm tra category và account thuộc về user
            category = Category.query.filter_by(category_id=data['category_id'], user_id=user_id).first()
            if not category:
                raise ValueError('Danh mục không hợp lệ')
                
            account = Account.query.filter_by(account_id=data['account_id'], user_id=user_id).first()
            if not account:
                raise ValueError('Tài khoản không hợp lệ')

            # Cập nhật transaction
            transaction.amount = data['amount']
            transaction.note = data['note']
            transaction.transaction_type = data['transaction_type']
            transaction.category_id = data['category_id']
            transaction.account_id = data['account_id']
            transaction.transaction_date = data['transaction_date']

            db.session.commit()

            # Cập nhật ngân sách
            calculate_budget(user_id, data['category_id'], data['transaction_date'])

            if request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'success': True, 
                    'message': 'Cập nhật thành công!',
                    'transaction': {
                        'transaction_id': transaction.transaction_id,
                        'category_id': transaction.category_id,
                        'account_id': transaction.account_id,
                        'amount': str(transaction.amount),
                        'type': transaction.transaction_type,
                        'transaction_date': transaction.transaction_date.strftime('%Y-%m-%d'),
                        'note': transaction.note or ''
                    }
                })

            flash('Cập nhật thành công!')
            return redirect(url_for('home.home'))
        except ValueError as e:
            db.session.rollback()
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'success': False, 'message': str(e)}), 400
            flash(f'Cập nhật thất bại: {str(e)}')
            return redirect(url_for('home.home'))
        except Exception as e:
            db.session.rollback()
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'success': False, 'message': 'Có lỗi xảy ra khi chỉnh sửa giao dịch'}), 500
            flash('Cập nhật thất bại')
            return redirect(url_for('home.home'))

    return render_template('transaction_form.html',
                         transaction=transaction,
                         categories=categories,
                         accounts=accounts)