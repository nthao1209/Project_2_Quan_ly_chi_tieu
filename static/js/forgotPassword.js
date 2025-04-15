document.addEventListener("DOMContentLoaded", function () {
    const forgotPasswordForm = document.getElementById("forgotPasswordForm");
    const verifyOtpForm = document.getElementById("verifyOtpForm");
    const resetPasswordForm = document.getElementById("resetPasswordForm");

    const otpSection = document.getElementById("otpSection");
    const resetPasswordSection = document.getElementById("resetPasswordSection");

    let userEmail = "";

    // Gửi yêu cầu OTP
    forgotPasswordForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        userEmail = document.getElementById("email").value;

        try {
            const response = await fetch("/forgot-password", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: userEmail })
            });

            const data = await response.json();
            if (response.ok) {
                alert("OTP đã được gửi đến email của bạn.");
                otpSection.style.display = "block";
            } else {
                alert(data.message || "Gửi OTP thất bại!");
            }
        } catch (error) {
            console.error("Lỗi:", error);
            alert("Đã xảy ra lỗi, vui lòng thử lại!");
        }
    });

    // Xác thực OTP
    verifyOtpForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        const otp = document.getElementById("otp").value;

        try {
            const response = await fetch("/verify-otp", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: userEmail, otp: otp })
            });

            const data = await response.json();
            if (response.ok) {
                alert("Xác thực OTP thành công. Hãy đặt lại mật khẩu.");
                resetPasswordSection.style.display = "block";
            } else {
                alert(data.message || "Mã OTP không chính xác!");
            }
        } catch (error) {
            console.error("Lỗi:", error);
            alert("Đã xảy ra lỗi, vui lòng thử lại!");
        }
    });

    // Đặt lại mật khẩu
    resetPasswordForm.addEventListener("submit", async function (event) {
        event.preventDefault();
        const newPassword = document.getElementById("newPassword").value;

        try {
            const response = await fetch("/reset-password", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: userEmail, newPassword: newPassword })
            });

            const data = await response.json();
            if (response.ok) {
                alert("Mật khẩu đã được đặt lại thành công!");
                window.location.href = "/login";
            } else {
                alert(data.message || "Đặt lại mật khẩu thất bại!");
            }
        } catch (error) {
            console.error("Lỗi:", error);
            alert("Đã xảy ra lỗi, vui lòng thử lại!");
        }
    });
});