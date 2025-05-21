document.addEventListener('DOMContentLoaded', function() {
    // Thay thế phần setDefaultDate bằng code sau
    const todayInput = document.getElementById('todayInput');
    if (todayInput) {
      // Tạo nút "Bây giờ"
      const nowButton = document.getElementById('now-button');
      nowButton.addEventListener('click', function() {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        
        todayInput.value = `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;
      });
      
      todayInput.parentNode.appendChild(nowButton);
    }
  
    // Initialize category selection
        const categoryButtons = document.querySelectorAll('.category-item');
        const selectedCategoryId = document.getElementById('selectedCategory').value;

        categoryButtons.forEach(button => {
            button.addEventListener('click', function() {
                selectCategory(this);
            });

            if (selectedCategoryId && button.dataset.categoryId === selectedCategoryId) {
                button.classList.add('selected');
            }
        });

    // Initialize account selection
        const accountButtons = document.querySelectorAll('.account-grid button');
        const selectedAccountId = document.getElementById('selectedAccount').value;

        accountButtons.forEach(button => {
            button.addEventListener('click', function() {
                selectAccount(this);
            });

            if (selectedAccountId && button.dataset.accountId === selectedAccountId) {
                button.classList.add('selected');
                updateAccountIcon(button.querySelector('.name').textContent.trim());
            }
        });


    // Format currency on input
    const amountInput = document.querySelector('.amount-display');
    if (amountInput && amountInput.value) {
        formatCurrency({ target: amountInput });
    }

    amountInput.addEventListener('focus', handleFocus);
    amountInput.addEventListener('blur', formatCurrency);
    
    // Ensure correct value on form submit
    amountInput.form?.addEventListener('submit', function() {
        amountInput.value = amountInput.dataset.rawValue || amountInput.value.replace(/[^0-9]/g, '');
    });

    // Handle form submission
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', submitTransaction);
    }

    function setDefaultDate() {
        if (todayInput && !todayInput.value) {
            const today = new Date();
            todayInput.value = today.toISOString().slice(0, 10); // Format for type="date"
        }
    }

    function selectCategory(button) {
        document.querySelectorAll('.category-item').forEach(item => {
            item.classList.remove('selected');
        });
        button.classList.add('selected');
        document.getElementById('selectedCategory').value = button.dataset.categoryId || '';
    }

    function selectAccount(button) {
        document.querySelectorAll('.account-grid button').forEach(item => {
            item.classList.remove('selected');
        });
        button.classList.add('selected');
        document.getElementById('selectedAccount').value = button.dataset.accountId || '';
        updateAccountIcon(button.querySelector('.name').textContent.trim());
    }


    function handleFocus(e) {
        if (e.target.dataset.rawValue) {
            e.target.value = e.target.dataset.rawValue;
        }
    }

    function formatCurrency(e) {
        let value = e.target.value.replace(/[^\d]/g, '');
        if (value.length > 0 && !isNaN(value)) {
            const numericValue = parseInt(value, 10);
            e.target.value = numericValue.toLocaleString('vi-VN', {
                maximumFractionDigits: 0,
                minimumFractionDigits: 0
            });
            e.target.dataset.rawValue = numericValue.toString();
        } else {
            e.target.value = '';
            e.target.dataset.rawValue = '';
        }
    }

    async function submitTransaction(event) {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        const isEdit = form.getAttribute('action').includes('edit');

        // Format amount before sending
        const amountInput = document.querySelector('.amount-display');
        if (amountInput) {
            const rawValue = amountInput.dataset.rawValue || amountInput.value.replace(/[^0-9]/g, '');
            formData.set('amount', rawValue);
        }

        // Validate required fields
        if (!formData.get('category_id') || !formData.get('account_id') || !formData.get('amount')) {
            showErrorMessage('Vui lòng điền đầy đủ thông tin');
            return;
        }

        // Validate required fields with specific messages
        if (!formData.get('category_id')) {
            showErrorMessage('Vui lòng chọn danh mục');
            return;
        }
        if (!formData.get('account_id')) {
            showErrorMessage('Vui lòng chọn tài khoản');
            return;
        }
        if (!formData.get('amount')) {
            showErrorMessage('Vui lòng nhập số tiền');
            return;
        }


        // Validate date
        const dateInput = document.getElementById('todayInput');
        if (!dateInput.value && !isEdit) {
            showErrorMessage('Vui lòng chọn ngày giao dịch');
            return;
        }
        if(dateInput.value) {
            formData.set('transaction_date', dateInput.value);
        }
        
        try {
            const response = await fetch(form.getAttribute('action'), {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/json'
                }
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.message || 'Lỗi không xác định');
            }

            if (result.success) {
                showSuccessMessage(result.message || (isEdit ? 'Cập nhật giao dịch thành công!' : 'Thêm giao dịch thành công!'));
                setTimeout(() => {
                    window.location.href = '/home';
                },1000);
            }
        } catch (error) {
            console.error('Error:', error);
            showErrorMessage(error.message || 'Có lỗi xảy ra khi kết nối đến server');
        }
    }

    function showSuccessMessage(message) {
        showNotification(message, 'success');
    }

    function showErrorMessage(message) {
        showNotification(message, 'error');
    }

    function showNotification(message, type) {
        const existing = document.querySelector('.notification');
        if (existing) existing.remove();

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
});