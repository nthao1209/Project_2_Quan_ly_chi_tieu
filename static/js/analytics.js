let currentDate = new Date();
let expenseChart = null;
let currentType = 'expense'; // Mặc định là chi tiêu

function formatMonthYear(date) {
    const month = String(date.getMonth() + 1).padStart(2, '0'); // thêm số 0 nếu < 10
    const year = date.getFullYear();
    return `${month}/${year}`;
}

function fetchAnalyticsData(month, year, type = 'expense') {
    fetch(`/api/analytics-data?month=${month}&year=${year}&type=${type}`)
        .then(response => response.json())
        .then(data => {
            const totalAmount = data.total || 1;
            const categories = data.data.map(item => item.category);
            const percentages = data.data.map(item => ((item.total / totalAmount) * 100).toFixed(2));
            const amounts = data.data.map(item => item.total.toLocaleString('vi-VN') + ' đ'); 

            const ctx = document.getElementById('expenseChart').getContext('2d');
            if (expenseChart) expenseChart.destroy();

            // Chart plugin cho chữ ở giữa
            const centerTextPlugin = {
                id: 'centerText',
                beforeDraw(chart) {
                    const { ctx, chartArea: { width, height } } = chart;
                    const total = chart.options.plugins.centerTextValue || 0;
                    ctx.save();
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.font = '16px Arial';
                    ctx.fillStyle = '#000';
                    ctx.fillText('Tổng ' , width / 2, height / 2 - 10);
                    ctx.font = '15px Arial';
                    ctx.fillText(`${total.toLocaleString('vi-VN')} đ`, width / 2, height / 2 + 10);
                    ctx.restore();
                }
            };
            Chart.register(centerTextPlugin);

            function generatePastelColors(count) {
                const colors = [];
                for (let i = 0; i < count; i++) {
                    const hue = Math.floor(Math.random() * 360);
                    colors.push(`hsl(${hue}, 70%, 80%)`);
                }
                return colors;
            }

            // Vẽ biểu đồ
            expenseChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: categories.map((cat, i) => `${cat} (${percentages[i]}%)`),
                    datasets: [{
                        label: `Tỷ lệ ${type}`,
                        data: percentages,
                        backgroundColor: generatePastelColors(categories.length),
                        hoverOffset: 4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'bottom' },
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    return context.label;
                                }
                            }
                        },
                        centerTextValue: data.total
                    }
                }
            });

            // Gán tiêu đề tháng
            document.getElementById('currentMonthYear').textContent = formatMonthYear(currentDate);

            // Chi tiết danh mục
            const container = document.getElementById('detailsContainer');
            container.innerHTML = '';
            data.data.forEach((item, index) => {
                const detail = document.createElement('div');
                detail.className = 'detail-item';
                detail.innerHTML = `
                    <span class="detail-icon">${item.icon}</span>
                    <div class="detail-text">
                        <span class="detail-name">${item.category}</span>
                        <span class="detail-percent">${percentages[index]}%</span>
                        <span class="detail-amount">${item.total.toLocaleString('vi-VN')} đ</span>
                    </div>`;
                container.appendChild(detail);
            });
        })
        .catch(error => console.error('Lỗi khi lấy dữ liệu:', error));
}
function changeMonth(offset) {
    currentDate.setMonth(currentDate.getMonth() + offset);
    const month = currentDate.getMonth() + 1;
    const year = currentDate.getFullYear();
    fetchAnalyticsData(month, year, currentType);
}

function switchChart(type) {
    currentType = type;

    // Cập nhật nút active
    document.querySelectorAll('.chart-tab').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`tab-${type}`).classList.add('active');

    const month = currentDate.getMonth() + 1;
    const year = currentDate.getFullYear();
    fetchAnalyticsData(month, year, type);
}

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('prevMonth').addEventListener('click', () => changeMonth(-1));
    document.getElementById('nextMonth').addEventListener('click', () => changeMonth(1));
    fetchAnalyticsData(currentDate.getMonth() + 1, currentDate.getFullYear(), currentType);
});
