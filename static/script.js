/**
 * OpenAI 代理监控前端脚本
 */

// 更新统计信息
async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        // 更新统计数据
        const totalRequestsEl = document.getElementById('total-requests');
        const successRateEl = document.getElementById('success-rate');
        const avgResponseTimeEl = document.getElementById('avg-response-time');
        
        if (totalRequestsEl) {
            totalRequestsEl.textContent = data.total_requests;
        }
        
        if (successRateEl) {
            successRateEl.textContent = `${data.success_rate}%`;
        }
        
        if (avgResponseTimeEl) {
            avgResponseTimeEl.textContent = `${data.avg_response_time}ms`;
        }
        
    } catch (error) {
        console.error('更新统计信息失败:', error);
    }
}

// 格式化时间戳
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// 格式化持续时间
function formatDuration(ms) {
    if (ms < 1000) {
        return `${ms.toFixed(2)}ms`;
    } else if (ms < 60000) {
        return `${(ms / 1000).toFixed(2)}s`;
    } else {
        return `${(ms / 60000).toFixed(2)}min`;
    }
}

// 获取状态类名
function getStatusClass(status) {
    if (status >= 200 && status < 300) {
        return 'status-success';
    } else if (status >= 400) {
        return 'status-error';
    } else {
        return 'status-pending';
    }
}

// 获取方法类名
function getMethodClass(method) {
    return `method-${method.toLowerCase()}`;
}

// 复制到剪贴板
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (error) {
        console.error('复制失败:', error);
        return false;
    }
}

// 显示通知
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // 添加样式
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#38a169' : type === 'error' ? '#e53e3e' : '#667eea'};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // 显示动画
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // 自动隐藏
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// 搜索功能
function initSearch() {
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        // 添加回车键搜索
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.closest('form').submit();
            }
        });
        
        // 添加实时搜索提示
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const query = this.value.trim();
                if (query.length > 2) {
                    // 可以在这里添加实时搜索建议
                    console.log('搜索建议:', query);
                }
            }, 300);
        });
    }
}

// 键盘快捷键
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K 聚焦搜索框
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('.search-input');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
        
        // F5 或 Ctrl/Cmd + R 刷新页面
        if (e.key === 'F5' || ((e.ctrlKey || e.metaKey) && e.key === 'r')) {
            // 让浏览器处理默认刷新
            return;
        }
        
        // Escape 清除搜索
        if (e.key === 'Escape') {
            const searchInput = document.querySelector('.search-input');
            if (searchInput && searchInput.value) {
                searchInput.value = '';
                searchInput.blur();
            }
        }
    });
}

// 自动刷新功能
let autoRefreshInterval;
function initAutoRefresh() {
    const autoRefreshCheckbox = document.getElementById('auto-refresh');
    if (autoRefreshCheckbox) {
        autoRefreshCheckbox.addEventListener('change', function() {
            if (this.checked) {
                autoRefreshInterval = setInterval(() => {
                    location.reload();
                }, 10000); // 每10秒刷新一次
                showNotification('已启用自动刷新', 'success');
            } else {
                clearInterval(autoRefreshInterval);
                showNotification('已关闭自动刷新', 'info');
            }
        });
    }
}

// 主题切换
function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        // 检查本地存储的主题设置
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.body.setAttribute('data-theme', savedTheme);
        
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.body.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            document.body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            showNotification(`已切换到${newTheme === 'light' ? '浅色' : '深色'}主题`, 'success');
        });
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initSearch();
    initKeyboardShortcuts();
    initAutoRefresh();
    initThemeToggle();
    
    // 添加页面加载动画
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.3s ease';
        document.body.style.opacity = '1';
    }, 100);
});

// 页面卸载时清理
window.addEventListener('beforeunload', function() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
});

// 导出函数供全局使用
window.updateStats = updateStats;
window.copyToClipboard = copyToClipboard;
window.showNotification = showNotification;
