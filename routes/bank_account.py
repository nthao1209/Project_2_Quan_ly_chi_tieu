from flask import Blueprint, jsonify, request, session, render_template
from models import db, Account
from datetime import datetime


bank_account_bp = Blueprint('bank_account', __name__)

@bank_account_bp.route('/bank_account', methods=['GET'])
def get_bank_accounts():
    user_id = session.get('user_id')
    # Kiểm tra xem người dùng đã đăng nhập chưa
    if not user_id:
        return  jsonify ({'error': 'Người dùng chưa đăng nhập.'}), 401
    # Lấy danh sách tài khoản ngân hàng của người dùng từ cơ sở dữ liệu
    accounts = Account.query.filter_by(user_id=user_id).all()

    if not accounts:
           default_account = Account(
            user_id=user_id,
            account_name='Tài khoản mặc định',
            balance=0,
            currency='VND',
            is_default=True,
            created_at=datetime.now()
            )
           db.session.add(default_account)
           db.session.commit()
           accounts = [default_account]

    
    return render_template('bank_account.html', accounts=accounts)


def add_update_similar(data,is_update=False,account_id=None):
    user_id = session.get('user_id')
    account_name = data.get('account_name')
    # Kiểm tra xem người dùng đã đăng nhập chưa
    if not user_id or not account_name:
        return jsonify({'error': 'Tất cả các trường đều bắt buộc.'}), 400
    
    currency = data.get('currency','VND')
    balance = float(data.get('balance', 0))

    # Nếu là cập nhật tài khoản, tìm tài khoản cần sửa
    if is_update:
        account = Account.query.get(account_id)
        if not account:
            return jsonify({'error': 'Tài khoản ngân hàng không tồn tại.'}), 404
        if account.user_id != user_id:
            return jsonify({'error': 'Bạn không có quyền sửa tài khoản này.'}), 403
    else:
        # Nếu là thêm tài khoản mới
        account = Account(
            user_id=user_id,
            account_name=account_name,
            balance=balance,
            currency=currency
        )

    # Cập nhật các thông tin cho tài khoản
    account.account_name = account_name
    account.balance = balance
    account.currency = currency

    # Lưu vào cơ sở dữ liệu
    if not is_update:
        db.session.add(account)  # Thêm mới tài khoản
    db.session.commit()

    if is_update:
        return jsonify({'message': 'Tài khoản ngân hàng đã được cập nhật thành công.'}), 200
    else:
        return jsonify({'message': 'Tài khoản ngân hàng đã được thêm thành công.'}), 201
    
# Thêm tài khoản ngân hàng mới
@bank_account_bp.route('/bank_account/add', methods=['POST'])
def add_bank_accounts():
    data = request.get_json()
    print("Dữ liệu nhận được để thêm tài khoản ngân hàng:", data)
    return add_update_similar(data,is_update=False)

# Cập nhật tài khoản ngân hàng
@bank_account_bp.route('/bank_account/update/<int:account_id>', methods=['POST'])
def update_bank_account(account_id):
    data = request.get_json()
    print(f"Updating account {account_id} with data: {data}")

    return add_update_similar(data,is_update=True,account_id=account_id)    

# Xóa tài khoản ngân hàng
@bank_account_bp.route('/bank_account/<int:account_id>', methods=['DELETE'])
def delete_bank_account(account_id):

    print(f"Attempting to delete account with ID: {account_id}")

    account = Account.query.get(account_id)
    
    if not account:
        return jsonify({'error': 'Tài khoản ngân hàng không tồn tại.'}), 404
    
    db.session.delete(account)
    db.session.commit()
    return jsonify({'message': 'Tài khoản ngân hàng đã được xóa thành công.'}), 200

@bank_account_bp.route('/bank_account/set_default/<int:account_id>', methods=['POST'])
def set_default_bank_account(account_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Người dùng chưa đăng nhập.'}), 401

    # Đặt tất cả tài khoản về không mặc định
    Account.query.filter_by(user_id=user_id).update({'is_default': False})
    db.session.commit()

    # Đặt tài khoản được chọn làm mặc định
    account = Account.query.get(account_id)
    if not account or account.user_id != user_id:
        return jsonify({'error': 'Tài khoản không tồn tại hoặc không thuộc về người dùng.'}), 404

    account.is_default = True
    db.session.commit()

    # Trả về thông tin tài khoản để cập nhật giao diện
    return jsonify({
        'message': 'Tài khoản đã được đặt làm mặc định.',
        'account': {
            'account_name': account.account_name,
            'balance': account.balance,
            'currency': account.currency
        }
    }), 200


@bank_account_bp.route('/bank_account/<int:account_id>', methods=['GET'])
def get_single_bank_account(account_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Người dùng chưa đăng nhập.'}), 401

    account = Account.query.get(account_id)
    if not account:
        return jsonify({'error': 'Tài khoản không tồn tại.'}), 404
    if account.user_id != user_id:
        return jsonify({'error': 'Bạn không có quyền truy cập tài khoản này.'}), 403

    return jsonify({
        'account_name': account.account_name,
        'currency': account.currency,
        'balance': account.balance
    })

