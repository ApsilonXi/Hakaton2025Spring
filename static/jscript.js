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
