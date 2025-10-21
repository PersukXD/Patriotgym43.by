// map-system.js - ПОЛНОСТЬЮ ИСПРАВЛЕННАЯ ВЕРСИЯ

let map;
let markersCluster;
let currentFilteredEvents = [];
let currentCategoryFilter = null;

function initMap() {
    console.log('Инициализация карты...');

    const mapElement = document.getElementById('historical-map');
    if (!mapElement) {
        console.error('❌ Элемент карты не найден!');
        return;
    }

    try {
        map = L.map('historical-map', {
            attributionControl: false
        }).setView([53.9, 27.5], 7);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19
        }).addTo(map);

        markersCluster = L.markerClusterGroup();
        map.addLayer(markersCluster);

        // Инициализируем ВСЕ события
        currentFilteredEvents = [...historicalEvents];
        currentCategoryFilter = null;

        addMarkersToMap();
        renderEventsList(historicalEvents);
        renderCategories();
        initFilters();

        console.log('✅ Карта успешно инициализирована');

    } catch (error) {
        console.error('❌ Ошибка при создании карты:', error);
    }
}

// ПОЛНОСТЬЮ ПЕРЕПИСАННАЯ ФУНКЦИЯ СБРОСА
// map-system.js - ИСПРАВЛЕННАЯ ФУНКЦИЯ СБРОСА

function resetAllFilters() {
    console.log('🔄 АГРЕССИВНЫЙ СБРОС ВСЕХ ФИЛЬТРОВ');

    // 1. Сбрасываем категории
    document.querySelectorAll('.category-item').forEach(item => {
        item.classList.remove('active');
    });

    // 2. ПРИНУДИТЕЛЬНЫЙ сброс селектов
    const centuryFilter = document.getElementById('century-filter');
    const typeFilter = document.getElementById('type-filter');
    const timelineSlider = document.getElementById('timeline-slider');
    const currentYear = document.getElementById('current-year');

    // Полностью переустанавливаем значения
    if (centuryFilter) {
        centuryFilter.value = "";
        centuryFilter.dispatchEvent(new Event('change'));
    }

    if (typeFilter) {
        typeFilter.value = "";
        typeFilter.dispatchEvent(new Event('change'));
    }

    if (timelineSlider) {
        timelineSlider.value = "2024";
        timelineSlider.dispatchEvent(new Event('input'));
    }

    if (currentYear) {
        currentYear.textContent = '2024 г.';
    }

    // 3. Сбрасываем переменные
    currentCategoryFilter = null;
    currentFilteredEvents = [...historicalEvents];

    // 4. Перерисовываем карту
    updateMapWithFilteredEvents(historicalEvents);

    // 5. Обновляем список
    renderEventsList(historicalEvents);

    // 6. Сбрасываем вид карты
    if (map) {
        map.setView([53.9, 27.5], 7);
    }

    // 7. Визуальная обратная связь
    const resetBtn = document.getElementById('reset-view');
    if (resetBtn) {
        const originalHtml = resetBtn.innerHTML;
        resetBtn.innerHTML = '<i class="bi bi-check"></i>';
        resetBtn.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';

        setTimeout(() => {
            resetBtn.innerHTML = originalHtml;
            resetBtn.style.background = 'linear-gradient(135deg, #2196f3 0%, #1976d2 100%)';
        }, 1000);
    }

    console.log('✅ Все фильтры сброшены');
}

// ИСПРАВЛЕННАЯ функция для категорий
function toggleCategoryFilter(category) {
    const categoryItem = document.querySelector(`[data-category="${category}"]`);
    const isActive = categoryItem.classList.contains('active');

    // Сначала сбрасываем ВСЕ категории
    document.querySelectorAll('.category-item').forEach(item => {
        item.classList.remove('active');
    });

    if (isActive) {
        // Если категория была активна - сбрасываем фильтр
        currentCategoryFilter = null;
        currentFilteredEvents = [...historicalEvents];
        console.log('🗑️ Фильтр категории сброшен');
    } else {
        // Если не активна - применяем фильтр
        categoryItem.classList.add('active');
        currentCategoryFilter = category;
        currentFilteredEvents = historicalEvents.filter(event => event.category === category);
        console.log('✅ Применен фильтр категории:', category);
    }

    // Обновляем карту и список
    updateMapWithFilteredEvents(currentFilteredEvents);
    renderEventsList(currentFilteredEvents);
}

function initFilters() {
    // Фильтр по веку
    document.getElementById('century-filter').addEventListener('change', function() {
        applyCombinedFilters();
    });

    // Фильтр по типу
    document.getElementById('type-filter').addEventListener('change', function() {
        applyCombinedFilters();
    });

    // Таймлайн
    document.getElementById('timeline-slider').addEventListener('input', function() {
        const year = this.value;
        document.getElementById('current-year').textContent = year + ' г.';
        applyCombinedFilters();
    });

    // Кнопка сброса - ТЕПЕРЬ РАБОТАЕТ ПРАВИЛЬНО
    document.getElementById('reset-view').addEventListener('click', function() {
        resetAllFilters();
    });

    // Кнопка переключения кластеров
    document.getElementById('toggle-clusters').addEventListener('click', function() {
        if (map.hasLayer(markersCluster)) {
            map.removeLayer(markersCluster);
            this.innerHTML = '<i class="bi bi-geo-alt"></i>';
        } else {
            map.addLayer(markersCluster);
            this.innerHTML = '<i class="bi bi-collection"></i>';
        }
    });
}

function applyCombinedFilters() {
    const century = document.getElementById('century-filter').value;
    const type = document.getElementById('type-filter').value;
    const year = parseInt(document.getElementById('timeline-slider').value);

    console.log('Применение фильтров:', { century, type, year, currentCategoryFilter });

    let filteredEvents = historicalEvents.filter(event => {
        // Фильтр по категории (если активен)
        if (currentCategoryFilter && event.category !== currentCategoryFilter) {
            return false;
        }

        // Фильтр по веку
        if (century && Math.ceil(event.year / 100) != century) {
            return false;
        }

        // Фильтр по типу
        if (type && event.category !== type) {
            return false;
        }

        // Фильтр по году
        if (event.year > year) {
            return false;
        }

        return true;
    });

    currentFilteredEvents = filteredEvents;
    updateMapWithFilteredEvents(filteredEvents);
    renderEventsList(filteredEvents);
}

function updateMapWithFilteredEvents(events) {
    markersCluster.clearLayers();

    events.forEach(event => {
        const color = getCategoryColor(event.category);
        const radius = event.importance === 'high' ? 10 : (event.importance === 'medium' ? 8 : 6);

        const marker = L.circleMarker(event.coordinates, {
            radius: radius,
            fillColor: color,
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        });

        marker.bindPopup(`
            <div class="event-popup">
                <div class="popup-title">${event.title}</div>
                <div class="popup-meta">
                    <span class="popup-date">${event.date}</span>
                    <span class="popup-category" style="background-color: ${color}">${event.category}</span>
                </div>
                <div class="popup-description">${event.description}</div>
            </div>
        `);

        marker.on('click', function() {
            highlightEventInList(event.id);
        });

        marker.eventData = event;
        markersCluster.addLayer(marker);
    });

    // Автоматическое приближение если есть события
    if (events.length > 0) {
        const bounds = markersCluster.getBounds();
        if (bounds.isValid()) {
            map.fitBounds(bounds, { padding: [20, 20] });
        }
    }
}

// Остальные функции остаются без изменений...
function renderEventsList(events) {
    const container = document.getElementById('events-container');
    if (!container) return;

    if (events.length === 0) {
        container.innerHTML = `
            <div class="no-events">
                <div><i class="bi bi-inbox" style="font-size: 2rem;"></i></div>
                <p class="mt-2 mb-0">События не найдены</p>
            </div>
        `;
        return;
    }

    container.innerHTML = events.map(event => {
        const color = getCategoryColor(event.category);
        return `
        <div class="event-item" data-event-id="${event.id}" onclick="focusOnEvent(${event.id})">
            <div class="event-title">${event.title}</div>
            <div class="event-meta">
                <span class="event-date">${event.date}</span>
                <span class="event-category" style="background-color: ${color}">
                    ${event.category}
                </span>
            </div>
            <div class="event-description">${event.description}</div>
        </div>
        `;
    }).join('');
}

function renderCategories() {
    const container = document.getElementById('category-list');
    if (!container) return;

    const categories = {};
    historicalEvents.forEach(event => {
        categories[event.category] = (categories[event.category] || 0) + 1;
    });

    container.innerHTML = Object.entries(categories).map(([category, count]) => {
        const color = getCategoryColor(category);
        return `
        <div class="category-item" data-category="${category}">
            <div class="category-color" style="background-color: ${color}"></div>
            <div class="category-name">${category}</div>
            <div class="category-count">${count}</div>
        </div>
        `;
    }).join('');

    addCategoryEventListeners();
}

function addCategoryEventListeners() {
    const categoryItems = document.querySelectorAll('.category-item');
    categoryItems.forEach(item => {
        item.addEventListener('click', function() {
            const category = this.dataset.category;
            toggleCategoryFilter(category);
        });
    });
}

function focusOnEvent(eventId) {
    const event = currentFilteredEvents.find(e => e.id === eventId);
    if (event && map) {
        map.setView(event.coordinates, 10);
        markersCluster.getLayers().forEach(layer => {
            if (layer.eventData && layer.eventData.id === eventId) {
                layer.openPopup();
            }
        });
        highlightEventInList(eventId);
    }
}

function highlightEventInList(eventId) {
    document.querySelectorAll('.event-item').forEach(item => {
        item.classList.remove('active');
        if (parseInt(item.dataset.eventId) === eventId) {
            item.classList.add('active');
            item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    });
}

function getCategoryColor(category) {
    const colorMap = {
        'основания': '#34495e',
        'религия': '#9b59b6',
        'сражения': '#e74c3c',
        'реформы': '#27ae60',
        'восстания': '#e67e22',
        'политика': '#2c3e50',
        'технологии': '#d35400',
        'культура': '#8e44ad'
    };
    return colorMap[category] || '#6c757d';
}

function addMarkersToMap() {
    historicalEvents.forEach(event => {
        const color = getCategoryColor(event.category);
        const radius = event.importance === 'high' ? 10 : (event.importance === 'medium' ? 8 : 6);

        const marker = L.circleMarker(event.coordinates, {
            radius: radius,
            fillColor: color,
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        });

        marker.bindPopup(`
            <div class="event-popup">
                <div class="popup-title">${event.title}</div>
                <div class="popup-meta">
                    <span class="popup-date">${event.date}</span>
                    <span class="popup-category" style="background-color: ${color}">${event.category}</span>
                </div>
                <div class="popup-description">${event.description}</div>
            </div>
        `);

        marker.on('click', function() {
            highlightEventInList(event.id);
        });

        marker.eventData = event;
        markersCluster.addLayer(marker);
    });
}

window.focusOnEvent = focusOnEvent;
window.resetAllFilters = resetAllFilters;