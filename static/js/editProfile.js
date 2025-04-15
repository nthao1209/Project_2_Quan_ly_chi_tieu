document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('editProfileForm');

    form.addEventListener('submit', async function(event) {
        event.preventDefault();

        const formData = {
            phone: form.querySelector('input[name="phone"]').value,
            email: form.querySelector('input[name="email"]').value,
            currentPassword: form.querySelector('input[name="currentPassword"]').value,
            newPassword: form.querySelector('input[name="newPassword"]').value
        };

        try {
            const response = await fetch('/editprofile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();
            alert(result.message);

            if (response.ok) {
                window.location.href = '/register';
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    // Reset form handling
    const resetButton = form.querySelector('button[type="reset"]');
    resetButton.addEventListener('click', function() {
        form.reset();
    });
});

document.getElementById("avatar-input").addEventListener("change", function(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById("avatarImage").src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
});
document.querySelector('form button[name="delete_avatar"]').addEventListener('click', function(event) {
    event.preventDefault();  // Ngừng việc submit form mặc định

    fetch("/editProfile", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            delete_avatar: true
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
            // Cập nhật giao diện: Ẩn ảnh và nút xóa
            document.getElementById("avatarImage").src = "/static/images/default-avatar.png"; // ảnh mặc định
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
});
