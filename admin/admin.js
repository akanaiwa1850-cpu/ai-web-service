document.addEventListener('DOMContentLoaded', () => {
    // --- Navigation Logic ---
    const navFeedback = document.getElementById('nav-feedback');
    const navSettings = document.getElementById('nav-settings');
    const viewFeedback = document.getElementById('view-feedback');
    const viewSettings = document.getElementById('view-settings');
    const topbarTitle = document.getElementById('topbar-title');
    const btnChangeSettings = document.getElementById('btn-change-settings');
    
    // Default active items
    const navItems = document.querySelectorAll('.nav-item');

    function switchTab(tabName) {
        // Remove active class from all
        navItems.forEach(item => item.classList.remove('active'));
        
        // Hide all views
        viewFeedback.style.display = 'none';
        viewSettings.style.display = 'none';
        
        if (tabName === 'feedback') {
            navFeedback.classList.add('active');
            viewFeedback.style.display = 'block';
            topbarTitle.textContent = 'AIへの要望送信（サイト更新）';
        } else if (tabName === 'settings') {
            navSettings.classList.add('active');
            viewSettings.style.display = 'block';
            topbarTitle.textContent = '初期設定・デザイン';
        } else {
            // For dashboard and preview, just show an alert for mockup purposes
            alert('この機能はモックアップです。（現在開発中）');
            // Revert back to feedback visual state
            navFeedback.classList.add('active');
            viewFeedback.style.display = 'block';
        }
    }

    navFeedback.addEventListener('click', (e) => { e.preventDefault(); switchTab('feedback'); });
    navSettings.addEventListener('click', (e) => { e.preventDefault(); switchTab('settings'); });
    btnChangeSettings.addEventListener('click', () => switchTab('settings'));

    document.getElementById('nav-dashboard').addEventListener('click', (e) => { e.preventDefault(); switchTab('dashboard'); });
    document.getElementById('nav-preview').addEventListener('click', (e) => { e.preventDefault(); switchTab('preview'); });

    // --- Settings Logic ---
    const btnSaveSettings = document.getElementById('btn-save-settings');
    const scheduleSelect = document.getElementById('setting-schedule');
    const badge = document.getElementById('current-schedule-badge');

    // Load saved settings
    const savedSchedule = localStorage.getItem('ai-schedule');
    if (savedSchedule) {
        scheduleSelect.value = savedSchedule;
        badge.textContent = savedSchedule + ' 更新';
    }

    btnSaveSettings.addEventListener('click', () => {
        const scheduleVal = scheduleSelect.value;
        localStorage.setItem('ai-schedule', scheduleVal);
        badge.textContent = scheduleVal + ' 更新';
        alert('設定を保存しました！次回更新時にAIに適用されます。');
        switchTab('feedback'); // Return to feedback view
    });
});
