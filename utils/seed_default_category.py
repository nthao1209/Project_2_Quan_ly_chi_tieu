from models import db, Category

def seed_default_categories():
    expenses_categories = [
        {'name': 'Ăn uống', 'icon': '🍔','type':'Chi tiêu'},
        {'name': 'Đi lại', 'icon': '🚗','type':'Chi tiêu'},
        {'name': 'Thuế', 'icon': '🏦','type':'Chi tiêu'},
        {'name': 'Giải trí', 'icon': '🎮','type':'Chi tiêu'},
        {'name': 'Hóa đơn', 'icon': '🧾','type':'Chi tiêu'},
        {'name': 'Mua sắm', 'icon': '🛍️','type':'Chi tiêu'},
        {'name': 'Sức khỏe', 'icon': '🏥','type':'Chi tiêu'},
        {'name': 'Giáo dục', 'icon': '🎓','type':'Chi tiêu'},
        {'name': 'Vật nuôi', 'icon': '🐈','type':'Chi tiêu'}
    ]
    
    for category in expenses_categories:
        # Chỉ check các category mặc định (user_id=None)
        existing_category = Category.query.filter_by(name=category['name'], user_id=None).first()
        if not existing_category:
            new_category = Category(
                name=category['name'],
                icon=category['icon'],
                type=category['type'],
                user_id=None  # Quan trọng: gán user_id = None để là mặc định dùng chung              
            )
            db.session.add(new_category)

    db.session.commit()
