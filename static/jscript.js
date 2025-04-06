function updateScrollIndicator(containerId, indicatorId) {
    const container = document.getElementById(containerId);
    const indicator = document.getElementById(indicatorId);
    const dots = indicator.querySelectorAll('.scroll-dot');
    
    if (!container || !indicator) return;
    
    container.addEventListener('scroll', () => {
        const scrollPosition = container.scrollLeft;
        const cardWidth = container.querySelector('a').offsetWidth;
        const activeIndex = Math.round(scrollPosition / cardWidth);
        
        dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === activeIndex);
        });
    });
}

// Инициализация для обоих контейнеров
document.addEventListener('DOMContentLoaded', () => {
    updateScrollIndicator('adminCards', 'adminScrollIndicator');
    updateScrollIndicator('savedCards', 'savedScrollIndicator');
    setupTabSwitching(); // Добавляем инициализацию переключения вкладок
    
    // Если текущий пользователь - админ, загружаем предложенные новости
    if (document.querySelector('.news-requests-button')) {
        document.querySelector('.news-requests-button').addEventListener('click', async () => {
            await loadProposedNews();
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    // Получаем элементы
    const sortDropdownItems = document.querySelectorAll('[data-sort]');
    const sortButton = document.querySelector('.sort-menu');
    const newsContainer = document.getElementById('newsContainer');
    const newsCards = Array.from(document.querySelectorAll('.news-card'));
    
    // Функция для сортировки новостей
    function sortNews(sortType) {
        // Создаем копию массива карточек для сортировки
        const sortedCards = [...newsCards];
        
        // Сортируем в зависимости от выбранного типа
        sortedCards.sort((a, b) => {
            const dateA = new Date(a.getAttribute('data-date'));
            const dateB = new Date(b.getAttribute('data-date'));
            
            if (sortType === 'date-asc') {
                return dateA - dateB; // Сначала старые
            } else {
                return dateB - dateA; // Сначала новые
            }
        });
        
        // Очищаем контейнер
        while (newsContainer.firstChild) {
            if (newsContainer.firstChild.classList && 
                newsContainer.firstChild.classList.contains('news-card')) {
                newsContainer.removeChild(newsContainer.firstChild);
            } else {
                break; // Оставляем поиск и другие элементы
            }
        }
        
        // Вставляем отсортированные карточки после поиска
        const searchElement = document.querySelector('.search');
        sortedCards.forEach(card => {
            newsContainer.insertBefore(card, searchElement.nextSibling);
        });
    }
    
    // Обработчики для выбора сортировки
    sortDropdownItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const sortType = this.getAttribute('data-sort');
            
            // Меняем текст кнопки
            if (sortType === 'date-asc') {
                sortButton.textContent = 'По дате (↑)';
            } else if (sortType === 'date-desc') {
                sortButton.textContent = 'По дате (↓)';
            }
            
            // Сортируем новости
            sortNews(sortType);
        });
    });
    
    // Изначальная сортировка (по умолчанию - сначала новые)
    sortNews('date-desc');
    sortButton.textContent = 'По дате (↓)';
});

document.getElementById('newsSearch').addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase();
    const newsCards = document.querySelectorAll('.news-card');
    
    newsCards.forEach(card => {
        const title = card.querySelector('.title').textContent.toLowerCase();
        const content = card.querySelector('.news-text').textContent.toLowerCase();
        
        if (title.includes(searchTerm) || content.includes(searchTerm)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
});

// Добавим в конец файла jscript.js

// Функция для переключения между вкладками
function setupTabSwitching() {
    const tabs = {
        allNews: document.querySelector('.all-news-button'),
        following: document.querySelector('.following-button'),
        proposedNews: document.querySelector('.news-requests-button')
    };
    
    const containers = {
        allNews: document.getElementById('newsContainer'),
        proposedNews: document.getElementById('proposedNews')
    };

    // Обработчики для кнопок навигации
    tabs.allNews.addEventListener('click', () => {
        containers.allNews.style.display = 'block';
        containers.proposedNews.style.display = 'none';
        tabs.allNews.classList.add('active');
        tabs.following.classList.remove('active');
        tabs.proposedNews.classList.remove('active');
    });

    tabs.following.addEventListener('click', () => {
        // Логика для подписок (если нужно)
        containers.allNews.style.display = 'block';
        containers.proposedNews.style.display = 'none';
        tabs.allNews.classList.remove('active');
        tabs.following.classList.add('active');
        tabs.proposedNews.classList.remove('active');
    });

    tabs.proposedNews.addEventListener('click', async () => {
        containers.allNews.style.display = 'none';
        containers.proposedNews.style.display = 'block';
        tabs.allNews.classList.remove('active');
        tabs.following.classList.remove('active');
        tabs.proposedNews.classList.add('active');
        
        // Загружаем предложенные новости
        await loadProposedNews();
    });
}

// Функция загрузки предложенных новостей
async function loadProposedNews() {
    const container = document.getElementById('proposedCards');
    if (!container) return;
    
    try {
        container.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Загрузка...</span></div></div>';
        
        const response = await fetch('/api/offers');
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.error || `Ошибка сервера: ${response.status}`);
        }
        
        const offers = await response.json();
        
        if (!offers || offers.length === 0) {
            container.innerHTML = '<p class="text-center py-3">Нет предложенных новостей</p>';
            return;
        }
        
        container.innerHTML = '';
        offers.forEach(offer => {
            const card = document.createElement('div');
            card.className = 'proposed-card mb-3 p-3 border rounded';
            
            const isSource = offer.link.startsWith('source_suggestion:');
            const content = isSource ? offer.link.replace('source_suggestion:', '') : offer.link;
            
            card.innerHTML = `
                <h4>${isSource ? 'Предложен новый источник' : 'Новость на модерации'}</h4>
                <p><small class="text-muted">От: ${offer.user_login || 'пользователь #'+offer.user_id}</small></p>
                <p>${isSource ? 'Ссылка:' : 'ID новости:'} <a href="${isSource ? content : '#'}" target="_blank">${content}</a></p>
                <div class="d-flex gap-2 mt-2">
                    <button class="btn btn-sm btn-success approve-btn" data-id="${offer.id}">Одобрить</button>
                    <button class="btn btn-sm btn-danger reject-btn" data-id="${offer.id}">Отклонить</button>
                </div>
            `;
            container.appendChild(card);
        });
        
        // Добавляем обработчики для кнопок
        document.querySelectorAll('.approve-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                await processOffer(e.target.dataset.id, 'approve');
            });
        });
        
        document.querySelectorAll('.reject-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                await processOffer(e.target.dataset.id, 'reject');
            });
        });
        
    } catch (error) {
        console.error('Ошибка загрузки предложенных новостей:', error);
        container.innerHTML = `
            <div class="alert alert-danger">
                ${error.message}
                <button class="btn btn-sm btn-secondary mt-2" onclick="loadProposedNews()">Попробовать снова</button>
            </div>
        `;
    }
}

// Функция обработки предложения (одобрить/отклонить)
async function processOffer(offerId, action) {
    try {
        const response = await fetch(`/api/offers/${offerId}/${action}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            // Обновляем список после действия
            await loadProposedNews();
        } else {
            alert('Произошла ошибка при обработке предложения');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при обработке предложения');
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    setupTabSwitching();
    // Остальная инициализация...
});

// Заменяем существующий обработчик на:
tabs.following.addEventListener('click', async () => {
    try {
        const response = await fetch('/following');
        if (!response.ok) throw new Error('Ошибка загрузки');
        
        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        // Обновляем контейнер с новостями
        containers.allNews.innerHTML = doc.getElementById('newsContainer').innerHTML;
        
        // Обновляем популярные теги
        const popularTags = doc.querySelector('.popular-tags');
        if (popularTags) {
            document.querySelector('.popular-tags').innerHTML = popularTags.innerHTML;
        }
        
        // Обновляем активные кнопки
        tabs.allNews.classList.remove('active');
        tabs.following.classList.add('active');
        tabs.proposedNews.classList.remove('active');
        
    } catch (error) {
        console.error('Ошибка загрузки подписок:', error);
        alert('Не удалось загрузить новости по подпискам');
    }
});