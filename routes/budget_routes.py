
@app.route('/budgets', methods=['GET'])
def get_budgets():
    budgets = Budget.query.all()
    budget_list = [
        {
            "budget_id": b.budget_id,
            "user_id": b.user_id,
            "category_id": b.category_id,
            "limit_amount": float(b.limit_amount),
            "start_date": b.start_date.strftime("%Y-%m-%d"),
            "end_date": b.end_date.strftime("%Y-%m-%d")
        }
        for b in budgets
    ]

    return jsonify(budget_list)
