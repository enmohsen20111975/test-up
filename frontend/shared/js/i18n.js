const i18n = {
    translations: {},
    currentLang: 'ar', // Default language
    supportedLangs: ['ar', 'en', 'fr'],

    async loadTranslations(lang) {
        try {
            const response = await fetch(`./shared/js/i18n/${lang}.json`);
            if (!response.ok) {
                throw new Error(`Failed to load translations for ${lang}`);
            }
            this.translations = await response.json();
            this.currentLang = lang;
            this.applyTranslations();
        } catch (error) {
            console.error("Error loading translations:", error);
            // Fallback to default language if loading fails
            if (lang !== 'ar') {
                await this.loadTranslations('ar');
            }
        }
    },

    applyTranslations() {
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (this.translations[key]) {
                element.textContent = this.translations[key];
            }
        });

        document.querySelectorAll('[data-i18n-html]').forEach(element => {
            const key = element.getAttribute('data-i18n-html');
            if (this.translations[key]) {
                element.innerHTML = this.translations[key];
            }
        });

        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            if (this.translations[key]) {
                element.setAttribute('placeholder', this.translations[key]);
            }
        });

        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            if (this.translations[key]) {
                element.setAttribute('title', this.translations[key]);
            }
        });

        document.querySelectorAll('[data-i18n-aria-label]').forEach(element => {
            const key = element.getAttribute('data-i18n-aria-label');
            if (this.translations[key]) {
                element.setAttribute('aria-label', this.translations[key]);
            }
        });

        document.querySelectorAll('[data-i18n-value]').forEach(element => {
            const key = element.getAttribute('data-i18n-value');
            if (this.translations[key]) {
                element.setAttribute('value', this.translations[key]);
            }
        });

        document.querySelectorAll('meta[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (this.translations[key]) {
                element.setAttribute('content', this.translations[key]);
            }
        });

        this.updateDocumentLangDir();
        this.updateLanguageSelectors();

        document.dispatchEvent(new CustomEvent('i18n:changed', {
            detail: { lang: this.currentLang }
        }));
    },

    getTranslation(key) {
        return this.translations[key] || key;
    },

    setLanguage(lang) {
        localStorage.setItem('lang', lang);
        this.loadTranslations(lang);
    },

    updateDocumentLangDir() {
        const isRtl = this.currentLang === 'ar';
        document.documentElement.setAttribute('lang', this.currentLang);
        document.documentElement.setAttribute('dir', isRtl ? 'rtl' : 'ltr');
    },

    updateLanguageSelectors() {
        const selectors = document.querySelectorAll('[data-i18n-lang], #language-select');
        selectors.forEach(select => {
            if (select.value !== this.currentLang) {
                select.value = this.currentLang;
            }
        });
    },

    init() {
        const savedLang = localStorage.getItem('lang');
        const browserLang = navigator.language.split('-')[0];
        const initialLang = savedLang || (this.supportedLangs.includes(browserLang) ? browserLang : 'ar');
        this.loadTranslations(initialLang);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    i18n.init();
});
