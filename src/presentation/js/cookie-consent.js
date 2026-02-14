/**
 * path: src/presentation/js/cookie-consent.js
 * description: Cookie Consent Manager v1.2 - Multi-language Production.
 * 
 * ABSTRACT:
 * Manages user consent for essential session cookies within the Z-Realism 
 * production ecosystem. This version is i18n-aware, allowing the consent 
 * interface to switch languages dynamically based on the active manifold.
 * 
 * ARCHITECTURAL ROLE (Presentation Layer):
 * Acts as a Compliance & State Manager. It ensures the user is informed 
 * of the technical necessity of session tokens for task continuity.
 * 
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

const initCookieConsent = () => {
    const CACHE_STORAGE_KEY = 'z_realism_cookie_consent_accepted';

    /**
     * Injects the localized Cookie Consent modal into the DOM.
     * @returns {HTMLElement} The created modal element.
     */
    const injectProtocolModal = () => {
        const modalHTML = `
            <div id="cookie-modal" class="cookie-modal">
                <div class="cookie-content">
                    <span class="cookie-icon">🍪</span>
                    <div class="cookie-text">
                        <h4 data-i18n="cookie_title">${i18n.translate('cookie_title')}</h4>
                        <p>
                            <span data-i18n="cookie_text">${i18n.translate('cookie_text')}</span>
                            <a href="legal.html#privacy" data-i18n="nav_legal">${i18n.translate('nav_legal')}</a>.
                        </p>
                    </div>
                </div>
                <div class="cookie-actions">
                    <button id="accept-cookies" class="btn btn-primary" data-i18n="cookie_accept">
                        ${i18n.translate('cookie_accept')}
                    </button>
                    <a href="legal.html#privacy" class="btn btn-secondary" data-i18n="cookie_policy">
                        ${i18n.translate('cookie_policy')}
                    </a>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        return document.getElementById('cookie-modal');
    };

    /**
     * Transitions the modal into the visible viewport.
     */
    const activateModal = (modalElement) => {
        setTimeout(() => {
            modalElement.classList.add('active');
        }, 1200); 
    };

    /**
     * Transitions the modal out of the viewport and cleans up.
     */
    const decommissionModal = (modalElement) => {
        modalElement.classList.remove('active');
        setTimeout(() => {
            modalElement.style.display = 'none'; 
            modalElement.remove();
        }, 700); 
    };

    // --- EXECUTION LOGIC ---
    const isAccepted = localStorage.getItem(CACHE_STORAGE_KEY);

    if (!isAccepted) {
        const modal = injectProtocolModal();
        activateModal(modal);

        // Binding: Consent Acceptance Handler
        document.getElementById('accept-cookies').addEventListener('click', () => {
            localStorage.setItem(CACHE_STORAGE_KEY, 'true');
            decommissionModal(modal);
            console.log("COOKIE_CONSENT: Manifold persistence authorized by user.");
        });
    }
};

// --- SUBSCRIPTION INTERFACES ---
// Ensure the component only runs when the translation manifold is loaded.
if (i18n.isReady) {
    initCookieConsent();
} else {
    window.addEventListener('i18nReady', initCookieConsent);
}