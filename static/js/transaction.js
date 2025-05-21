document.addEventListener('DOMContentLoaded', function () {
  const prevMonth = document.getElementById('prevMonth');
  const nextMonth = document.getElementById('nextMonth');
  const currentMonthYear = document.getElementById('currentMonthYear');
  let expenseChart = null;
  let currentDate = new Date();

  const floatingBtn = document.querySelector('.floating-btn');
    if (floatingBtn) {
        floatingBtn.addEventListener('click', e => {
            e.preventDefault();
            window.location.href = '/transactions/add_form';
        });
    }

  function updateMonthYear() {
    const month = currentDate.getMonth();
    const year = currentDate.getFullYear();
    currentMonthYear.textContent = `${month + 1}/${year}`;
  }

  function changeMonth(direction) {
    currentDate.setMonth(currentDate.getMonth() + direction);
    updateMonthYear();
    updateCategoryInfo();
    fetchAnalyticsData(currentDate.getMonth() + 1, currentDate.getFullYear(), 'expense');
  }

  function updateCategoryInfo() {
    const month = currentDate.getMonth() + 1;
    const year = currentDate.getFullYear();
    const urlParams = new URLSearchParams(window.location.search);
    const categoryId = urlParams.get('category_id');
    let url = `/transactions?month=${month}&year=${year}&category_id=${categoryId}`;

    fetch(url, {
      headers: {
        'Accept': 'application/json'
      }
    })
     .then(response => response.json())
  .then(data => {
    const { total_amount, total_count, budget, percentage, remaining_budget } = data;
    console.log({ total_amount, total_count, budget, percentage, remaining_budget });
    
    function formatCurrency(amount) {
      const roundedAmount = Math.round(parseFloat(amount));  // Chuyển thành số nguyên
      return roundedAmount.toLocaleString('vi-VN') + ' đ';    // Định dạng theo kiểu Việt Nam
    }
    console.log('budget:', budget);
    console.log('budget.limit_amount:', budget ? budget.limit_amount : 'budget is null/undefined');

    
    const summaryValues = document.querySelectorAll('.summary-item .value');
    summaryValues[0].innerText = total_count;
    summaryValues[1].innerText = budget && budget.limit_amount ? formatCurrency(budget.limit_amount) : 'Chưa có';
    summaryValues[2].innerText = formatCurrency(total_amount);
    summaryValues[3].innerText = `${percentage.toFixed(2)}%`;
    summaryValues[4].innerText = formatCurrency(remaining_budget);
  });
  }

  function fetchAnalyticsData(month, year, type = 'expense') {
    fetch(`/api/analytics-data?month=${month}&year=${year}&type=${type}`)
      .then(response => {
        if (!response.ok) throw new Error('Lỗi khi lấy dữ liệu phân tích');
        return response.json();
      })
      .then(data => {
        const totalAmount = data.total || 1;
        const categories = data.data.map(item => item.category);
        const percentages = data.data.map(item => ((item.total / totalAmount) * 100).toFixed(2));
        const amounts = data.data.map(item => item.total.toLocaleString('vi-VN') + ' đ');

        const ctx = document.getElementById('expenseChart').getContext('2d');
        if (expenseChart) expenseChart.destroy();

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
            ctx.fillText('Tổng', width / 2, height / 2 - 10);
            ctx.font = '20px Arial';
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
              legend: { position: 'top' },
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

        const container = document.getElementById('detailsContainer');
        container.innerHTML = '';
        if (data.data.length > 0) {
          data.data.forEach((item, index) => {
            const detail = document.createElement('div');
            detail.className = 'detail-item';
            detail.innerHTML = `
              <span class="detail-icon">${item.icon || '📊'}</span>
              <div class="detail-text">
                <span class="detail-name">${item.category}</span> 
                <span class="detail-percent">${percentages[index]}%</span>
                <span class="detail-amount">${item.total.toLocaleString('vi-VN')} đ</span>
              </div>
            `;
            container.appendChild(detail);
          });
        } else {
          container.innerHTML = '<p>Không có dữ liệu chi tiết.</p>';
        }
      })
      .catch(error => {
        console.error('Lỗi khi lấy dữ liệu phân tích:', error);
        document.getElementById('detailsContainer').innerHTML = '<p>Lỗi khi tải dữ liệu chi tiết.</p>';
      });
  }

  updateMonthYear();
  updateCategoryInfo();
  fetchAnalyticsData(currentDate.getMonth() + 1, currentDate.getFullYear(), 'expense');

  prevMonth.addEventListener('click', function () {
    changeMonth(-1);
  });

  nextMonth.addEventListener('click', function () {
    changeMonth(1);
  });
});