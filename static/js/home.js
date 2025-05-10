let currentViewDate = new Date();

// DOM Content Loaded event
document.addEventListener('DOMContentLoaded', function() {
    // Xử lý dropdown avatar
    const avatar = document.querySelector('.avatar-wrapper');
    const dropdown = document.querySelector('.dropdown-content');

    if (avatar && dropdown) {
        avatar.addEventListener('click', function(event) {
            event.stopPropagation();
            dropdown.style.display = (dropdown.style.display === 'none' || dropdown.style.display === '') ? 'block' : 'none';
        });

        document.addEventListener('click', function(event) {
            if (!avatar.contains(event.target) && !dropdown.contains(event.target)) {
                dropdown.style.display = 'none';
            }
        });
    }

    // Xử lý các nút điều hướng
    setupNavigationButtons();

    // Initialize month display and fetch transactions
    updateMonthDisplay();
    fetchTransactions();

    // Event listeners for month navigation
    document.getElementById('prevMonth').addEventListener('click', () => {
        currentViewDate.setMonth(currentViewDate.getMonth() - 1);
        updateMonthDisplay();
        fetchTransactions();
    });

    document.getElementById('nextMonth').addEventListener('click', () => {
        currentViewDate.setMonth(currentViewDate.getMonth() + 1);
        updateMonthDisplay();
        fetchTransactions();
    });

    // Event listeners for transaction tabs
    document.querySelectorAll('.filter-buttons button').forEach(button => {
        button.addEventListener('click', () => {
            document.querySelectorAll('.filter-buttons button').forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            filterTransactions(button.dataset.type);
        });
    });
});

function setupNavigationButtons() {
    const categoryBtn = document.querySelector('.category-btn');
    const accountBtn = document.querySelector('.account-btn');
    const analyticsBtn = document.querySelector('.analytics-btn');
    const budgetBtn = document.querySelector('.budget-btn');
    const savingGoalBtn = document.querySelector('.saving-goal-btn');
    const floatingBtn = document.querySelector('.floating-btn');

    if (categoryBtn) {
        categoryBtn.addEventListener('click', e => {
            e.preventDefault();
            window.location.href = '/categories-page';
        });
    }
    if (accountBtn) {
        accountBtn.addEventListener('click', e => {
            e.preventDefault();
            window.location.href = '/bank_account';
        });
    }
    if (analyticsBtn) {
        analyticsBtn.addEventListener('click', e => {
            e.preventDefault();
            window.location.href = '/analytics';
        });
    }
    if (budgetBtn) {
        budgetBtn.addEventListener('click', e => {
            e.preventDefault();
            window.location.href = '/budgets';
        });
    }
    if (savingGoalBtn) {
        savingGoalBtn.addEventListener('click', e => {
            e.preventDefault();
            window.location.href = '/home_saving_goal';
        });
    }
    if (floatingBtn) {
        floatingBtn.addEventListener('click', e => {
            e.preventDefault();
            window.location.href = '/transactions/add_form';
        });
    }
}

async function fetchTransactions() {
    const month = currentViewDate.getMonth() + 1;
    const year = currentViewDate.getFullYear();
    try {
        const response = await fetch(`/transactions/recent?month=${month}&year=${year}`);
        if (!response.ok) throw new Error('Không thể tải giao dịch');
        const transactions = await response.json();
        updateRecentTransactions(transactions);
        updateFinancialSummary(transactions);
    } catch (error) {
        console.error('Error fetching transactions:', error);
        showErrorMessage('Không thể tải dữ liệu giao dịch');
    }
}

function updateMonthDisplay() {
    const month = currentViewDate.getMonth() + 1;
    const year = currentViewDate.getFullYear();
    document.getElementById('currentMonthYear').textContent = `Tháng ${month}/${year}`;
}

function updateRecentTransactions(transactions) {
    const container = document.querySelector('.recent-transactions');
    if (!container) return;

    container.innerHTML = '';

    if (transactions.length === 0) {
        container.innerHTML = '<div class="no-transactions">Không có giao dịch nào trong tháng này</div>';
        return;
    }

    transactions.forEach(trans => {
        const box = document.createElement('div');
        box.className = 'recent-transaction-box';
        box.setAttribute('data-type', trans.type);
        box.innerHTML = `
            <div class="transaction-category">
                <div class="category-icon">${trans.icon}</div>
                <div>
                    <div>${trans.category_name}</div>
                    <div style="font-size: 12px; color: #777;">${trans.account_name}</div>
                </div>
            </div>
            <div class="transaction-amount ${trans.type}">
                ${trans.type === 'income' ? '+' : '-'}${formatNumber(trans.amount)} ₫
            </div>
        `;

        box.addEventListener('click', () =>  showTransactionDetail(trans));
        container.appendChild(box);
    });

    // Hàm hiển thị chi tiết giao dịch
function showTransactionDetail(trans) {
    const detailHTML = `
        <div class="transaction-detail-modal">
            <div class="modal-header">
                <span class="close-btn">&times;</span>
                <div class="action-icons">
                    <i class="fas fa-edit edit-btn" title="Chỉnh sửa"></i>
                    <i class="fas fa-trash-alt delete-btn" title="Xóa"></i>
                </div>
            </div>
            <div class="modal-content">
                <div class="category-icon">${trans.icon} ${trans.category_name} </div>
                <p>Số tiền: ${trans.type === 'income' ? '+' : '-'} ${formatNumber(trans.amount)} ₫</p>
                <p>Ngày: ${trans.transaction_date}</p>
                <p>Giờ: ${trans.transaction_time}</p>
                <p>Tài khoản: ${trans.account_name}</p>
            </div>
        </div>
    `;

    // Tạo và thêm modal vào body
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = detailHTML;
    document.body.appendChild(modal);

    document.body.classList.add('modal-open'); // Thêm class để khóa cuộn trang

    // Thêm sự kiện đóng modal
    modal.querySelector('.close-btn').addEventListener('click', () => {
        document.body.removeChild(modal);
        document.body.classList.remove('modal-open'); // Bỏ class khóa cuộn trang
    });
    // Gắn sự kiện xóa
    modal.querySelector('.delete-btn').addEventListener('click', () => {
        if (confirm('Bạn có chắc chắn muốn xóa giao dịch này?')) {
            fetch(`/transactions/delete/${trans.transaction_id}`, {
                method: 'POST'
            })
            .then(res => {
                if (res.ok) location.reload();
                else alert('Xóa thất bại.');
            });
        }
    });

// Gắn sự kiện chỉnh sửa
modal.querySelector('.edit-btn').addEventListener('click', () => {
    window.location.href = `/transactions/edit/${trans.transaction_id}`;
});

}
}


function updateFinancialSummary(transactions) {
    const incomeElement = document.getElementById('incomeAmount');
    const expenseElement = document.getElementById('expenseAmount');
    const balanceElement = document.getElementById('balanceAmount');

    if (!incomeElement || !expenseElement || !balanceElement) return;

    const totalIncome = transactions
        .filter(trans => trans.type === 'income')
        .reduce((sum, trans) => sum + parseFloat(trans.amount), 0);
    const totalExpense = transactions
        .filter(trans => trans.type === 'expense')
        .reduce((sum, trans) => sum + parseFloat(trans.amount), 0);
    const balance = totalIncome - totalExpense;

    incomeElement.textContent = `${formatNumber(totalIncome)} ₫`;
    expenseElement.textContent = `${formatNumber(totalExpense)} ₫`;
    balanceElement.textContent = `${formatNumber(balance)} ₫`;
}

function filterTransactions(type) {
    const transactions = document.querySelectorAll('.recent-transaction-box');
    if (!transactions) return;

    transactions.forEach(trans => {
        const transType = trans.dataset.type;
        trans.style.display = type === 'all' ? 'flex' :
                            type === 'income' && transType === 'income' ? 'flex' :
                            type === 'expense' && transType === 'expense' ? 'flex' : 'none';
    });
}

function formatNumber(num) {
    return new Intl.NumberFormat('vi-VN').format(num);
}

function showErrorMessage(message) {
    const notification = document.createElement('div');
    notification.className = 'error-notification';
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}