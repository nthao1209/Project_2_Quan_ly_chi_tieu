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

// Gắn sự kiện click cho nút "Thêm"
document.addEventListener("DOMContentLoaded", function() {
  document.getElementById('add-button').addEventListener('click', addBudget);
});

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
      const errorMessage = data.error || 'Có lỗi xảy ra khi thêm ngân sách.';
      alert(errorMessage);    }
  } catch (err) {
    console.error(err);
    alert('Không thể kết nối tới máy chủ.');
  }
}

document.querySelectorAll('.delete-button').forEach(button => {
  button.addEventListener('click', function () {
    const budgetId = this.closest('.item').getAttribute('data-id');
    deleteBudget(budgetId);
  });
});

// Khi nhấn nút ✏️ hiện form cập nhật
document.querySelectorAll('.update-button').forEach(button => {
  button.addEventListener('click', function () {
    const form = this.parentElement.querySelector('.update-form');
    form.style.display = (form.style.display === 'none') ? 'block' : 'none';
  });
});

// Khi nhấn nút "Cập nhật" trong form
document.querySelectorAll('.confirm-update').forEach(button => {
  button.addEventListener('click', async function () {
    const item = this.closest('.item');
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


document.querySelectorAll('.icon').forEach(icon => {
  icon.addEventListener('click', function () {
    const details = this.closest('.item').querySelector('.budget-details');
    details.style.display = (details.style.display === 'none') ? 'block' : 'none';
  });
});