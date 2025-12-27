// Менеджер тем для блога
// Проверяем, загружена ли страница логина/регистрации
if (document.querySelector('input[name="username"]') ||
    document.querySelector('input[name="password"]')) {
    console.log('Страница авторизации обнаружена, применяем тему');
}
class ThemeManager {
    constructor() {
        this.currentTheme = 'blog'; // По умолчанию
        this.init();
    }

    init() {
        // Создаём элемент для динамической загрузки тем
        this.themeLink = document.createElement('link');
        this.themeLink.rel = 'stylesheet';
        this.themeLink.id = 'active-theme';
        document.head.appendChild(this.themeLink);

        // Создаём элемент для favicon
        this.favicon = document.querySelector("link[rel='icon']");
        if (!this.favicon) {
            this.favicon = document.createElement('link');
            this.favicon.rel = 'icon';
            document.head.appendChild(this.favicon);
        }

        // Загружаем сохранённую тему
        this.loadSavedTheme();

        // Настраиваем переключатель
        this.setupSelector();
    }

    loadSavedTheme() {
        const saved = localStorage.getItem('blog-theme');
        if (saved) {
            this.setTheme(saved);
        }
    }

    setTheme(themeName) {
        // 1. Меняем CSS
        if (themeName === 'blog') {
            this.themeLink.href = '';
        } else {
            this.themeLink.href = `/static/css/themes/${themeName}.css`;
        }

        // 2. Меняем favicon
        this.favicon.href = `/static/images/icons/${themeName}.png`;

        // 3. Добавляем класс темы к body
        document.body.className = '';
        document.body.classList.add(`theme-${themeName}`);

        // 4. Сохраняем
        this.currentTheme = themeName;
        localStorage.setItem('blog-theme', themeName);

        // 5. Обновляем селектор
        const selector = document.getElementById('theme-selector');
        if (selector) {
            selector.value = themeName;
        }

        console.log(`Тема изменена: ${themeName}`);
    }

    setupSelector() {
        const selector = document.getElementById('theme-selector');
        if (selector) {
            // Устанавливаем текущую тему
            selector.value = this.currentTheme;

            // Вешаем обработчик
            selector.addEventListener('change', (e) => {
                this.setTheme(e.target.value);
            });
        } else {
            console.warn('Селектор тем не найден. Добавьте <select id="theme-selector">');
        }
    }
}

// Запускаем при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
});