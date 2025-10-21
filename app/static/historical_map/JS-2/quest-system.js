// quest-system.js - ПОЛНОСТЬЮ ИСПРАВЛЕННАЯ ВЕРСИЯ БЕЗ ALERT

// Перехватываем все alert сообщения
const originalAlert = window.alert;
window.alert = function(message) {
    console.log('Alert blocked:', message);
    // Не показываем alert, просто логируем
    return;
};

class QuestSystem {
    constructor() {
        this.currentQuest = null;
        this.questMarker = null;
        this.questPopup = null;
        this.diamonds = 0;
        this.lastQuestTime = 0;
        this.QUEST_COOLDOWN = 5 * 60 * 1000;
        this.userId = null;
        this.username = null;
        this.isInitialized = false;

        // Дополнительная защита от alert
        this.blockAlerts();
        this.init();
    }

    // Метод для блокировки alert
    blockAlerts() {
        window.alert = function(message) {
            console.log('❌ Alert blocked in QuestSystem:', message);
            return;
        };
    }

    async init() {
        console.log('🔧 Инициализация системы заданий...');
        await this.loadUserData();
        this.updateCooldownDisplay();
        this.setupEventListeners();
        setInterval(() => this.updateCooldownDisplay(), 60000);
        this.isInitialized = true;
        console.log('✅ Система заданий инициализирована');
    }

    async loadUserData() {
        try {
            const userDataElement = document.getElementById('user-data');
            if (userDataElement) {
                this.userId = userDataElement.dataset.userId;
                this.username = userDataElement.dataset.username;

                if (this.userId === 'anonymous') {
                    console.warn('⚠️ Пользователь не авторизован');
                    this.showLoginRequired();
                    return;
                }
            }

            const response = await fetch('/api/diamonds/');
            const data = await response.json();

            if (data.success) {
                this.diamonds = data.diamonds;
                this.updateDiamondCounter();
            } else {
                this.diamonds = 0;
                this.updateDiamondCounter();
            }

            const userLastQuestTime = localStorage.getItem(`lastQuestTime_${this.userId}`);
            this.lastQuestTime = userLastQuestTime ? parseInt(userLastQuestTime) : 0;

        } catch (error) {
            console.error('❌ Ошибка при загрузке данных:', error);
            this.diamonds = 0;
            this.updateDiamondCounter();
        }
    }

    showLoginRequired() {
        const questButton = document.getElementById('quest-button');
        const diamondCounter = document.querySelector('.diamond-counter');
        const cooldownText = document.getElementById('quest-cooldown');

        if (questButton) {
            questButton.disabled = true;
            questButton.innerHTML = '<i class="bi bi-lock"></i> Войдите в аккаунт';
            questButton.style.opacity = '0.6';
        }

        if (cooldownText) {
            cooldownText.textContent = 'Доступно после входа в аккаунт';
        }
    }

    async addDiamonds(amount, questType = 'general', difficulty = 'medium') {
        try {
            const response = await fetch('/api/update_diamonds/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    diamonds: amount,
                    quest_type: questType,
                    difficulty: difficulty
                })
            });

            const data = await response.json();

            if (data.success) {
                this.diamonds = data.new_balance;
                this.updateDiamondCounter();
                this.showDiamondAnimation(amount);
                return true;
            } else {
                return false;
            }
        } catch (error) {
            return false;
        }
    }

    updateDiamondCounter() {
        const diamondElement = document.getElementById('diamond-count');
        if (diamondElement) {
            diamondElement.textContent = this.diamonds;
            diamondElement.style.transform = 'scale(1.2)';
            setTimeout(() => {
                diamondElement.style.transform = 'scale(1)';
            }, 300);
        }
    }

    showDiamondAnimation(amount) {
        const animation = document.createElement('div');
        animation.className = 'diamond-animation';
        animation.innerHTML = `<i class="bi bi-gem"></i><span>+${amount}</span>`;
        animation.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(52, 152, 219, 0.9);
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 1.2rem;
            font-weight: bold;
            z-index: 10000;
            animation: diamondFloat 2s ease-out forwards;
        `;

        document.body.appendChild(animation);
        setTimeout(() => {
            if (document.body.contains(animation)) {
                document.body.removeChild(animation);
            }
        }, 2000);
    }

    updateCooldownDisplay() {
        if (this.userId === 'anonymous') return;

        const now = Date.now();
        const timeSinceLastQuest = now - this.lastQuestTime;
        const cooldownElement = document.getElementById('quest-cooldown');
        const questButton = document.getElementById('quest-button');

        if (timeSinceLastQuest < this.QUEST_COOLDOWN) {
            const remainingTime = Math.ceil((this.QUEST_COOLDOWN - timeSinceLastQuest) / 1000 / 60);
            cooldownElement.textContent = `Доступно через: ${remainingTime} мин`;
            questButton.disabled = true;
            questButton.style.opacity = '0.6';
        } else {
            cooldownElement.textContent = 'Готово к выполнению!';
            questButton.disabled = false;
            questButton.style.opacity = '1';
        }
    }

    setupEventListeners() {
        if (this.userId === 'anonymous') return;

        let selectedTopic = null;
        let selectedDifficulty = null;

        document.querySelectorAll('.topic-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.topic-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                selectedTopic = this.dataset.topic;
                window.questSystem.updateStartButton(selectedTopic, selectedDifficulty);
            });
        });

        document.querySelectorAll('.difficulty-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.difficulty-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                selectedDifficulty = this.dataset.difficulty;
                window.questSystem.updateStartButton(selectedTopic, selectedDifficulty);
            });
        });

        document.getElementById('start-quest').addEventListener('click', () => {
            if (selectedTopic && selectedDifficulty) {
                this.startQuest(selectedTopic, selectedDifficulty);
            }
        });

        document.getElementById('show-quest-marker').addEventListener('click', () => {
            if (this.questMarker && this.currentQuest) {
                map.setView(this.currentQuest.coordinates, 10);
                this.questMarker.openPopup();
            }
        });

        document.getElementById('questModal').addEventListener('hidden.bs.modal', () => {
            document.querySelectorAll('.topic-btn, .difficulty-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            selectedTopic = null;
            selectedDifficulty = null;
            this.updateStartButton(null, null);
        });

        document.getElementById('questModal').addEventListener('show.bs.modal', () => {
            this.loadUserData();
        });
    }

    updateStartButton(topic, difficulty) {
        const startBtn = document.getElementById('start-quest');
        startBtn.disabled = !(topic && difficulty);
    }

    startQuest(topic, difficulty) {
        if (this.userId === 'anonymous') {
            console.log('⚠️ Для выполнения заданий необходимо войти в аккаунт');
            return;
        }

        const now = Date.now();
        if (now - this.lastQuestTime < this.QUEST_COOLDOWN) {
            console.log('Задание еще не доступно. Подождите немного.');
            return;
        }

        const questionData = this.generateQuestion(topic, difficulty);
        this.currentQuest = { ...questionData, difficulty, topic };

        if (this.questMarker) {
            map.removeLayer(this.questMarker);
        }

        this.questMarker = L.marker(this.currentQuest.coordinates, {
            icon: L.divIcon({
                html: '<i class="bi bi-flag-fill" style="color: #dc3545; font-size: 20px; line-height: 35px; text-align: center;"></i>',
                iconSize: [35, 35],
                className: 'quest-marker-icon'
            })
        }).addTo(map);

        this.questPopup = L.popup({
            className: 'quest-popup-container',
            maxWidth: 400,
            closeOnEscapeKey: false,
            closeButton: true
        });

        this.updateQuestPopupContent();
        this.questMarker.bindPopup(this.questPopup).openPopup();

        // Убираем обработчик, который вызывает alert
        this.questPopup.off('remove');
        this.questPopup.on('remove', () => {
            if (this.currentQuest && !this.questPopup._isCompleted) {
                this.cancelQuestSilent();
            }
        });

        document.getElementById('show-quest-marker').style.display = 'block';
        map.setView(this.currentQuest.coordinates, 10);

        const questModal = bootstrap.Modal.getInstance(document.getElementById('questModal'));
        if (questModal) {
            questModal.hide();
        }
    }

    generateQuestion(topic, difficulty) {
        const questions = {
            'основания': [
                { question: "В каком году было первое упоминание Полоцка?", answer: "862", coordinates: [55.4856, 28.7686] },
                { question: "Какой город был основан в 980 году?", answer: "Туров", coordinates: [52.0678, 27.7333] },
                { question: "Когда основали Минск?", answer: "1067", coordinates: [53.9, 27.5] }
            ],
            'сражения': [
                { question: "В каком году произошла Грюнвальдская битва?", answer: "1410", coordinates: [53.4833, 20.1] },
                { question: "Когда была битва под Оршей?", answer: "1514", coordinates: [54.5, 30.4167] }
            ],
            'политика': [
                { question: "В каком году приняли первый Статут ВКЛ?", answer: "1529", coordinates: [53.9, 27.5] },
                { question: "Когда заключили Люблинскую унию?", answer: "1569", coordinates: [51.25, 22.5667] }
            ],
            'культура': [
                { question: "Когда создали БГУ?", answer: "1921", coordinates: [53.9, 27.5] },
                { question: "В каком году основали Национальную библиотеку?", answer: "1922", coordinates: [53.9, 27.5] }
            ]
        };

        const topicQuestions = questions[topic] || questions['основания'];
        return topicQuestions[Math.floor(Math.random() * topicQuestions.length)];
    }

    updateQuestPopupContent() {
        const popupContent = `
            <div class="quest-popup-content">
                <div class="quest-header">
                    <h5>🎯 Историческое задание</h5>
                    <div class="quest-meta">
                        <span class="badge bg-primary">${this.currentQuest.topic}</span>
                        <span class="badge difficulty-${this.currentQuest.difficulty}">${this.getDifficultyText(this.currentQuest.difficulty)}</span>
                    </div>
                </div>
                
                <div class="quest-info">
                    <div class="quest-info-item">
                        <strong>Сложность:</strong> ${this.getDifficultyText(this.currentQuest.difficulty)}
                    </div>
                    <div class="quest-info-item">
                        <strong>Цена:</strong> 
                        <span class="reward-amount">
                            <i class="bi bi-gem"></i> 
                            ${this.getRewardAmount(this.currentQuest.difficulty)} алмаз(ов)
                        </span>
                    </div>
                </div>
                
                <div class="quest-question">
                    <strong>Вопрос:</strong>
                    <p>${this.currentQuest.question}</p>
                </div>
                
                <div class="quest-answer-form">
                    <label class="form-label">Ваш ответ:</label>
                    <input type="text" class="quest-answer-input form-control" placeholder="Введите ответ..." autocomplete="off">
                    <div class="quest-buttons mt-2">
                        <button class="submit-quest-answer btn btn-success btn-sm">
                            <i class="bi bi-check-circle"></i> Проверить
                        </button>
                        <button class="cancel-quest btn btn-secondary btn-sm">
                            <i class="bi bi-x-circle"></i> Отмена
                        </button>
                    </div>
                </div>
            </div>
        `;

        this.questPopup.setContent(popupContent);

        setTimeout(() => {
            const popupElement = this.questPopup.getElement();
            if (popupElement) {
                const submitBtn = popupElement.querySelector('.submit-quest-answer');
                const cancelBtn = popupElement.querySelector('.cancel-quest');
                const answerInput = popupElement.querySelector('.quest-answer-input');

                if (submitBtn) submitBtn.onclick = (e) => { e.preventDefault(); this.checkQuestAnswer(); };
                if (cancelBtn) cancelBtn.onclick = (e) => { e.preventDefault(); this.cancelQuestSilent(); };
                if (answerInput) answerInput.onkeypress = (e) => { if (e.key === 'Enter') { e.preventDefault(); this.checkQuestAnswer(); } };
            }
        }, 50);
    }

    async checkQuestAnswer() {
        const popupElement = this.questPopup.getElement();
        if (!popupElement) return;

        const answerInput = popupElement.querySelector('.quest-answer-input');
        const userAnswer = answerInput ? answerInput.value.trim().toLowerCase() : '';
        const correctAnswer = this.currentQuest.answer.toLowerCase();

        if (!userAnswer) {
            console.log('⚠️ Введите ответ!');
            return;
        }

        if (userAnswer === correctAnswer) {
            const reward = this.getRewardAmount(this.currentQuest.difficulty);
            const success = await this.addDiamonds(reward, this.currentQuest.topic, this.currentQuest.difficulty);

            if (success) {
                this.questPopup._isCompleted = true;
                this.showQuestResult(true, reward);
                this.lastQuestTime = Date.now();
                localStorage.setItem(`lastQuestTime_${this.userId}`, this.lastQuestTime.toString());
                this.updateCooldownDisplay();
            } else {
                this.showQuestResult(false, 0, 'Ошибка при начислении алмазов');
            }
        } else {
            this.showQuestResult(false, 0, `Неправильно. Правильный ответ: ${this.currentQuest.answer}`);
        }
    }

    showQuestResult(success, reward = 0, message = '') {
        let content;

        if (success) {
            content = `
                <div class="quest-popup-content text-center">
                    <div class="text-success mb-3"><i class="bi bi-check-circle-fill" style="font-size: 3rem;"></i></div>
                    <h5>✅ Правильно!</h5>
                    <p>Вы получили <strong>${reward} алмаз(ов)</strong></p>
                    <button class="complete-quest-btn btn btn-success btn-sm">Закрыть</button>
                </div>
            `;
        } else {
            content = `
                <div class="quest-popup-content text-center">
                    <div class="text-danger mb-3"><i class="bi bi-x-circle-fill" style="font-size: 3rem;"></i></div>
                    <h5>❌ ${message || 'Неправильно!'}</h5>
                    ${!message ? `
                        <p>Попробуйте еще раз</p>
                        <button class="retry-quest-btn btn btn-secondary btn-sm">Попробовать снова</button>
                        <button class="cancel-quest-btn btn btn-outline-danger btn-sm mt-1">Отменить задание</button>
                    ` : `<button class="complete-quest-btn btn btn-secondary btn-sm">Закрыть</button>`}
                </div>
            `;
        }

        this.questPopup.setContent(content);

        setTimeout(() => {
            const popupElement = this.questPopup.getElement();
            if (popupElement) {
                const completeBtn = popupElement.querySelector('.complete-quest-btn');
                const retryBtn = popupElement.querySelector('.retry-quest-btn');
                const cancelBtn = popupElement.querySelector('.cancel-quest-btn');

                if (completeBtn) completeBtn.onclick = (e) => { e.preventDefault(); success ? this.completeQuest() : this.cancelQuestSilent(); };
                if (retryBtn) retryBtn.onclick = (e) => { e.preventDefault(); this.updateQuestPopupContent(); };
                if (cancelBtn) cancelBtn.onclick = (e) => { e.preventDefault(); this.cancelQuestSilent(); };
            }
        }, 50);
    }

    completeQuest() {
        this.cleanupQuest();
    }

    // ГЛАВНОЕ ИСПРАВЛЕНИЕ - полное удаление alert
    cancelQuestSilent() {
        this.lastQuestTime = Date.now();
        localStorage.setItem(`lastQuestTime_${this.userId}`, this.lastQuestTime.toString());
        this.updateCooldownDisplay();
        this.cleanupQuest();
        console.log('Задание отменено');
    }

    cleanupQuest() {
        if (this.questMarker) {
            map.removeLayer(this.questMarker);
            this.questMarker = null;
        }
        if (this.questPopup) {
            map.closePopup(this.questPopup);
            this.questPopup = null;
        }
        this.currentQuest = null;
        document.getElementById('show-quest-marker').style.display = 'none';
    }

    getDifficultyText(difficulty) {
        const texts = { 'easy': '🟢 Легкая', 'medium': '🟡 Средняя', 'hard': '🔴 Сложная' };
        return texts[difficulty];
    }

    getRewardAmount(difficulty) {
        const rewards = { 'easy': 1, 'medium': 3, 'hard': 5 };
        return rewards[difficulty];
    }

    getCsrfToken() {
        return document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
    }

    forceRefresh() {
        this.loadUserData();
        this.updateCooldownDisplay();
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    window.questSystem = new QuestSystem();
});