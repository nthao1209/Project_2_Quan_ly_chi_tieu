document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.delete-account').forEach(btn=> {
        btn.addEventListener('click',function() {
            const accountId = this.dataset.account_id;
            deleteAccount(accountId);
        });
    });
});

function goBack(){
    window.history.back();  // Trở về trang trước đó
}

function addAccount() {
    const list = document.getElementById('accountList');
    const div = document.createElement('div');
    div.className = 'account-item';
    div.innerHTML = `
        <input type="text" name="account_name" placeholder="Tên tài khoản" class="new_account_name">
        <input type="integer" name="balance" placeholder="Số dư" required>
        <input type = "text" name="currency" placeholder="Loại tiền tệ" required>
        <button onclick="saveAccount(this)">Lưu</button>
        <button onclick="cancelAccount(this)">Hủy</button> `;
    list.appendChild(div);
}

function saveAccount(button) {
    const nameInput= button.parentElement.querySelector('.new_account_name');
    const accountName = nameInput.value;

    if(!accountName.trim()){
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
    .then(res=> res.json())
    .then(data=> {
        if(data.success){
            alert('Thêm tài khoản thành công!');
            location.reload();
        } else {
            alert('Có lỗi xảy ra!');
        }
    })
    .catch(error=> {
        console.error('Error:', error);
        alert('Có lỗi xảy ra khi thêm tài khoản!');
    });
}

function deleteAccount(account_id){
    fetch(`/bank_account/${account_id}`, {
        method: 'DELETE',
    })
    .then(res=> res.json()) 
    .then(data=> {
        if(data.success){
            alert('Xóa tài khoản thành công!');
            location.reload();
        } else {
            alert('Có lỗi xảy ra khi xóa tài khoản!');
        }
    })
    .catch(error=> {
        console.error('Error:', error);
        alert('Có lỗi xảy ra khi xóa tài khoản!');
    });
}






