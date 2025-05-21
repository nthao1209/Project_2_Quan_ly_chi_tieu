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
        document.getElementById('overlay').style.display = 'none'; // Ẩn overlay
    });
    document.getElementById('add-account-form').addEventListener('submit', function (e) {
        e.preventDefault();
        saveNewAccount();
    });

});

function addAccount() {
      document.getElementById('add-account-modal').style.display = 'block';
      document.getElementById('overlay').style.display = 'block'; // Hiển thị overlay
    }

    // Đóng modal thêm tài khoản
    function closeAddAccountModal() {
      document.getElementById('add-account-modal').style.display = 'none';
      document.getElementById('overlay').style.display = 'none'; // Ẩn overlay
    }

    // Lưu tài khoản mới
    function saveNewAccount() {
      const accountName = document.getElementById('new_account_name').value;
      const balance = document.getElementById('new_balance').value;
      const currency = document.getElementById('new_currency').value;

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
          balance: balance,
          currency: currency
        })
      })
      .then(res => res.json())
      .then(data => {
        if (data.message) {
          alert('Thêm tài khoản thành công!');
          location.reload(); // Reload lại trang
        } else {
          alert('Có lỗi xảy ra khi thêm tài khoản!');
        }
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Có lỗi xảy ra khi thêm tài khoản!');
      });

      closeAddAccountModal(); // Đóng form sau khi lưu thành công
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
    document.getElementById('overlay').style.display = 'block'; // Hiển thị overlay

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