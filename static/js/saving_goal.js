document.addEventListener("DOMContentLoaded", function () {
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

        fetch("/goals/add", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(res => {
            if (res.error) {
                alert("Lỗi: " + res.error);
            } else {
                alert("Đã thêm mục tiêu thành công!");
                window.location.href = "/home_saving_goal?_=" + new Date().getTime();
            }
        })
        .catch(err => {
            console.error("Lỗi:", err);
            alert("Có lỗi xảy ra. Vui lòng thử lại.");
        });
    });
});
