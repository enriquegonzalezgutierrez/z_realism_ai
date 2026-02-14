/**
 * path: src/presentation/js/i18n-engine.js
 * description: High-Fidelity Translation Engine v2.0 - SOLID/DDD Edition.
 * 
 * ABSTRACT:
 * Orchestrates the internationalization (i18n) lifecycle. This engine 
 * asynchronously loads decoupled translation manifolds (JSON) and 
 * synchronizes the UI state.
 * 
 * SOLID PRINCIPLES APPLIED:
 * 1. SRP: Manages only the state and application of translations.
 * 2. OCP: New languages can be added by creating JSON files without modifying this engine.
 * 3. DIP: Depends on abstract JSON structures, not concrete dictionaries.
 * 
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

class I18nEngine {
    constructor() {
        this.currentLang = localStorage.getItem('z_realism_lang') || 'en';
        this.dictionary = {};
        this.isReady = false;
        
        // Initialize the engine boot sequence
        this.boot();
    }

    /**
     * Infrastructure Bootstrapper.
     * Loads the initial language manifold from the filesystem.
     */
    async boot() {
        await this.loadManifest(this.currentLang);
        this.isReady = true;
        
        // Signal the system that the translation layer is active
        window.dispatchEvent(new CustomEvent('i18nReady'));
        this.translateDOM();
    }

    /**
     * Data Ingestion Logic (Infrastructure Port).
     * Fetches decoupled JSON manifolds.
     * @param {string} lang 
     */
    async loadManifest(lang) {
        try {
            // Using fetch to decouple the data from the script logic (DIP)
            const response = await fetch(`i18n/${lang}.json`);
            if (!response.ok) throw new Error(`I18N_ERROR: Manifest [${lang}] not found.`);
            
            this.dictionary = await response.json();
            this.currentLang = lang;
            localStorage.setItem('z_realism_lang', lang);
            document.documentElement.lang = lang;
            
            console.log(`I18N_ENGINE: Manifold [${lang.toUpperCase()}] successfully injected.`);
        } catch (error) {
            console.error(error);
            // Fallback strategy could be implemented here
        }
    }

    /**
     * Production Pipeline: Language Switcher.
     * @param {string} lang 
     */
    async setLanguage(lang) {
        if (this.currentLang === lang) return;
        
        await this.loadManifest(lang);
        this.translateDOM();
        
        // Notify UI Controllers (Nav, Lab, etc.) to re-render dynamic components
        window.dispatchEvent(new CustomEvent('langChanged', { detail: lang }));
    }

    /**
     * Recursive DOM Projection.
     * Scans for data-i18n attributes and applies the dictionary.
     */
    translateDOM() {
        const elements = document.querySelectorAll('[data-i18n]');
        elements.forEach(el => {
            const key = el.getAttribute('data-i18n');
            const translation = this.dictionary[key];
            
            if (translation) {
                // Strategic check for input elements (placeholders) vs standard tags
                if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                    el.placeholder = translation;
                } else {
                    el.innerHTML = translation;
                }
            }
        });
    }

    /**
     * Direct Access Port for Dynamic Content.
     * @param {string} key 
     * @returns {string}
     */
    translate(key) {
        return this.dictionary[key] || key;
    }
}

// Global Singleton Instance to maintain state across the ecosystem
const i18n = new I18nEngine();