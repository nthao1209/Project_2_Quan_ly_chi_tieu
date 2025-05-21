from flask import Blueprint, request, jsonify, session, render_template
from . import db
from models import Account, TransferTransaction
import traceback 
transfer_bp = Blueprint('transfer', __name__)


@transfer_bp.route('/transfer', methods=['POST'])
def transfer_money():
    data = request.get_json()
    user_id = session.get('user_id')
    from_account_id = data.get('from_account_id')
    to_account_id = data.get('to_account_id')
    amount = data.get('amount')
    note = data.get('note', '')



    if not all([user_id, from_account_id, to_account_id, amount]):
        return jsonify({'error': 'Thiếu thông tin cần thiết'}), 400
    if from_account_id == to_account_id:
        return jsonify({'error': 'Không thể chuyển vào cùng tài khoản'}), 400

    from_account = Account.query.get(from_account_id)
    to_account = Account.query.get(to_account_id)

    if not from_account or not to_account:
        return jsonify({'error': 'Tài khoản không tồn tại'}), 404
    if from_account.user_id != user_id or to_account.user_id != user_id:
        return jsonify({'error': 'Tài khoản không thuộc về người dùng'}), 403
    if from_account.balance < amount:
        return jsonify({'error': 'Số dư không đủ'}), 400

    try:
        # 1. Cập nhật số dư
        from_account.balance -= amount
        to_account.balance += amount

        # 2. Tạo bản ghi chuyển tiền
        transfer = TransferTransaction(
            user_id=user_id,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            note=note
        )
        db.session.add(transfer)

        db.session.commit()
        return jsonify({'message': 'Chuyển tiền thành công'}), 200

    except Exception as e:
        db.session.rollback()
        print("❌ LỖI CHUYỂN TIỀN ❌")
        print("Dữ liệu nhận được:", data)
        print("user_id:", user_id)
        print("from_account_id:", from_account_id)
        print("to_account_id:", to_account_id)
        print("amount:", amount)
        print("note:", note)
        print("=== TRACEBACK ===")
        traceback.print_exc()   

        return jsonify({'error': 'Lỗi khi chuyển tiền', 'details': str(e)}), 500
    
@transfer_bp.route('/transfer/home', methods=['GET'])
def transfer():
    return render_template('transfer_transactions.html')

@transfer_bp.route('/transfer/accounts', methods=['GET'])
def get_user_accounts():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Chưa đăng nhập'}), 401

    accounts = Account.query.filter_by(user_id=user_id).all()
    account_list = [{
        'account_id': acc.account_id,
        'account_name': acc.account_name,
        'balance': acc.balance,
        'currency': acc.currency
    } for acc in accounts]

    return jsonify({'accounts': account_list})

