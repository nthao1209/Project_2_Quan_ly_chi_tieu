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
    return render_template('bank_account.html', accounts=accounts)

@bank_account_bp.route('/bank_account/add', methods=['POST'])
def add_bank_accounts():
    data = request.get_json()
    user_id = session.get('user_id')
    account_name = data.get('account_name')
    # Kiểm tra xem người dùng đã đăng nhập chưa
    if not user_id or not account_name :
        return jsonify({'error': 'Tất cả các trường đều bắt buộc.'}), 400
    
    currency = data.get('currency','VND')
    balance = data.get('balance', 0)

    
    new_account = Account(
        user_id=user_id,
        account_name=account_name,
        balance=balance,
        currency=currency                                   
    )
    db.session.add(new_account)
    db.session.commit()

    return jsonify({'message': 'Tài khoản ngân hàng đã được thêm thành công.'}), 201

@bank_account_bp.route('/bank_account/<int:account_id>', methods=['DELETE'])
def delete_bank_account(account_id):
    account = Account.query.get(account_id)

    if not account:
        return jsonify({'error': 'Tài khoản ngân hàng không tồn tại.'}), 404
    
    db.session.delete(account)
    db.session.commit()
    return jsonify({'message': 'Tài khoản ngân hàng đã được xóa thành công.'}), 200