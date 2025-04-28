document.addEventListener('DOMContentLoaded', function () {
    // Gán sự kiện cho các nút xóa tài khoản
    document.querySelectorAll('.delete-account').forEach(btn => {
        btn.addEventListener('click', function () {
            const accountId = this.dataset.account_id;
            deleteAccount(accountId);
        });
    });

    // Gán sự kiện cho form cập nhật tài khoản
    document.getElementById('update-account-form').addEventListener('submit', function (e) {
        e.preventDefault();

        const formContainer = document.getElementById('update-account-form-container');
        const accountId = formContainer.dataset.accountId;

        const updatedData = {
            account_name: document.getElementById('account_name').value,
            currency: document.getElementById('currency').value,
            balance: document.getElementById('balance').value
        };

        fetch(`/bank_account/update/${accountId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updatedData)
        })
            .then(res => res.json())
            .then(data => {
                if (data.message) {
                    alert('Cập nhật thành công!');
                    location.reload();
                } else {
                    alert('Cập nhật thất bại!');
                }
            })
            .catch(error => {
                console.error('Lỗi khi cập nhật tài khoản:', error);
                alert('Đã có lỗi xảy ra khi cập nhật!');
            });
    });

    // Gán sự kiện cho nút "Hủy" form cập nhật
    document.getElementById('cancel-update').addEventListener('click', function () {
        document.getElementById('update-account-form-container').style.display = 'none';
    });
});

// Thêm tài khoản mới
function addAccount() {
    const list = document.getElementById('accountList');
    const div = document.createElement('div');
    div.className = 'account-item';
    div.innerHTML = `
        <input type="text" name="account_name" placeholder="Tên tài khoản" class="new_account_name">
        <input type="number" name="balance" placeholder="Số dư" required>
        <input type="text" name="currency" placeholder="Loại tiền tệ" required>
        <button onclick="saveAccount(this)">Lưu</button>
        <button onclick="cancelAccount(this)">Hủy</button>`;
    list.appendChild(div);
}

// Lưu tài khoản mới
function saveAccount(button) {
    const nameInput = button.parentElement.querySelector('.new_account_name');
    const accountName = nameInput.value;

    if (!accountName.trim()) {
        alert('Vui lòng nhập tên tài khoản');
        return;
    }

    fetch('/bank_account/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            account_name: accountName,
            balance: button.parentElement.querySelector('input[name="balance"]').value,
            currency: button.parentElement.querySelector('input[name="currency"]').value
        })
    })
        .then(res => res.json())
        .then(data => {
            if (data.message) {
                alert('Thêm tài khoản thành công!');
                location.reload();
            } else {
                alert('Có lỗi xảy ra khi thêm tài khoản!');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Có lỗi xảy ra khi thêm tài khoản!');
        });
}

// Hủy thêm tài khoản
function cancelAccount(button) {
    button.parentElement.remove();
}

// Xóa tài khoản
function deleteAccount(account_id) {
    fetch(`/bank_account/${account_id}`, {
        method: 'DELETE',
    })
        .then(res => res.json())
        .then(data => {
            if (data.message) {
                alert('Xóa tài khoản thành công!');
                location.reload();
            } else {
                alert('Có lỗi xảy ra khi xóa tài khoản!');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Có lỗi xảy ra khi xóa tài khoản!');
        });
}

// Đặt tài khoản làm mặc định
function setAsDefault(account_id) {
    fetch(`/bank_account/set_default/${account_id}`, {
        method: 'POST',
    })
        .then(res => res.json())
        .then(data => {
            if (data.message) {
                alert('Đã đặt tài khoản này làm mặc định!');
                location.reload();
            } else {
                alert('Có lỗi xảy ra khi đặt tài khoản này làm mặc định!');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Có lỗi xảy ra khi đặt tài khoản này làm mặc định!');
        });
}

// Hiển thị form cập nhật
function showUpdateForm(account_id) {
    const formContainer = document.getElementById('update-account-form-container');
    formContainer.style.display = 'block';

    fetch(`/bank_account/${account_id}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById('account_name').value = data.account_name;
            document.getElementById('currency').value = data.currency;
            document.getElementById('balance').value = data.balance;
            formContainer.dataset.accountId = account_id;
        })
        .catch(error => {
            console.error('Lỗi khi lấy thông tin tài khoản:', error);
            alert('Không thể tải dữ liệu tài khoản.');
        });
}
