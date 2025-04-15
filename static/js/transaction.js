document.addEventListener("DOMContentLoaded", () => {
    const addForm = document.getElementById("addForm");
    const toggleFormBtn = document.getElementById("toggleForm");
    const cancelAddBtn = document.getElementById("cancelForm");
    const deleteButtons = document.querySelectorAll(".delete-button");
    const editButtons = document.querySelectorAll(".edit-button");
    const cancelEditButtons = document.querySelectorAll(".cancel-edit");
    const monthSelect = document.getElementById("monthSelect");
    const yearSelect = document.getElementById("yearSelect");
  
    // Hiển thị form thêm giao dịch
    toggleFormBtn?.addEventListener("click", () => {
      addForm.style.display = "block";
    });
  
    // Ẩn form thêm giao dịch
    cancelAddBtn?.addEventListener("click", () => {
      addForm.reset();
      addForm.style.display = "none";
    });
  
    // Gán sự kiện cho nút sửa: hiện form tương ứng
    editButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const parent = btn.closest(".transaction-item");
        const form = parent.querySelector(".edit-form");
        form.style.display = "block";
      });
    });
  
    // Gán sự kiện hủy form sửa
    cancelEditButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const form = btn.closest(".edit-form");
        form.reset();
        form.style.display = "none";
      });
    });
  
    // Xử lý xóa giao dịch
    deleteButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const transactionId = btn.getAttribute("data-transaction-id");
        if (transactionId) {
          deleteTransaction(transactionId);
        }
      });
    });
  
    // Thiết lập tháng/năm mặc định
    if (monthSelect && yearSelect) {
      const now = new Date();
      monthSelect.value = now.getMonth() + 1;
      yearSelect.value = now.getFullYear();
  
      const updateView = () => {
        const month = monthSelect.value;
        const year = yearSelect.value;
        console.log(`Đang xem dữ liệu cho: ${month}/${year}`);
      };
  
      monthSelect.addEventListener("change", updateView);
      yearSelect.addEventListener("change", updateView);
    }
  });
  
  // Hàm xóa giao dịch
  async function deleteTransaction(transactionId) {
    const confirmDelete = confirm("Bạn có chắc chắn muốn xóa giao dịch này?");
    if (!confirmDelete) return;
  
    try {
      const response = await fetch(`/transaction/${transactionId}`, {
        method: "DELETE",
      });
  
      if (response.redirected) {
        window.location.href = response.url;
      } else {
        alert("Không thể xóa giao dịch này!");
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Đã xảy ra lỗi khi xóa giao dịch!");
    }
  }
  