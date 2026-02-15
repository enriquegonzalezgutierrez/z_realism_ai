/**
 * path: src/presentation/js/i18n-engine.js
 * description: High-Fidelity Translation Engine v2.1 - SOLID/DDD Edition.
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
 * MODIFICATION LOG v2.1:
 * Implemented a DOMReady guard within the boot sequence. This prevents 
 * race conditions during hard refreshes (CTRL+F5) where the translation 
 * logic might execute before the DOM tree is fully parsed.
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
     * Loads the initial language manifold and ensures DOM readiness.
     */
    async boot() {
        // Load the manifest data first
        await this.loadManifest(this.currentLang);
        
        // Guard: Wait for DOM to be fully parsed to prevent translation failure on hard refresh
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeUI());
        } else {
            this.initializeUI();
        }
    }

    /**
     * Finalizes UI synchronization once data and DOM are ready.
     */
    initializeUI() {
        this.translateDOM();
        this.isReady = true;
        
        // Signal the system that the translation layer is active and ready for dependent scripts
        window.dispatchEvent(new CustomEvent('i18nReady'));
        console.log(`I18N_ENGINE: Manifold [${this.currentLang.toUpperCase()}] synchronized with DOM.`);
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
        } catch (error) {
            console.error(error);
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