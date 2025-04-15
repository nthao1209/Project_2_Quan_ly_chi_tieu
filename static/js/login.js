document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");

    form.addEventListener("submit", async function(event) {
        event.preventDefault(); // Ngăn form gửi request mặc định

        const formData = new FormData(form);
        const data = {
            email: formData.get("email"),
            password: formData.get("password"),
        };

        if (!data.email || !data.password) {
            alert("Vui lòng nhập đầy đủ email và mật khẩu!");
            return;
        }

        try {
            const response = await fetch("/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (response.ok) {
                alert("Đăng nhập thành công!");
                window.location.href = "/"; 
            } else {
                alert(result.message || "Đăng nhập thất bại!");
            }
        } catch (error) {
            console.error("Lỗi đăng nhập:", error);
            alert("Đã xảy ra lỗi, vui lòng thử lại!");
        }
    });
});
