/**
 * path: src/presentation/js/cookie-consent.js
 * description: Neural Cache Protocol Orchestrator v21.1 - Thesis Candidate.
 * 
 * ABSTRACT:
 * Manages the data sovereignty and session persistence protocols. 
 * This script injects the "Neural Cache" consent modal, explaining the 
 * engineering necessity of session tokens for asynchronous task tracking.
 * 
 * ARCHITECTURAL ROLE (Presentation Layer):
 * Acts as a Compliance & State Manager. It ensures the researcher is 
 * informed of the local caching logic used to maintain task continuity 
 * during long-latency CUDA inference.
 * 
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. PROTOCOL CONFIGURATION
    const CACHE_STORAGE_KEY = 'z_realism_neural_cache_accepted';

    /**
     * Injects the Neural Cache Protocol modal into the DOM.
     * @returns {HTMLElement} The created modal element.
     */
    const injectProtocolModal = () => {
        const modalHTML = `
            <div id="cookie-modal" class="cookie-modal">
                <div class="cookie-content">
                    <span class="cookie-icon">🧬</span>
                    <div class="cookie-text">
                        <h4>NEURAL CACHE PROTOCOL (SESSION DATA)</h4>
                        <p>
                            This research platform utilizes essential "Neural Cache" tokens 
                            (session cookies) to orchestrate Task UUIDs. This is required 
                             to maintain operational continuity during asynchronous CUDA 
                            inference. No personal metadata is harvested. Review the 
                            <a href="legal.html#cookies">Data Sovereignty Policy</a>.
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
     * Transitions the modal into the visible viewport.
     * @param {HTMLElement} modalElement 
     */
    const activateModal = (modalElement) => {
        // Small delay to prevent layout thrashing during laboratory boot
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
        }, 700); // Sync with CSS transition duration
    };

    // --- MAIN EXECUTION LOGIC ---
    // Check if the protocol has already been accepted in this client manifold
    const isProtocolAccepted = localStorage.getItem(CACHE_STORAGE_KEY);

    if (!isProtocolAccepted) {
        const modal = injectProtocolModal();
        activateModal(modal);

        // Binding: Protocol Acceptance Handler
        document.getElementById('accept-cookies').addEventListener('click', () => {
            localStorage.setItem(CACHE_STORAGE_KEY, 'true');
            decommissionModal(modal);
            console.log("CACHE_PROTOCOL: Metadata caching authorized by researcher.");
        });
    }
});