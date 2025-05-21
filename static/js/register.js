document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('#register-form');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const passwordFields = form.querySelectorAll('input[type="password"]');
        const formData = {
            name: form.querySelector('input[name="Username"]').value,
            ngay_sinh: form.querySelector('input[name="Date of birth"]').value,
            gioi_tinh: form.querySelector('select[name="Gender"]').value,
            email: form.querySelector('input[name="email"]').value,
            phone: form.querySelector('input[name="phone"]').value,
            password: passwordFields[0]?.value || "",
            confirm_password: passwordFields[1]?.value || "",
        };

        if (!formData.name || !formData.ngay_sinh || !formData.gioi_tinh || 
            !formData.email || !formData.phone || !formData.password) {
            alert("Vui lòng điền đầy đủ thông tin!");
            return;
        }

        if (formData.password !== formData.confirm_password) {
            alert("Mật khẩu xác nhận không khớp!");
            return;
        }

        try {
            const response = await fetch('/register', {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(formData),
            });

            const result = await response.json();
            if (response.ok) {
                alert("Đăng ký thành công!");
                window.location.href = "/login";
            } else {
                alert("Lỗi: " + result.message);
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Có lỗi xảy ra!");
        }
    });
});