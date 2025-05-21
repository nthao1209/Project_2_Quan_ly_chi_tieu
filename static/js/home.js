let currentViewDate = new Date();

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
    const navButtons = document.querySelectorAll('.nav-btn');
    
    navButtons.forEach(button => {
        button.addEventListener('click', function() {
            const text = this.textContent.trim();
            let url = '/';
            
            switch(text) {
                case 'Danh mục':
                    url = '/categories-page';
                    break;
                case 'Tài khoản':
                    url = '/bank_account';
                    break;
                case 'Phân tích':
                    url = '/analytics';
                    break;
                case 'Ngân sách':
                    url = '/budgets';
                    break;
                case 'Mục tiêu tiết kiệm':
                    url='/home_saving_goal';
                    break;
                default:
                    return;
            }
            
            window.location.href = url;
        });
    });

    const floatingBtn = document.querySelector('.floating-btn');
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

    // Nhóm giao dịch theo ngày
    const grouped = {};
    transactions.forEach(trans => {
        if (!grouped[trans.transaction_date]) {
            grouped[trans.transaction_date] = [];
        }
        grouped[trans.transaction_date].push(trans);
    });



    // Duyệt qua từng ngày và tạo phần tử hiển thị
    Object.keys(grouped).sort((a, b) => new Date(b) - new Date(a)).forEach(date => {
        const dateGroup = document.createElement('div');
        dateGroup.className = 'transaction-date-group';

        const dateTitle = document.createElement('div');
        dateTitle.className = 'transaction-date-title';
        dateTitle.textContent = date; 
        dateGroup.appendChild(dateTitle);

        grouped[date].forEach(trans => {
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
            box.addEventListener('click', () => showTransactionDetail(trans));
            dateGroup.appendChild(box);
        });

        container.appendChild(dateGroup);
    });

    // Hàm hiển thị chi tiết (giữ nguyên)
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
                    <p>Ghi chú: ${trans.note}</p>
                </div>
            </div>
        `;

        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = detailHTML;
        document.body.appendChild(modal);
        document.body.classList.add('modal-open');

        modal.querySelector('.close-btn').addEventListener('click', () => {
            document.body.removeChild(modal);
            document.body.classList.remove('modal-open');
        });

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

    const dateGroups = document.querySelectorAll('.transaction-date-group');
    dateGroups.forEach(group => {
        const visibleTransactions = group.querySelectorAll('.recent-transaction-box[style="display: flex;"]');
        group.style.display = visibleTransactions.length > 0 ? 'block' : 'none';
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

document.getElementById("deleteAccountLink").addEventListener("click", function (e) {
    e.preventDefault();

    if (confirm("Bạn có chắc chắn muốn xóa tài khoản? Hành động này không thể hoàn tác.")) {
        fetch("/delete_account", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
        })
        .then((response) => {
            if (response.ok) {
                alert("Tài khoản đã bị xóa.");
                window.location.href = "/login"; 
            } else {
                response.json().then(data => {
                    alert("Lỗi: " + (data.message || "Không thể xóa tài khoản"));
                });
            }
        })
        .catch((error) => {
            alert("Lỗi kết nối: " + error.message);
        });
    }
});