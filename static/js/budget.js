// Khởi tạo sự kiện sau khi DOM đã sẵn sàng
document.addEventListener("DOMContentLoaded", function() {
  document.getElementById('add-button').addEventListener('click', addBudget);

  const toggleBtn = document.getElementById('toggle-add-form');
  const addForm = document.querySelector('.add-budget-form');

  toggleBtn.addEventListener('click', () => {
    addForm.classList.toggle('show');
  });

  initBudgetEvents(); // Khởi tạo các sự kiện còn lại
});

// Hàm thêm ngân sách bằng API
async function addBudget() {
  const categoryId = document.getElementById('new-category').value;
  const amount = document.getElementById('new-amount').value.trim();
  const startDate = document.getElementById('start-date').value.trim();
  const endDate = document.getElementById('end-date').value.trim();

  if (!amount || !startDate || !endDate) {
    alert("Vui lòng nhập đầy đủ thông tin.");
    return;
  }

  const payload = {
    category_id: categoryId,
    limit_amount: amount,
    start_date: startDate,
    end_date: endDate
  };

  try {
    const res = await fetch('/budgets/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (res.ok) {
      alert('Đã thêm ngân sách!');
      location.reload();
    } else {
      alert(data.error || 'Có lỗi xảy ra khi thêm ngân sách.');
    }
  } catch (err) {
    console.error(err);
    alert('Không thể kết nối tới máy chủ.');
  }
}

// Hàm khởi tạo các sự kiện
function initBudgetEvents() {
  // Xử lý xóa ngân sách
  document.querySelectorAll('.delete-button').forEach(button => {
    button.addEventListener('click', function() {
      const budgetId = this.closest('.budget-item').getAttribute('data-id');
      deleteBudget(budgetId);
    });
  });

  // Xử lý mở/đóng chi tiết
  document.querySelectorAll('.toggle-details').forEach(button => {
    button.addEventListener('click', function() {
      const details = this.closest('.budget-item').querySelector('.budget-details');
      const icon = this.querySelector('i');

      if (details.style.display === 'none' || !details.style.display) {
        details.style.display = 'block';
        icon.classList.remove('fa-chevron-down');
        icon.classList.add('fa-chevron-up');
      } else {
        details.style.display = 'none';
        icon.classList.remove('fa-chevron-up');
        icon.classList.add('fa-chevron-down');
      }
    });
  });

  // Xử lý cập nhật ngân sách
  document.querySelectorAll('.update-button').forEach(button => {
    button.addEventListener('click', function() {
      const form = this.closest('.budget-item').querySelector('.update-form');
      const details = this.closest('.budget-item').querySelector('.budget-details');

      if (details.style.display === 'block') {
        details.style.display = 'none';
        const toggleIcon = this.closest('.budget-item').querySelector('.toggle-details i');
        toggleIcon.classList.remove('fa-chevron-up');
        toggleIcon.classList.add('fa-chevron-down');
      }

      form.style.display = form.style.display === 'block' ? 'none' : 'block';
    });
  });

  // Xử lý hủy cập nhật
  document.querySelectorAll('.cancel-update').forEach(button => {
    button.addEventListener('click', function() {
      const form = this.closest('.update-form');
      form.style.display = 'none';
    });
  });

  // Xử lý xác nhận cập nhật
  document.querySelectorAll('.confirm-update').forEach(button => {
    button.addEventListener('click', async function() {
      const item = this.closest('.budget-item');
      const budgetId = item.getAttribute('data-id');
      const amount = item.querySelector('.update-amount').value.trim();
      const start = item.querySelector('.update-start').value.trim();
      const end = item.querySelector('.update-end').value.trim();

      if (!amount || !start || !end) {
        alert("Vui lòng điền đầy đủ thông tin.");
        return;
      }

      try {
        const res = await fetch(`/budgets/update/${budgetId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            limit_amount: amount,
            start_date: start,
            end_date: end
          })
        });

        const data = await res.json();
        if (res.ok) {
          alert("Cập nhật thành công!");
          location.reload();
        } else {
          alert(data.error || "Có lỗi khi cập nhật.");
        }
      } catch (err) {
        console.error(err);
        alert("Không thể kết nối máy chủ.");
      }
    });
  });
}

// Hàm xoá ngân sách
async function deleteBudget(budgetId) {
  if (!confirm('Bạn có chắc chắn muốn xoá ngân sách này không?')) return;

  try {
    const res = await fetch(`/budgets/delete/${budgetId}`, {
      method: 'DELETE'
    });
    const data = await res.json();
    if (res.ok) {
      alert('Đã xóa ngân sách!');
      location.reload();
    } else {
      const errorMessage = data.error || 'Có lỗi xảy ra khi xóa ngân sách.';
      alert(errorMessage);
    }
  } catch (err) {
    console.error(err);
    alert('Không thể kết nối tới máy chủ.');
  }
}
