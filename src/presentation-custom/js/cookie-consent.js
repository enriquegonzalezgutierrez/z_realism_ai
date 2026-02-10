/**
 * path: src/presentation-custom/js/cookie-consent.js
 * description: Neural Cache Protocol Orchestrator v20.9.
 * 
 * ABSTRACT:
 * Manages the display and user interaction for the cookie (Neural Cache) consent modal.
 * This script dynamically injects the modal into the DOM and uses localStorage
 * to remember user preferences, ensuring it only appears once per user.
 * 
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

document.addEventListener('DOMContentLoaded', () => {
    const COOKIE_STORAGE_KEY = 'z_realism_neural_cache_accepted';

    /**
     * Injects the HTML structure of the cookie modal into the body.
     * @returns {HTMLElement} The created modal element.
     */
    const injectCookieModal = () => {
        const modalHTML = `
            <div id="cookie-modal" class="cookie-modal">
                <div class="cookie-content">
                    <span class="cookie-icon">🍪</span>
                    <div class="cookie-text">
                        <h4>NEURAL CACHE PROTOCOL (COOKIES)</h4>
                        <p>
                            This research platform uses essential "Neural Cache" tokens (session cookies) 
                            to track task IDs and ensure operational continuity during long-latency inference. 
                            No personal data is collected or transmitted. 
                            Review our <a href="legal.html#cookies">Neural Cache Policy</a> for details.
                        </p>
                    </div>
                </div>
                <div class="cookie-actions">
                    <button id="accept-cookies" class="btn btn-primary">ACCEPT PROTOCOL</button>
                    <a href="legal.html" class="btn btn-secondary">REVIEW POLICY</a>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        return document.getElementById('cookie-modal');
    };

    /**
     * Displays the cookie modal with an animation.
     * @param {HTMLElement} modalElement - The modal DOM element.
     */
    const showCookieModal = (modalElement) => {
        setTimeout(() => {
            modalElement.classList.add('active');
        }, 500); // Small delay for better UX
    };

    /**
     * Hides the cookie modal with an animation.
     * @param {HTMLElement} modalElement - The modal DOM element.
     */
    const hideCookieModal = (modalElement) => {
        modalElement.classList.remove('active');
        setTimeout(() => {
            modalElement.style.display = 'none'; // Completely remove after transition
        }, 700); // Match CSS transition duration
    };

    // --- MAIN EXECUTION LOGIC ---
    const hasAcceptedCookies = localStorage.getItem(COOKIE_STORAGE_KEY);

    if (!hasAcceptedCookies) {
        const modal = injectCookieModal();
        showCookieModal(modal);

        // Event listener for the "Accept Protocol" button
        document.getElementById('accept-cookies').addEventListener('click', () => {
            localStorage.setItem(COOKIE_STORAGE_KEY, 'true');
            hideCookieModal(modal);
        });
    }
});