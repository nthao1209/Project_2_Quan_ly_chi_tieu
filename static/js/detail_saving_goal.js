document.addEventListener("DOMContentLoaded", function () {
  let currentGoalId = null;
  const modal = document.getElementById('edit-form');
  const formTitle = document.getElementById('form-title');

  // Function to open edit form
  window.openEditForm = function(goalId) {
      
    if (!goalId) {
      console.error('No goal ID provided');
      return;
    }

      currentGoalId = goalId;
      fetch(`/goals/detail/${goalId}`)
          .then(response => {
              if (!response.ok) throw new Error('Không thể tải dữ liệu mục tiêu');
              return response.json();
          })
          .then(goal => {
              // Populate form fields
              document.getElementById('edit-name').value = goal.name;
              document.getElementById('edit-target-amount').value = goal.target_amount;
              document.getElementById('edit-start-time').value = goal.start_time;
              document.getElementById('edit-end-time').value = goal.end_time;
              document.getElementById('edit-note').value = goal.note || '';
              
              // Update form title
              formTitle.textContent = 'Chỉnh sửa mục tiêu';
              document.querySelector('.save-btn').textContent = 'Cập nhật';
              
              // Show modal
              modal.classList.remove('hidden');
          })
          .catch(error => {
              console.error('Error:', error);
              showAlert('error', 'Lỗi khi tải dữ liệu: ' + error.message);
          });
  };

  // Function to hide edit form
  window.hideEditForm = function() {
      modal.classList.add('hidden');
      editForm.reset();
      currentGoalId = null;
  };

  // Form submission handler
  editForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const formData = {
          name: document.getElementById('edit-name').value.trim(),
          target_amount: parseFloat(document.getElementById('edit-target-amount').value),
          start_time: document.getElementById('edit-start-time').value,
          end_time: document.getElementById('edit-end-time').value,
          note: document.getElementById('edit-note').value.trim()
      };

      // Validation
      if (!formData.name || isNaN(formData.target_amount) || !formData.start_time || !formData.end_time) {
          showAlert('error', 'Vui lòng điền đầy đủ thông tin bắt buộc');
          return;
      }

      if (formData.target_amount <= 0) {
          showAlert('error', 'Số tiền mục tiêu phải lớn hơn 0');
          return;
      }

      const startDate = new Date(formData.start_time);
      const endDate = new Date(formData.end_time);
      if (endDate <= startDate) {
          showAlert('error', 'Thời gian kết thúc phải sau thời gian bắt đầu');
          return;
      }

      const url = currentGoalId ? `/goals/update/${currentGoalId}` : '/goals/add';
      const method = currentGoalId ? 'PUT' : 'POST';

      // Show loading state
      const submitBtn = document.querySelector('.save-btn');
      const originalBtnText = submitBtn.textContent;
      submitBtn.disabled = true;
      submitBtn.textContent = 'Đang xử lý...';

      fetch(url, {
          method: method,
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData)
      })
      .then(response => {
          if (!response.ok) throw new Error('Lỗi kết nối với máy chủ');
          return response.json();
      })
      .then(data => {
          if (data.error) throw new Error(data.error);
          showAlert('success', currentGoalId ? 'Cập nhật mục tiêu thành công!' : 'Thêm mục tiêu mới thành công!');
          setTimeout(() => window.location.reload(), 1500);
      })
      .catch(error => {
          console.error('Error:', error);
          showAlert('error', 'Lỗi: ' + error.message);
      })
      .finally(() => {
          submitBtn.disabled = false;
          submitBtn.textContent = originalBtnText;
      });
  });

  // Delete confirmation
  window.confirmDelete = function() {
      if (!currentGoalId) return;
      
      if (confirm('Bạn có chắc chắn muốn xóa mục tiêu này? Toàn bộ lịch sử nạp tiền cũng sẽ bị xóa.')) {
          deleteGoal(currentGoalId);
      }
  };

  // Delete goal function
  function deleteGoal(goalId) {
      fetch(`/goals/delete/${goalId}`, {
          method: 'DELETE'
      })
      .then(response => {
          if (!response.ok) throw new Error('Lỗi kết nối với máy chủ');
          return response.json();
      })
      .then(data => {
          if (data.error) throw new Error(data.error);
          showAlert('success', 'Đã xóa mục tiêu thành công!');
          window.location.reload();
        })
      .catch(error => {
          console.error('Error:', error);
          showAlert('error', 'Lỗi khi xóa mục tiêu: ' + error.message);
      });
  }

  // Helper function to show alerts
  function showAlert(type, message) {
      const alertDiv = document.createElement('div');
      alertDiv.className = `alert ${type}`;
      alertDiv.textContent = message;
      document.body.appendChild(alertDiv);
      
      setTimeout(() => {
          alertDiv.classList.add('fade-out');
          setTimeout(() => alertDiv.remove(), 500);
      }, 3000);
  }
});