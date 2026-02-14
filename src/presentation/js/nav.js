/**
 * path: src/presentation/js/nav.js
 * description: Global Navigation Injector v23.1 - Responsive Multi-language Flag Edition.
 * 
 * ABSTRACT:
 * Orchestrates the shared navigation manifold across the Z-Realism production ecosystem.
 * This version implements a decoupled i18n-aware controller that manages the
 * responsive mobile drawer and a high-fidelity visual language selection interface.
 * 
 * ARCHITECTURAL ROLE (Presentation Layer):
 * Acts as a Shared Component Injector. It centralizes the navigation structure,
 * active-state detection, and mobile interaction logic for a streamlined global UX.
 * 
 * author: Enrique González Gutiérrez <enrique.gonzalez.gutierrez@gmail.com>
 */

const injectNav = () => {
    // 1. URI PATH ANALYSIS
    // Extract the current location to highlight the active production node.
    const currentPath = window.location.pathname;
    const isActive = (filename) => currentPath.includes(filename) ? 'active' : '';

    // 2. LANGUAGE SELECTOR MANIFOLD (Visual Flag Buttons)
    // Generates the 🇺🇸 | 🇪🇸 toggle with active state detection and grayscale filters.
    const langToggle = `
        <div class="lang-selector">
            <button onclick="i18n.setLanguage('en')" 
                    class="flag-btn ${i18n.currentLang === 'en' ? 'active' : ''}" 
                    title="English"
                    aria-label="Switch to English">
                🇺🇸
            </button>
            <button onclick="i18n.setLanguage('es')" 
                    class="flag-btn ${i18n.currentLang === 'es' ? 'active' : ''}" 
                    title="Español"
                    aria-label="Cambiar a Español">
                🇪🇸
            </button>
        </div>
    `;

    // 3. COMPONENT CONSTRUCTION
    // Dynamically resolves localized labels via the i18n.translate() method.
    const navHTML = `
    <nav class="main-nav">
        <!-- Brand Identity -->
        <a href="index.html" class="nav-logo">
            <span>🐉</span> Z-REALISM
        </a>

        <!-- Interactive Mobile Toggle (Hamburger) -->
        <button class="menu-toggle" id="nav-toggle" aria-label="Toggle menu">
            <span></span>
            <span></span>
            <span></span>
        </button>
        
        <!-- Navigation Nodes & Language Selection -->
        <div class="nav-links" id="nav-menu">
            <a href="image-lab.html" class="nav-item ${isActive('image-lab')}" data-i18n="nav_image">
                ${i18n.translate('nav_image')}
            </a>
            <a href="video-lab.html" class="nav-item ${isActive('video-lab')}" data-i18n="nav_video">
                ${i18n.translate('nav_video')}
            </a>
            <a href="about.html" class="nav-item ${isActive('about')}" data-i18n="nav_about">
                ${i18n.translate('nav_about')}
            </a>
            <a href="architecture.html" class="nav-item ${isActive('architecture')}" data-i18n="nav_tech">
                ${i18n.translate('nav_tech')}
            </a>
            <a href="contact.html" class="nav-item ${isActive('contact')}" data-i18n="nav_contact">
                ${i18n.translate('nav_contact')}
            </a>
            <a href="legal.html" class="nav-item ${isActive('legal')}" data-i18n="nav_legal">
                ${i18n.translate('nav_legal')}
            </a>
            
            <!-- Injected Flag Toggles -->
            ${langToggle}
        </div>
    </nav>
    `;

    // 4. INJECTION & CLEANUP PROTOCOL
    // Sanitizes the top of the body to prevent duplicate navigation manifolds.
    const existingNav = document.querySelector('.main-nav');
    if (existingNav) existingNav.remove();
    document.body.insertAdjacentHTML('afterbegin', navHTML);

    // 5. RESPONSIVE INTERACTION LOGIC
    // Manages the lifecycle of the mobile navigation drawer.
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');

    if (navToggle && navMenu) {
        navToggle.onclick = () => {
            // Synchronize the 'X' animation with drawer visibility
            const isOpened = navToggle.classList.toggle('active');
            navMenu.classList.toggle('active');
            
            // Interaction telemetry
            console.log(`NAV_INTERACT: Mobile drawer ${isOpened ? 'Opened' : 'Closed'}`);
        };

        // Auto-closure on navigation
        navMenu.querySelectorAll('.nav-item').forEach(link => {
            link.onclick = () => {
                navToggle.classList.remove('active');
                navMenu.classList.remove('active');
            };
        });
    }

    console.log(`NAV_SYNC: Production manifold [${i18n.currentLang.toUpperCase()}] injected.`);
};

// --- SYSTEM SUBSCRIPTION ---
// Ensures the navigation renders only when the i18n manifest is fully resolved.
if (i18n.isReady) {
    injectNav();
} else {
    window.addEventListener('i18nReady', injectNav);
}

// Reactive re-render on language manifold switch
window.addEventListener('langChanged', injectNav);