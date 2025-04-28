document.addEventListener('DOMContentLoaded', function() {

const avatar = document.querySelector('.avatar-wrapper');
const dropdown = document.querySelector('.dropdown-content');
const categoryIcon = document.querySelector('.category-btn'); // Chọn icon danh mục

// Khi click vào avatar, hiển thị hoặc ẩn dropdown
avatar.addEventListener('click', function(event) {
    event.stopPropagation(); // Ngăn sự kiện lan ra ngoài
    dropdown.style.display = (dropdown.style.display === 'none' || dropdown.style.display === '') ? 'block' : 'none';
});

// Khi click ra ngoài avatar, ẩn dropdown
document.addEventListener('click', function(event) {
    if (!avatar.contains(event.target) && !dropdown.contains(event.target)) {
        dropdown.style.display = 'none';
    }
});

const categoryBtn = document.querySelector('.category-btn');
const accountBtn = document.querySelector('.account-btn');
const analyticsBtn = document.querySelector('.analytics-btn');
const budgetBtn = document.querySelector('.budget-btn');
const savingGoalBtn = document.querySelector('.saving-goal-btn');

if(categoryBtn){
    categoryBtn.addEventListener('click', function(event) {
        event.preventDefault(); 
        window.location.href = '/categories-page';
    })
}

if(accountBtn){
    accountBtn.addEventListener('click', function(event) {
        event.preventDefault(); 
        window.location.href = '/bank_account';
    })
}

if(analyticsBtn){
    analyticsBtn.addEventListener('click', function(event) {
        event.preventDefault(); 
        window.location.href = '/analytics';
    })
}

if(budgetBtn){
    budgetBtn.addEventListener('click', function(event) {
        event.preventDefault(); 
        window.location.href = '/budgets';
    })
}   

if(savingGoalBtn){
    savingGoalBtn.addEventListener('click', function(event) {
        event.preventDefault(); 
        window.location.href = '/home_saving_goal';
    })
}

}); 

