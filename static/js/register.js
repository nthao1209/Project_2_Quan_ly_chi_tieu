document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    
    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        
        const formData = new FormData(form);
        const data = {
            name: formData.get("Username"),
            email: formData.get("email"),
            password: formData.get("password"),
            phone: formData.get("phone"),
        };
        
        try {
            const response = await fetch("http://127.0.0.1:5000/users/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data),
            });
            
            const result = await response.json();
            
            if (response.ok) {
                alert("Đăng ký thành công!");
                window.location.href = "/"; // Chuyển hướng đến trang đăng nhập
            } else {
                alert(result.message);
            }
        } catch (error) {
            console.error("Lỗi đăng ký:", error);
            alert("Đã xảy ra lỗi, vui lòng thử lại!");
        }
    });
});
