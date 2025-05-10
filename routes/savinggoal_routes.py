from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from models import SavingsGoal, db, DepositTransaction
from datetime import datetime

saving_goal_bp = Blueprint('saving_goal', __name__)

def parse_goal_data(data, goal=None):
    
    raw_amount = data['target_amount']

    if not raw_amount:
      raise ValueError("Số tiền mục tiêu không được để trống.")

    if isinstance(raw_amount, str):
        raw_amount = raw_amount.replace(',', '').replace(' ', '')

    target_amount = float(raw_amount)
    if target_amount <= 0:
        raise ValueError("Số tiền mục tiêu phải lớn hơn 0.")

    if goal:
        goal.name = data.get('name', goal.name).strip()
        goal.target_amount = target_amount
        if 'start_time' in data:
            goal.start_time = datetime.strptime(data['start_time'], '%Y-%m-%d').date()
        if 'end_time' in data:
            goal.end_time = datetime.strptime(data['end_time'], '%Y-%m-%d').date()
        goal.note = data.get('note', goal.note)
        return goal
    else:
        return SavingsGoal(
            user_id=session.get('user_id'),
            name=data['name'].strip(),
            target_amount=target_amount,
            start_time=datetime.strptime(data['start_time'], '%Y-%m-%d').date(),
            end_time=datetime.strptime(data['end_time'], '%Y-%m-%d').date(),
            note=data.get('note')
        )


@saving_goal_bp.route('/home_saving_goal',methods=['GET'])
def home_saving_goal():
    user_id=session.get('user_id')
    if not user_id:
        return "Bạn chưa đăng nhập",401
    goals = SavingsGoal.query.filter_by(user_id=user_id).all()

    return render_template('home_saving_goal.html',goals=goals)

@saving_goal_bp.route('/detail_saving_goal',methods=['GET'])
def detail_saving_goal():
    user_id=session.get('user_id')
    if not user_id:
        return "Bạn chưa đăng nhập",401
    goals = SavingsGoal.query.filter_by(user_id=user_id).all()

    goals_with_progress = []
    for goal in goals:
        total_deposited = db.session.query(db.func.sum(DepositTransaction.deposit_amount)).filter(DepositTransaction.goal_id == goal.goal_id).scalar() or 0
        
        if goal.target_amount > 0:
            completion_percentage = (total_deposited / goal.target_amount) * 100
        else:
            completion_percentage = 0
        
        goals_with_progress.append({
            'goal': goal,
            'total_deposited': total_deposited,
            'completion_percentage': completion_percentage
        })


    return render_template('detail_saving_goal.html', goals_with_progress=goals_with_progress,goals=goals)



#  Danh sách mục tiêu
@saving_goal_bp.route('/goals', methods=['GET'])
def get_goals():
    user_id = session.get('user_id')
    goals = SavingsGoal.query.filter_by(user_id=user_id).all()
    return render_template('saving_goal.html', goals=goals)

#  Thêm mục tiêu
@saving_goal_bp.route('/goals/add', methods=['POST'])
def add_goal():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dữ liệu không hợp lệ hoặc không có dữ liệu JSON"}), 400

    try:
        if not session.get('user_id'):
            return jsonify({"error": "Chưa đăng nhập"}), 401

        goal = parse_goal_data(data)
        db.session.add(goal)
        db.session.commit()
        return jsonify({'message': 'Đã thêm mục tiêu', 'goal_id': goal.goal_id}), 201

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

#  Xem chi tiết mục tiêu
@saving_goal_bp.route('/goals/detail/<int:goal_id>', methods=['GET'])
def get_goal(goal_id):
    goal = SavingsGoal.query.get(goal_id)
    if not goal:
        return jsonify({'error': 'Không tìm thấy mục tiêu'}), 404

    return jsonify({
        'goal_id': goal.goal_id,
        'name': goal.name,
        'target_amount': float(goal.target_amount),
        'start_time': goal.start_time.strftime('%Y-%m-%d'),
        'end_time': goal.end_time.strftime('%Y-%m-%d'),
        'note': goal.note
    })

#  Cập nhật mục tiêu
@saving_goal_bp.route('/goals/update/<int:goal_id>', methods=['PUT'])
def update_goal(goal_id):
    goal = SavingsGoal.query.get(goal_id)
    if not goal:
        return jsonify({'error': 'Không tìm thấy mục tiêu'}), 404

    data = request.get_json()
    print(f"Dữ liệu nhận được để cập nhật: {data}")
    try:
        data = request.get_json()
        goal = parse_goal_data(data, goal)
        db.session.commit()
        return jsonify({'message': 'Đã cập nhật mục tiêu', 'goal_id': goal.goal_id}), 200
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Xóa mục tiêu
@saving_goal_bp.route('/goals/delete/<int:goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
     try:
        goal = SavingsGoal.query.get(goal_id)
        if not goal:
            return jsonify({'error': 'Không tìm thấy mục tiêu'}), 404
        
        DepositTransaction.query.filter_by(goal_id=goal_id).delete()
    
    
        db.session.delete(goal)
        db.session.commit()
        return jsonify({'message': f'Đã xóa mục tiêu {goal_id}'})
     except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
