from flask import Blueprint, request, jsonify, redirect, url_for, render_template, session
from . import db
from models import DepositTransaction , SavingsGoal, Account
from datetime import datetime
from decimal import Decimal
import traceback

deposit_bp = Blueprint('deposit_bp', __name__)


@deposit_bp.route('/deposit', methods=['GET'])
def show_deposit_form():
    user_id=session.get('user_id')
    if not user_id:        
        return redirect(url_for('user_bp.login'))
    goals = SavingsGoal.query.all()

    accounts = Account.query.filter_by(user_id=user_id).all()
    if not accounts:
      print("No accounts found for this user.")
    
    selected_goal_id = request.args.get('goal_id')  # Lấy goal_id từ URL

    return render_template('deposit_transactions.html', goals=goals, accounts=accounts, selected_goal_id=selected_goal_id)

@deposit_bp.route('/deposit', methods=['POST'])
def deposit_money():
    try:
        data = request.get_json()  # Nhận dữ liệu từ client
        
        goal_id = data.get('goal_id')
        deposit_amount = Decimal(data.get('deposit_amount'))
        from_account_id = data.get('from_account')
        to_account_id = data.get('to_account')
        
        # Kiểm tra dữ liệu nhập vào
        if not goal_id or not deposit_amount or not from_account_id or not to_account_id:
            return jsonify({'error': 'Thiếu thông tin cần thiết'}), 400
        
        # Kiểm tra xem mục tiêu tiết kiệm có tồn tại không
        goal = SavingsGoal.query.get(goal_id)
        if not goal:
            return jsonify({'error': 'Mục tiêu không tồn tại'}), 404
        
        # Kiểm tra tài khoản gửi và nhận có tồn tại không
        from_account = Account.query.get(from_account_id)
        to_account = Account.query.get(to_account_id)
        if not from_account or not to_account:
            return jsonify({'error': 'Tài khoản không hợp lệ'}), 404
        
        # Kiểm tra số dư tài khoản gửi
        from_account_balance = float(from_account.balance)
        if from_account.balance < deposit_amount:
            return jsonify({'error': 'Số dư tài khoản gửi không đủ'}), 400
        
        # Thực hiện giao dịch nạp tiền
        deposit_transaction = DepositTransaction(
            goal_id=goal_id,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            deposit_amount=deposit_amount,
            deposit_date=datetime.utcnow()
        )
        db.session.add(deposit_transaction)
        
        # Cập nhật số dư tài khoản gửi và nhận
        from_account.balance -= deposit_amount
        to_account.balance += deposit_amount
        db.session.commit()
        
        # Cập nhật tiến độ hoàn thành mục tiêu
        total_deposited = sum(txn.deposit_amount for txn in goal.deposit_transactions)
        completion_percentage = (total_deposited / goal.target_amount) * 100
        
        # Trả về kết quả
        return jsonify({'message': 'Nạp tiền thành công'}), 200

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
