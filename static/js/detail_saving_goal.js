// Function to open the edit form and populate it with data
function openEditForm(goalId) {
    fetch(`/goals/detail/${goalId}`)
      .then(response => response.json())
      .then(goal => {
        // Populate the form fields with goal data
        document.getElementById('edit-name').value = goal.name;
        document.getElementById('edit-target-amount').value = goal.target_amount;
        document.getElementById('edit-start-time').value = goal.start_time.split('T')[0];  // Assuming the time is in ISO format
        document.getElementById('edit-end-time').value = goal.end_time.split('T')[0];  // Assuming the time is in ISO format
        document.getElementById('edit-note').value = goal.note || '';
  
        // Save goalId in form to send PUT later
        document.getElementById('edit-goal-form').setAttribute('data-goal-id', goal.goal_id);
  
        // Show the edit form
        document.getElementById('edit-form').classList.remove('hidden');
      })
      .catch(error => {
        alert('Lỗi khi tải dữ liệu mục tiêu: ' + error);
      });
  }
  
  // Function to hide the edit form
  function hideEditForm() {
    document.getElementById('edit-form').classList.add('hidden');
  }
  
  // Form submit handler to update the goal
  document.getElementById('edit-goal-form').addEventListener('submit', function (e) {
    e.preventDefault();
    console.log('Form đã được gửi!')
    const goalId = this.getAttribute('data-goal-id');
    const data = {
      name: document.getElementById('edit-name').value,
      target_amount: document.getElementById('edit-target-amount').value,
      start_time: document.getElementById('edit-start-time').value,
      end_time: document.getElementById('edit-end-time').value,
      note: document.getElementById('edit-note').value
    };
    

    if (!data.name || !data.target_amount || !data.start_time || !data.end_time) {
        alert('Vui lòng điền đầy đủ thông tin.');
        return;
      }
    
    fetch(`/goals/update/${goalId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(res => {
      if (res.message) {
        alert('Cập nhật thành công!');
        location.reload(); 
      } else {
        alert('Lỗi: ' + res.error);
      }
    })
    .catch(error => {
      alert('Lỗi khi cập nhật: ' + error);
    });
  });
  