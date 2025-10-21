// app.js - УПРОЩЕННАЯ ВЕРСИЯ
console.log('=== ИНИЦИАЛИЗАЦИЯ ПРИЛОЖЕНИЯ ===');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM загружен');

    // Инициализация карты
    if (typeof initMap === 'function') {
        initMap();
    } else {
        console.error('❌ Функция initMap не найдена');
    }

    // Система заданий инициализируется автоматически через quest-system.js
    console.log('✅ Приложение успешно инициализировано');
});

// Перерисовка карты при изменении размера окна
window.addEventListener('resize', function() {
    if (typeof map !== 'undefined' && map) {
        setTimeout(() => {
            map.invalidateSize();
        }, 100);
    }
});