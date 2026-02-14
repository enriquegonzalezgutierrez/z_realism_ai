/**
 * path: src/presentation/js/cookie-consent.js
 * description: Cookie Consent Manager v1.0 - Commercial Product.
 * 
 * ABSTRACT:
 * Manages user consent for essential session cookies. 
 * This script injects the "Cookie Consent" modal, explaining the 
 * technical necessity of session tokens for asynchronous task tracking.
 * 
 * ARCHITECTURAL ROLE (Presentation Layer):
 * Acts as a Compliance & State Manager. It ensures the user is 
 * informed of the local caching logic used to maintain task continuity 
 * during high-latency AI inference.
 * 
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. PROTOCOL CONFIGURATION
    const CACHE_STORAGE_KEY = 'z_realism_cookie_consent_accepted';

    /**
     * Injects the Cookie Consent modal into the DOM.
     * @returns {HTMLElement} The created modal element.
     */
    const injectProtocolModal = () => {
        const modalHTML = `
            <div id="cookie-modal" class="cookie-modal">
                <div class="cookie-content">
                    <span class="cookie-icon">🍪</span>
                    <div class="cookie-text">
                        <h4>ESSENTIAL COOKIES (SESSION DATA)</h4>
                        <p>
                            This platform utilizes essential session cookies to manage 
                            your active tasks and track unique Production IDs. These are 
                            strictly necessary for service functionality and do not 
                            collect personal data. Review our 
                            <a href="legal.html#cookies">Privacy Policy</a>.
                        </p>
                    </div>
                </div>
                <div class="cookie-actions">
                    <button id="accept-cookies" class="btn btn-primary">ACCEPT</button>
                    <a href="legal.html" class="btn btn-secondary">REVIEW POLICY</a>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        return document.getElementById('cookie-modal');
    };

    /**
     * Transitions the modal into the visible viewport.
     * @param {HTMLElement} modalElement 
     */
    const activateModal = (modalElement) => {
        setTimeout(() => {
            modalElement.classList.add('active');
        }, 800); 
    };

    /**
     * Transitions the modal out of the viewport.
     * @param {HTMLElement} modalElement 
     */
    const decommissionModal = (modalElement) => {
        modalElement.classList.remove('active');
        setTimeout(() => {
            modalElement.style.display = 'none'; 
        }, 700);
    };

    // --- MAIN EXECUTION LOGIC ---
    const isProtocolAccepted = localStorage.getItem(CACHE_STORAGE_KEY);

    if (!isProtocolAccepted) {
        const modal = injectProtocolModal();
        activateModal(modal);

        document.getElementById('accept-cookies').addEventListener('click', () => {
            localStorage.setItem(CACHE_STORAGE_KEY, 'true');
            decommissionModal(modal);
            console.log("COOKIE_CONSENT: Essential cookie usage accepted.");
        });
    }
});