document.addEventListener('DOMContentLoaded', function () {
  // Gắn sự kiện xóa cho các danh mục render sẵn từ server
  document.querySelectorAll('.category-item .delete-button').forEach(button => {
    button.addEventListener('click', function () {
      const categoryItem = this.closest('.category-item');
      const categoryId = this.dataset.categoryId || categoryItem.dataset.id;
      console.log('ID cần xoá:', categoryId);
      deleteCategory(categoryId, categoryItem);
    });
  });

  // Hiện form khi bấm nút thêm
  document.querySelector('.add-button').addEventListener('click', function () {
    const modal = document.querySelector('.category-form');
    modal.style.display = 'flex'; // Hiển thị modal
    setTimeout(function () {
      modal.style.opacity = 1; // Hiển thị dần
      modal.style.transform = 'scale(1)'; // Modal nhảy vào vị trí bình thường
    }, 10);
  });
// Gửi dữ liệu khi bấm nút Thêm
document.querySelector('#submit-category').addEventListener('click', function () {
  const name = document.querySelector('#category-name').value;
  const icon = document.querySelector('#category-icon').value;
  const type = document.querySelector('#category-type').value;

  if (!name || !icon) {
    alert('Vui lòng điền đủ thông tin!');
    return;
  }

  const category = { name, icon, type };

  fetch('/categories', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(category)
  })
    .then(res => res.json())
    .then(data => {
      if (data.category) {
        appendCategoryToDOM(data.category);
        document.querySelector('.category-form').style.display = 'none';
        alert('Danh mục đã được thêm!');
        location.reload();
      } else {
        alert('Thêm thất bại!');
      }
    });
});

// Đóng form khi bấm nút Hủy
document.querySelector('#cancel-category').addEventListener('click', function () {
  const modal = document.querySelector('.category-form');
  modal.style.opacity = 0; // Ẩn dần
  modal.style.transform = 'scale(0.8)'; // Thu nhỏ lại
  setTimeout(function () {
    modal.style.display = 'none'; // Ẩn modal khi hiệu ứng kết thúc
  }, 300); // Thời gian trễ cho hiệu ứng ẩn
});

// Đóng form khi bấm nút đóng (x)
document.querySelector('.close-modal').addEventListener('click', function () {
  const modal = document.querySelector('.category-form');
  modal.style.opacity = 0; // Ẩn dần
  modal.style.transform = 'scale(0.8)'; // Thu nhỏ lại
  setTimeout(function () {
    modal.style.display = 'none'; // Ẩn modal khi hiệu ứng kết thúc
  }, 300);
});

  // Gắn sự kiện click cho tất cả menu-icon render sẵn
  document.querySelectorAll('.menu-icon').forEach(menuIcon => {
    menuIcon.addEventListener('click', function () {
      const categoryItem = this.closest('.category-item');
      const categoryId = categoryItem.dataset.id;

      if (categoryId) {
        window.location.href = `/transactions?category_id=${categoryId}`;
      } else {
        console.error('Không tìm thấy category_id!');
      }
    });
  });


  // Hàm thêm danh mục mới vào DOM
  function appendCategoryToDOM(category) {
    const categoryItem = document.createElement('div');
    categoryItem.classList.add('category-item');
    categoryItem.dataset.id = category.id || category.category_id;

    const categoryInfo = document.createElement('div');
    categoryInfo.classList.add('category-info');

    const icon = document.createElement('span');
    icon.classList.add('icon');
    icon.textContent = category.icon;

    const text = document.createElement('span');
    text.classList.add('text');
    text.textContent = category.name;

    categoryInfo.appendChild(icon);
    categoryInfo.appendChild(text);
    categoryItem.appendChild(categoryInfo);
  
    const actions = document.createElement('div');
    actions.classList.add('category-actions');

    const menuIcon = document.createElement('div');
    menuIcon.classList.add('menu-icon');

    menuIcon.addEventListener('click', function () {
      console.log('Đã click menu-icon!');
      const categoryId = categoryItem.dataset.id;
      if (categoryId) {
        window.location.href = `/transactions?category_id=${categoryId}`;
      } else {
        console.error('Không tìm thấy category_id để điều hướng.');
      }
    });


    const deleteButton = document.createElement('div');
    deleteButton.classList.add('delete-button');
    deleteButton.textContent = 'Xóa';
    deleteButton.dataset.categoryId = category.id;
    deleteButton.addEventListener('click', function () {
      deleteCategory(category.id, categoryItem);
    });

    actions.appendChild(menuIcon);
    actions.appendChild(deleteButton);
    categoryItem.appendChild(actions);

    
    if (category.type.toLowerCase() === 'chi tiêu') {
      document.querySelector('.category-list.expenses').appendChild(categoryItem);
    } else if (category.type.toLowerCase() === 'thu nhập') {
      document.querySelector('.category-list.income').appendChild(categoryItem);
    }
  }

  // Hàm xóa danh mục
  function deleteCategory(categoryId, elementToRemove) {
    console.log('Xoá ID:', categoryId); // Debug
  
    fetch(`/categories/${categoryId}`, {
      method: 'DELETE'
    })
    .then(res => {
      if (!res.ok) {
        throw new Error(`Server trả về lỗi ${res.status}`);
      }
      return res.json();
    })
    .then(data => {
      if (data.message) {
        alert(data.message);
        elementToRemove.remove(); // Xoá khỏi DOM
      } else {
        alert('Xóa thất bại.');
      }
    })
    .catch(error => {
      console.error('Lỗi khi xoá danh mục:', error);
      alert('Có lỗi xảy ra, vui lòng thử lại!');
    });
  }
  
});