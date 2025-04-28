document.addEventListener("DOMContentLoaded", function () {
    let mode = "create";
    let currentGoalId = null;

    const form = document.getElementById("goal-form");

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const data = {
            name: document.getElementById("name").value,
            target_amount: document.getElementById("target_amount").value,
            start_time: document.getElementById("start_time").value,
            end_time: document.getElementById("end_time").value,
            note: document.getElementById("note").value
        };

        if (!data.name || !data.target_amount || !data.start_time || !data.end_time) {
            alert("Vui lòng điền đầy đủ thông tin.");
            return;
        }

        const url = mode === "edit"
            ? `/goals/update/${currentGoalId}`
            : "/goals/add";

        const method = mode === "edit" ? "PUT" : "POST";

        fetch(url, {
            method: method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(res => {
            if (res.error) {
                alert("Lỗi: " + res.error);
            } else {
                alert(mode === "edit" ? "Cập nhật thành công" : "Đã thêm mục tiêu");
                window.location.href = "/goals";
            }
        })
        .catch(err => console.error("Lỗi:", err));
    });

    window.updateGoal = function (goalId) {
        fetch(`/goals/detail/${goalId}`)
            .then(res => res.json())
            .then(goal => {
                document.getElementById("name").value = goal.name;
                document.getElementById("target_amount").value = goal.target_amount;
                document.getElementById("start_time").value = goal.start_time;
                document.getElementById("end_time").value = goal.end_time;
                document.getElementById("note").value = goal.note;

                mode = "edit";
                currentGoalId = goalId;

                document.querySelector("header h1").innerText = "Cập nhật mục tiêu";
                document.querySelector(".save-btn").innerText = "Cập nhật";
            })
            .catch(err => console.error("Không thể load mục tiêu", err));
    };

    window.deleteGoal = function (goalId) {
        if (!confirm("Bạn chắc chắn muốn xóa mục tiêu này?")) return;

        fetch(`/goals/delete/${goalId}`, {
            method: "DELETE"
        })
        .then(res => res.json())
        .then(res => {
            if (res.error) {
                alert("Lỗi: " + res.error);
            } else {
                alert("Đã xóa mục tiêu");
                window.location.href = "/goals";
            }
        })
        .catch(err => console.error("Lỗi xóa mục tiêu:", err));
    };
});
