$(document).ready(function () {
    $('#deposit-form').on('submit', function (e) {
        e.preventDefault();

        // Lấy dữ liệu từ form
        const goal_id = $('#goal_id').val();
        const deposit_amount = $('#deposit_amount').val();
        const from_account = $('#from_account').val();
        const to_account = $('#to_account').val();

        const data = {
            goal_id: goal_id,
            deposit_amount: deposit_amount,
            from_account: from_account,
            to_account: to_account
        };

        // Gửi yêu cầu AJAX đến server
        $.ajax({
            url: '/deposit',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function (response) {
                // Hiển thị phần trăm hoàn thành
                $('#completion_percentage').text(response.completion_percentage.toFixed(2));
                $('#result').show();
                    window.location.href = '/detail_saving_goal';

            },
            error: function (error) {
                alert('Có lỗi xảy ra: ' + error.responseJSON.error);
            }
        });
    });
});
